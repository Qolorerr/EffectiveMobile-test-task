from pydantic import BaseModel


class PostProduct(BaseModel):
    name: str
    price: float
    quantity: int
    description: str = ""


class PutProduct(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None
