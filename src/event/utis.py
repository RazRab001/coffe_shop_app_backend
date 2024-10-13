from typing import List
from src.event.benefit.model import Activity
from src.event.criterion.model import Contrast
from src.order.schema import GettingOrder
from src.card.schema import GettingCard


contrast_operations = {
    Contrast.greater_than: lambda order, card, criterion_value:
        greater_for_count_points(order, card, criterion_value),
    Contrast.greater_for_all: lambda order, card, criterion_value:
        greater_for_all_points(order, card, criterion_value),
    Contrast.count_items_in_order: lambda order, card, criterion_value:
        check_items_count_in_order(order, card, criterion_value),
    Contrast.define_item_in_order: lambda order, card, criterion_value:
        check_define_item_in_order(order, card, criterion_value),
}


benefit_operations = {
    Activity.add_cart_bonuses: lambda order, card, benefit_value: add_point_to_card(order, card, benefit_value),
    Activity.reduce_card_bonuses: lambda order, card, benefit_value: reduce_bonuses_on_count(order, card, benefit_value),
    Activity.reduce_order_sum: lambda order, card, benefit_value: reduce_sum_of_order_for_value(order, card, benefit_value),
    Activity.reduce_order_sum_percent: lambda order, card, benefit_value: reduce_sum_of_order_for_percent(order, card, benefit_value)
}


class BenefitResult:
    card_value: int
    used_points: int
    total_cost: float

    def __init__(self, card_value: int, used_points: int, total_cost: float):
        self.card_value = card_value
        self.used_points = used_points
        self.total_cost = total_cost


def add_point_to_card(order: GettingOrder, card: GettingCard, benefit_value: int) -> BenefitResult:
    return BenefitResult(
        card_value=card.count + benefit_value,
        used_points=card.used_points,
        total_cost=order.cost
    )


def reduce_bonuses_on_count(order: GettingOrder, card: GettingCard, benefit_value: int) -> BenefitResult:
    return BenefitResult(
        card_value=card.count - benefit_value,
        used_points=card.used_points + benefit_value,
        total_cost=order.cost
    )


def reduce_sum_of_order_for_value(order: GettingOrder, card: GettingCard, benefit_value: float) -> BenefitResult:
    return BenefitResult(
        card_value=card.count,
        used_points=card.used_points,
        total_cost=order.cost - benefit_value
    )


def reduce_sum_of_order_for_percent(order: GettingOrder, card: GettingCard, benefit_value: float) -> BenefitResult:
    return BenefitResult(
        card_value=card.count,
        used_points=card.used_points,
        total_cost=order.cost * (1 - benefit_value / 100)
    )


def greater_for_all_points(order: GettingOrder, card: GettingCard, criterion_value: float) -> bool:
    return card.point + card.used_points > criterion_value


def greater_for_count_points(order: GettingOrder, card: GettingCard, criterion_value: float) -> bool:
    return card.point > criterion_value


def check_items_count_in_order(order: GettingOrder, card: GettingCard, criterion_value: float) -> bool:
    return len(order.items) >= criterion_value


def check_define_item_in_order(order: GettingOrder, card: GettingCard, criterion_value: float) -> bool:
    return any(item.product_id == criterion_value for item in order.items)
