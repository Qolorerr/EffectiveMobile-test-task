import logging.config
from typing import Any

import pytest
import yaml
from httpx import AsyncClient, Response

from main import app
from src.services import base_init

with open("config.yaml", encoding="utf-8") as stream:
    try:
        cfg = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("Can't read config file")
        raise exc
logging.config.dictConfig(cfg["logger"])
logger = logging.getLogger("testing")

base_init(cfg["db_path"])

URL = "/products"
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


async def _post_product(post_product: dict[str, Any]) -> int:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            URL,
            json=post_product,
        )
    assert response.status_code == 201
    product_id = response.json()["id"]
    return product_id


async def _post_products(post_products: list[dict[str, Any]]) -> list[int]:
    return [await _post_product(post_product) for post_product in post_products]


async def _get_product(product_id: int) -> Response:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{URL}/{product_id}",
        )
    assert response.status_code == 200
    return response


async def _delete_product(product_id: int) -> Response:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            f"{URL}/{product_id}",
        )
    assert response.status_code == 204
    return response


async def _delete_products(product_ids: list[int]) -> None:
    for product_id in product_ids:
        await _delete_product(product_id)


@pytest.mark.parametrize(
    "post_product, status_code",
    [
        (
            {
                "name": "Name of product",
                "description": "Some description",
                "price": 12.3,
                "quantity": 12,
            },
            201,
        ),
        ({"name": "Name of product", "price": 12.3, "quantity": 12}, 201),
        (
            {
                "name": "Name of product",
                "description": "Some description",
                "price": "Definitely not price",
                "quantity": 12,
            },
            422,
        ),
        ({"description": "Some description", "price": 12.3, "quantity": 12}, 422),
    ],
)
async def test_post_product(post_product: dict[str, Any], status_code: int) -> None:
    # Create item
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            URL,
            json=post_product,
        )
    assert response.status_code == status_code
    if status_code != 201:
        return

    product_id = response.json()["id"]

    # Get item
    response = await _get_product(product_id)
    response_product = response.json()
    for key, value in post_product.items():
        assert key in response_product
        assert value == response_product[key]

    # Delete item
    await _delete_product(product_id)


@pytest.mark.parametrize(
    "post_products, result_products, params",
    [
        (DEFAULT_PRODUCTS, [DEFAULT_PRODUCT_1, DEFAULT_PRODUCT_2], {}),
        (DEFAULT_PRODUCTS, [DEFAULT_PRODUCT_1], {"limit": 1}),
        (DEFAULT_PRODUCTS, [DEFAULT_PRODUCT_2], {"limit": 1, "offset": 1}),
    ],
)
async def test_get_products(post_products: list[dict[str, Any]], result_products: list[dict[str, Any]], params: dict[str, Any]) -> None:
    # Create items
    product_ids = await _post_products(post_products)

    # Get items
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            URL,
            params=params
        )
    assert response.status_code == 200
    response_products: list[dict[str, Any]] = response.json()
    for i, result_product in enumerate(result_products):
        assert i < len(response_products)
        for key, value in result_product.items():
            assert key in response_products[i]
            assert value == response_products[i][key]

    # Delete items
    await _delete_products(product_ids)


@pytest.mark.parametrize(
    "post_product, status_code, index",
    [
        (DEFAULT_PRODUCT_1, 200, None),
        (DEFAULT_PRODUCT_1, 404, -1),
        (DEFAULT_PRODUCT_1, 404, 10),
    ],
)
async def test_get_product(post_product: dict[str, Any], status_code: int, index: int | None) -> None:
    # Create item
    product_id = await _post_product(post_product)

    # Get item
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{URL}/{product_id if index is None else index}",
        )
    assert response.status_code == status_code
    if status_code == 200:
        response_product = response.json()
        for key, value in post_product.items():
            assert key in response_product
            assert value == response_product[key]

    # Delete item
    await _delete_product(product_id)


@pytest.mark.parametrize(
    "post_product, put_product, status_code, index",
    [
        (DEFAULT_PRODUCT_1, DEFAULT_PRODUCT_2, 200, None),
        (DEFAULT_PRODUCT_1, DEFAULT_PRODUCT_2, 404, -1),
        (DEFAULT_PRODUCT_1, DEFAULT_PRODUCT_2, 404, 10),
    ],
)
async def test_put_product(post_product: dict[str, Any], put_product: dict[str, Any], status_code: int, index: int | None) -> None:
    # Create item
    product_id = await _post_product(post_product)

    # Put item
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            f"{URL}/{product_id if index is None else index}",
            json=put_product,
        )
    assert response.status_code == status_code
    if status_code == 200:
        response_product = response.json()
        for key, value in put_product.items():
            assert key in response_product
            assert value == response_product[key]

    # Delete item
    await _delete_product(product_id)


@pytest.mark.parametrize(
    "post_product, status_code, index",
    [
        (DEFAULT_PRODUCT_1, 204, None),
        (DEFAULT_PRODUCT_1, 404, -1),
        (DEFAULT_PRODUCT_1, 404, 10),
    ],
)
async def test_delete_product(post_product: dict[str, Any], status_code: int, index: int | None) -> None:
    # Create item
    product_id = await _post_product(post_product)

    # Delete item
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            f"{URL}/{product_id if index is None else index}",
        )
    assert response.status_code == status_code
    if status_code == 204:
        return
    await _delete_product(product_id)
