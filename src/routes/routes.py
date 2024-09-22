from fastapi import FastAPI

from src.handlers.product_handler import router as product_router


def register_routes(app: FastAPI) -> None:
    app.include_router(product_router, prefix="/products", tags=["Work with products"])
