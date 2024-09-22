from fastapi import FastAPI

from src.handlers.product_handler import router as product_router
from src.handlers.order_handler import router as order_router


def register_routes(app: FastAPI) -> None:
    app.include_router(product_router, prefix="/products", tags=["Work with products"])
    app.include_router(order_router, prefix="/orders", tags=["Work with orders"])
