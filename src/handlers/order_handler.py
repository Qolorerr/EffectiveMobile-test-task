from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Path
from starlette.responses import JSONResponse

from src.exceptions import NotFoundError, NotEnoughProduct
from src.schemas import PostOrder
import src.services.order_service as service

router = APIRouter()


@router.post(
    "/",
    responses={
        201: {
            "content": {"application/json": {"example": {"id": 12}}},
            "description": "Order created",
        },
        400: {"description": "Not enough product to create order"},
        404: {"description": "Product not found"},
    },
)
async def post_product(args: PostOrder):
    try:
        order = await service.post_order(args)
    except NotFoundError as e:
        raise HTTPException(detail=e.args, status_code=status.HTTP_404_NOT_FOUND)
    except NotEnoughProduct as e:
        raise HTTPException(detail=e.args, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        content={"id": order.order_id}, status_code=status.HTTP_201_CREATED
    )


@router.get(
    "/",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "order_id": 12,
                            "status": "Created",
                            "order_items": {
                                "Product1": 2,
                                "Product2": 5,
                            },
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
async def get_orders(limit: int | None = None, offset: int = 0):
    orders = await service.get_orders(limit, offset)
    return JSONResponse(content=orders, status_code=status.HTTP_200_OK)


@router.get(
    "/{id}",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "order_id": 12,
                        "status": "Created",
                        "order_items": {
                            "Product1": 2,
                            "Product2": 5,
                        },
                        "created_at": "2024-09-20T12:00:00.000000",
                        "updated_at": "2024-09-20T12:00:00.000000",
                    }
                }
            },
            "description": "Ok",
        },
        404: {"description": "Order not found"},
    },
)
async def get_order(id: int):
    try:
        order = await service.get_order(id)
    except NotFoundError as e:
        raise HTTPException(detail=e.args, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(content=order, status_code=status.HTTP_200_OK)


@router.patch(
    "/{id}/status",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "order_id": 12,
                        "status": "Created",
                        "created_at": "2024-09-20T12:00:00.000000",
                        "updated_at": "2024-09-20T12:00:00.000000",
                    }
                }
            },
            "description": "Ok",
        },
        404: {"description": "Order not found"},
    },
)
async def set_order_status(order_status: str, id: Annotated[int, Path()]):
    try:
        order = await service.set_order_status(id, order_status)
    except NotFoundError as e:
        raise HTTPException(detail=e.args, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(content=order.as_dict(), status_code=status.HTTP_200_OK)
