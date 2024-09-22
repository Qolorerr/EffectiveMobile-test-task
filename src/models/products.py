from typing import Any

from sqlalchemy.orm import Mapped, mapped_column

from src.services.db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = "products"
    __table_args__ = {"extend_existing": True}
    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)

    def as_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
