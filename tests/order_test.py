import logging.config
from typing import Any

import pytest
import yaml
from httpx import AsyncClient, Response

from main import app
from src.services import base_init, clear_all_rows

with open("config.yaml", encoding="utf-8") as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("Can't read config file")
        raise exc
logging.config.dictConfig(cfg["logger"])
logger = logging.getLogger("testing")

base_init(cfg["db_path"])

URL = "/orders"
PRODUCTS_URL = "/products"

DEFAULT_PRODUCT_1 = {
                "name": "Name of first product",
                "description": "Some description",
                "price": 12.3,
                "quantity": 12,
            }
DEFAULT_PRODUCT_2 = {
                "name": "Name of second product",
                "description": "Some description",
                "price": 32.1,
                "quantity": 1,
            }
DEFAULT_PRODUCTS = [DEFAULT_PRODUCT_1, DEFAULT_PRODUCT_2]
DEFAULT_ORDER_1 = {
                "status": "First order",
                "items": {0: 10, 1: 1}
            }
DEFAULT_ORDER_2 = {
                "status": "Second order",
                "items": {0: 1}
            }
DEFAULT_ORDERS = [DEFAULT_ORDER_1, DEFAULT_ORDER_2]


async def _post_product(post_product: dict[str, Any]) -> int:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            PRODUCTS_URL,
            json=post_product,
        )
    assert response.status_code == 201
    return response.json()["id"]


async def _post_products(post_products: list[dict[str, Any]]) -> list[int]:
    return [await _post_product(post_product) for post_product in post_products]


async def _delete_product(product_id: int) -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            f"{PRODUCTS_URL}/{product_id}",
        )
    assert response.status_code == 204


async def _delete_products(product_ids: list[int]) -> None:
    for product_id in product_ids:
        await _delete_product(product_id)


async def _get_product(product_id: int) -> Response:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{PRODUCTS_URL}/{product_id}",
        )
    assert response.status_code == 200
    return response


def _convert_order_items_ids(items: dict[int, Any], product_ids: list[int]) -> dict[str, Any]:
    new_items: dict[str, Any] = dict()
    for key, value in items.items():
        if 0 <= key < len(product_ids):
            new_items[str(product_ids[key])] = value
        else:
            new_items[str(key)] = value
    return new_items


def _convert_order_to_result_type(post_order: dict[str, Any], post_products: list[dict[str, Any]]) -> dict[str, Any]:
    result_order = {"order_items": dict()}
    if "status" in post_order:
        result_order["status"] = post_order["status"]
    for key, value in post_order["items"].items():
        if 0 <= key < len(post_products):
            result_order["order_items"][post_products[key]["name"]] = value
        else:
            result_order["order_items"]["Unknown product"] = value
    return result_order


async def _get_order(order_id: int) -> Response:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{URL}/{order_id}",
        )
    assert response.status_code == 200
    return response


async def _post_order(post_order: dict[str, Any]) -> int:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            URL,
            json=post_order,
        )
    assert response.status_code == 201
    order_id = response.json()["id"]
    return order_id


async def _post_orders(post_orders: list[dict[str, Any]]) -> list[int]:
    return [await _post_order(post_order) for post_order in post_orders]


@pytest.mark.parametrize(
    "post_products, post_order, status_code",
    [
        (DEFAULT_PRODUCTS, {"status": "Some status", "items": {0: 10, 1: 1}}, 201),
        (DEFAULT_PRODUCTS, {"items": {0: 10, 1: 1}}, 201),
        (DEFAULT_PRODUCTS, {"status": "Some status", "items": {0: 10, 10: 1}}, 404),
        (DEFAULT_PRODUCTS, {"status": "Some status", "items": {0: 10, 1: 5}}, 400),
    ],
)
async def test_post_order(post_products: list[dict[str, Any]], post_order: dict[str, Any], status_code: int) -> None:
    await clear_all_rows()

    # Create items
    product_ids = await _post_products(post_products)

    # Convert order to result type
    result_order = _convert_order_to_result_type(post_order, post_products)

    # Convert order items ids
    old_items = post_order["items"]
    new_items = _convert_order_items_ids(old_items, product_ids)
    post_order["items"] = new_items

    # Create order
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            URL,
            json=post_order,
        )
    assert response.status_code == status_code
    if status_code != 201:
        await _delete_products(product_ids)
        return

    # Check response order
    order_id = response.json()["id"]
    response = await _get_order(order_id)
    response_order = response.json()
    for key, value in result_order.items():
        assert key in response_order
        if isinstance(value, dict):
            for inner_key, inner_value in value.items():
                assert inner_key in response_order[key]
                assert inner_value == response_order[key][inner_key]
            continue
        assert value == response_order[key]

    # Check quantity changes
    for i, product_id in enumerate(product_ids):
        response = await _get_product(product_id)
        response_product = response.json()
        assert response_product["quantity"] + old_items[i] == post_products[i]["quantity"]

    # Delete items
    await _delete_products(product_ids)


