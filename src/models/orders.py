from sqlalchemy.orm import Mapped, mapped_column

from src.services.db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = "orders"
    __table_args__ = {"extend_existing": True}
    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(nullable=False, default="created")
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)
