import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead, UserUpdate

from item import router as ItemRouter
from product import router as ProductRouter
from shop import router as ShopRouter
from allergen import router as AllergenRouter
from card import router as CardRouter
from comment import router as CommentRouter
from event import router as EventRouter
from auth import router as RoleRouter
from src.profile import router as ProfileRouter
from src.order import router as OrderRouter
from src.middleware import (
    db_integrity_error_middleware,
    validation_exception_handler,
    internal_server_error_middleware,
    not_found_error_middleware,
)


app = FastAPI(
    title="Product API",
)


app.middleware("http")(db_integrity_error_middleware)
app.middleware("http")(validation_exception_handler)
app.middleware("http")(internal_server_error_middleware)
app.middleware("http")(not_found_error_middleware)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(ItemRouter.router, prefix='/api/v1', tags=["Item"])
app.include_router(ProductRouter.router, prefix='/api/v1', tags=["Item Ingredients"])
app.include_router(ShopRouter.router, prefix='/api/v1', tags=["Shop"])
app.include_router(AllergenRouter.router, prefix='/api/v1', tags=["Allergen"])
app.include_router(CardRouter.router, prefix='/api/v1', tags=["Bonus Card"])
app.include_router(CommentRouter.router, prefix='/api/v1', tags=["Comment For Personal Or Items"])
app.include_router(EventRouter.router, prefix='/api/v1', tags=["Akce"])
app.include_router(ProfileRouter.router, prefix='/api/v1', tags=["Profile Management"])
app.include_router(OrderRouter.router, prefix='/api/v1', tags=["Order"])
app.include_router(RoleRouter.router, prefix='/api/v1', tags=["Role"])

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8090, reload=True, workers=3)