@pytest.mark.parametrize(
    "post_products, post_orders, result_orders, params",
    [
        (DEFAULT_PRODUCTS, DEFAULT_ORDERS, [DEFAULT_ORDER_1, DEFAULT_ORDER_2], {}),
        (DEFAULT_PRODUCTS, DEFAULT_ORDERS, [DEFAULT_ORDER_1], {"limit": 1}),
        (DEFAULT_PRODUCTS, DEFAULT_ORDERS, [DEFAULT_ORDER_2], {"limit": 1, "offset": 1}),
    ],
)
async def test_get_orders(post_products: list[dict[str, Any]], post_orders: list[dict[str, Any]], result_orders: list[dict[str, Any]], params: dict[str, Any]) -> None:
    await clear_all_rows()

    # Create items
    product_ids = await _post_products(post_products)

    # Convert order to result type
    result_orders = [_convert_order_to_result_type(order, post_products) for order in result_orders]

    # Convert order items ids
    post_orders_to_export: list[dict[str, Any]] = list()
    for post_order in post_orders:
        old_items = post_order["items"]
        new_items = _convert_order_items_ids(old_items, product_ids)
        post_orders_to_export.append({"status": post_order["status"], "items": new_items})

    # Create orders
    await _post_orders(post_orders_to_export)

    # Get items
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            URL,
            params=params
        )
    assert response.status_code == 200
    response_orders: list[dict[str, Any]] = response.json()
    for i, result_order in enumerate(result_orders):
        assert i < len(response_orders)
        for key, value in result_order.items():
            assert key in response_orders[i]
            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    assert inner_key in response_orders[i][key]
                    assert inner_value == response_orders[i][key][inner_key]
                continue
            assert value == response_orders[i][key]

    # Delete items
    for product_id in product_ids:
        await _delete_product(product_id)


@pytest.mark.parametrize(
    "post_products, post_order, status_code, index",
    [
        (DEFAULT_PRODUCTS, DEFAULT_ORDER_1, 200, None),
        (DEFAULT_PRODUCTS, DEFAULT_ORDER_1, 404, -1),
        (DEFAULT_PRODUCTS, DEFAULT_ORDER_1, 404, 100),
    ],
)
async def test_get_order(post_products: list[dict[str, Any]], post_order: dict[str, Any], status_code: int, index: int | None) -> None:
    await clear_all_rows()

    # Create items
    product_ids = await _post_products(post_products)

    # Convert order to result type
    result_order = _convert_order_to_result_type(post_order, post_products)

    # Convert order items ids
    old_items = post_order["items"]
    new_items = _convert_order_items_ids(old_items, product_ids)
    post_order_to_export = {"status": post_order["status"], "items": new_items}

    # Create order
    order_id = await _post_order(post_order_to_export)

    # Get order
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{URL}/{order_id if index is None else index}",
        )
    assert response.status_code == status_code
    if status_code == 200:
        response_order = response.json()
        for key, value in result_order.items():
            assert key in response_order
            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    assert inner_key in response_order[key]
                    assert inner_value == response_order[key][inner_key]
                continue
            assert value == response_order[key]

    # Delete items
    await _delete_products(product_ids)


@pytest.mark.parametrize(
    "post_products, post_order, status, status_code, index",
    [
        (DEFAULT_PRODUCTS, DEFAULT_ORDER_1, "Some new status", 200, None),
        (DEFAULT_PRODUCTS, DEFAULT_ORDER_1, "Some new status", 404, -1),
        (DEFAULT_PRODUCTS, DEFAULT_ORDER_1, "Some new status", 404, 100),
    ],
)
async def test_patch_order_status(post_products: list[dict[str, Any]], post_order: dict[str, Any], status: str, status_code: int, index: int | None) -> None:
    await clear_all_rows()

    # Create items
    product_ids = await _post_products(post_products)

    # Convert order to result type
    result_order = _convert_order_to_result_type(post_order, post_products)

    # Convert order items ids
    old_items = post_order["items"]
    new_items = _convert_order_items_ids(old_items, product_ids)
    post_order_to_export = {"status": post_order["status"], "items": new_items}

    # Create order
    order_id = await _post_order(post_order_to_export)

    # Change status
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch(
            f"{URL}/{order_id if index is None else index}/status",
            params={"order_status": status}
        )
    assert response.status_code == status_code

    # Get order
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{URL}/{order_id}",
        )
    assert response.status_code == 200
    response_order = response.json()
    assert response_order["status"] == status or status_code != 200

    # Delete items
    await _delete_products(product_ids)
