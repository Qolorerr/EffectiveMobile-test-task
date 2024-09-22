from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Path
from starlette.responses import JSONResponse, Response

from src.exceptions import NotFoundError
from src.schemas import PostProduct, PutProduct
import src.services.product_service as service

router = APIRouter()


@router.post(
    "/",
    responses={
        201: {
            "content": {"application/json": {"example": {"id": 12}}},
            "description": "Product created",
        },
    },
)
async def post_product(args: PostProduct):
    product = await service.post_product(args)
    return JSONResponse(
        content={"id": product.product_id}, status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "product_id": 12,
                            "name": "Name of product",
                            "description": "Description",
                            "price": 12.3,
                            "quantity": 12,
                            "created_at": "2024-09-20T12:00:00.000000",
                            "updated_at": "2024-09-20T12:00:00.000000",
                        }
                    ]
                }
            },
            "description": "Ok",
        },
    },
)
async def get_products(limit: int | None = None, offset: int | None = 0):
    products = await service.get_products(limit, offset)
    products_to_export = list(map(lambda x: x.as_dict(), products))
    return JSONResponse(content=products_to_export, status_code=status.HTTP_200_OK)


@router.get(
    "/{id}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "product_id": 12,
                        "name": "Name of product",
                        "description": "Description",
                        "price": 12.3,
                        "quantity": 12,
                        "created_at": "2024-09-20T12:00:00.000000",
                        "updated_at": "2024-09-20T12:00:00.000000",
                    }
                }
            },
            "description": "Ok",
        },
        404: {"description": "Product not found"},
    },
)
async def get_product(id: int):
    try:
        product = await service.get_product(id)
    except NotFoundError as e:
        raise HTTPException(detail=e.args, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(content=product.as_dict(), status_code=status.HTTP_200_OK)


@router.put(
    "/{id}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "product_id": 12,
                        "name": "Name of product",
                        "description": "Description",
                        "price": 12.3,
                        "quantity": 12,
                        "created_at": "2024-09-20T12:00:00.000000",
                        "updated_at": "2024-09-20T12:00:00.000000",
                    }
                }
            },
            "description": "Ok",
        },
        404: {"description": "Product not found"},
    },
)
async def put_product(args: PutProduct, id: Annotated[int, Path()]):
    try:
        product = await service.put_product(id, args)
    except NotFoundError as e:
        raise HTTPException(detail=e.args, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(content=product.as_dict(), status_code=status.HTTP_200_OK)


@router.delete(
    "/{id}",
    responses={
        204: {"description": "Product deleted"},
        404: {"description": "Product not found"},
    },
)
async def delete_product(id: Annotated[int, Path()]):
    try:
        await service.delete_product(id)
    except NotFoundError as e:
        raise HTTPException(detail=e.args, status_code=status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
