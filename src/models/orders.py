from typing import Any

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.services.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}
    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(nullable=False, default="created")
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)

    order_items = relationship("OrderItem", back_populates="order")

    def as_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
