from pydantic import BaseModel


class PostOrder(BaseModel):
    items: dict[int, int]
    status: str = "Created"
