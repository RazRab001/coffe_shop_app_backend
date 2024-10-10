import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
from src.main import app

from src.item.schema import ItemFields, AddingIngredient, GettingIngredientValueForItem
from src.item.service import create_item, get_all_active_items, update_item, delete_item, get_item_by_id, add_ingredient, get_item_ids_by_product
from src.item.model import metadata
from src.product.service import create_new_product
from src.product.schema import CreationProduct

# Используем SQLite в памяти для тестирования
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

Base = declarative_base()


@pytest.fixture(scope="module")
async def db():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession)

    # Создание всех таблиц
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield async_session

    # Удаление всех таблиц после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_item(db: AsyncSession):
    async with db() as session:
        data = ItemFields(title="Test Item", description="Test Description", ingredients=[])
        created_item = await create_item(data, session)

        assert created_item.title == "Test Item"
        assert created_item.description == "Test Description"
        assert created_item.ingredients == []
        assert created_item.cost == 0.0


@pytest.mark.asyncio
async def test_get_all_active_items(db: AsyncSession):
    async with db() as session:
        # Создаем активный item для тестирования
        item_data = ItemFields(title="Active Item", description="Active Description", ingredients=[])
        await create_item(item_data, session)

        active_items = await get_all_active_items(session)

        assert len(active_items) > 0
        assert all(item.title == "Active Item" for item in active_items)


@pytest.mark.asyncio
async def test_update_item(db: AsyncSession):
    async with db() as session:
        # Создаем item для обновления
        item_data = ItemFields(title="Old Item", description="Old Description", ingredients=[])
        created_item = await create_item(item_data, session)

        updated_data = ItemFields(title="Updated Item", description="Updated Description", ingredients=[])
        updated_item = await update_item(created_item.id, updated_data, session)

        assert updated_item.title == "Updated Item"
        assert updated_item.description == "Updated Description"


@pytest.mark.asyncio
async def test_delete_item(db: AsyncSession):
    async with db() as session:
        # Создаем item для удаления
        item_data = ItemFields(title="Item to Delete", description="Delete Me", ingredients=[])
        created_item = await create_item(item_data, session)

        await delete_item(created_item.id, session)

        with pytest.raises(ValueError):
            await get_item_by_id(created_item.id, session)  # Проверяем, что элемент был удален


@pytest.mark.asyncio
async def test_create_item_with_invalid_data(db: AsyncSession):
    async with db() as session:
        invalid_data = ItemFields(title=None, description=None, ingredients=None)  # обязательные поля пустые

        with pytest.raises(IntegrityError):
            await create_item(invalid_data, session)


@pytest.mark.asyncio
async def test_add_ingredient_with_nonexistent_product(db: AsyncSession):
    async with db() as session:
        # Создаем item без ингредиентов
        item_data = ItemFields(title="Test Item", description="Item Description", ingredients=[])
        created_item = await create_item(item_data, session)

        # Пытаемся добавить ингредиент с несуществующим product_id
        nonexistent_product = AddingIngredient(product_id=9999, value=10)  # product_id не существует

        with pytest.raises(Exception):
            await add_ingredient(nonexistent_product, created_item.id, session)


@pytest.mark.asyncio
async def test_update_item_with_nonexistent_id(db: AsyncSession):
    async with db() as session:
        item_id = 9999  # несуществующий item_id
        data = ItemFields(title="Updated Title", description="Updated Description")

        with pytest.raises(ValueError):
            await update_item(item_id, data, session)


@pytest.mark.asyncio
async def test_delete_nonexistent_item(db: AsyncSession):
    async with db() as session:
        item_id = 9999  # несуществующий item_id

        with pytest.raises(ValueError):
            await delete_item(item_id, session)


@pytest.mark.asyncio
async def test_get_item_ids_by_product_with_nonexistent_product(db: AsyncSession):
    async with db() as session:
        product_id = 9999  # несуществующий product_id

        item_ids = await get_item_ids_by_product(product_id, session)
        assert item_ids == []  # Ожидаем пустой список


@pytest.mark.asyncio
async def test_get_item_by_id_with_nonexistent_id(db: AsyncSession):
    async with db() as session:
        item_id = 9999  # несуществующий item_id

        with pytest.raises(ValueError):
            await get_item_by_id(item_id, session)


# Новый тест с добавлением ингредиента

@pytest.mark.asyncio
async def test_create_item_with_ingredient(db: AsyncSession):
    async with db() as session:
        # Сначала создаем продукт
        product_data = CreationProduct(title="Test Product", value_type="kilogram")
        created_product = await create_new_product(product_data, session)

        # Затем создаем item с этим ингредиентом
        ingredient = AddingIngredient(product_id=created_product.id, value=5.0)
        item_data = ItemFields(title="Item with Ingredient", description="Item description", ingredients=[ingredient])

        created_item = await create_item(item_data, session)

        assert created_item.title == "Item with Ingredient"
        assert len(created_item.ingredients) == 1
        assert created_item.ingredients[0].product_id == created_product.id
        assert created_item.ingredients[0].value == 5.0


@pytest.mark.asyncio
async def test_update_item_with_ingredients(db: AsyncSession):
    async with db() as session:
        # Создаем продукт
        product_data = CreationProduct(title="New Test Product", value_type="liter")
        created_product = await create_new_product(product_data, session)

        # Создаем item с ингредиентом
        initial_ingredient = AddingIngredient(product_id=created_product.id, value=2.0)
        item_data = ItemFields(title="Old Item", description="Old Description", ingredients=[initial_ingredient])
        created_item = await create_item(item_data, session)

        # Обновляем item
        new_ingredient = AddingIngredient(product_id=created_product.id, value=5.0)
        updated_data = ItemFields(title="Updated Item", description="Updated Description", ingredients=[new_ingredient])
        updated_item = await update_item(created_item.id, updated_data, session)

        assert updated_item.title == "Updated Item"
        assert updated_item.description == "Updated Description"
        assert len(updated_item.ingredients) == 1
        assert updated_item.ingredients[0].value == 5.0


@pytest.mark.asyncio
async def test_delete_item_with_ingredients(db: AsyncSession):
    async with db() as session:
        # Создаем продукт
        product_data = CreationProduct(title="Test Product for Deletion", value_type="unit")
        created_product = await create_new_product(product_data, session)

        # Создаем item с ингредиентом
        ingredient = AddingIngredient(product_id=created_product.id, value=3.0)
        item_data = ItemFields(title="Item to Delete", description="Delete Me", ingredients=[ingredient])
        created_item = await create_item(item_data, session)

        # Удаляем item
        await delete_item(created_item.id, session)

        # Проверяем, что item удален
        with pytest.raises(ValueError):
            await get_item_by_id(created_item.id, session)
