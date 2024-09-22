from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.services.db_session import SqlAlchemyBase


class OrderItem(SqlAlchemyBase):
    __tablename__ = "order_items"
    __table_args__ = {"extend_existing": True}
    order_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
