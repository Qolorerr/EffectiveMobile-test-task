from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.exceptions import NotFoundError, NotEnoughProduct
from src.models import Order, Product, OrderItem
from src.schemas import PostOrder
from src.services import create_session


async def post_order(args: PostOrder) -> Order:
    async with create_session() as session:
        order = Order(
            status=args.status,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        session.add(order)

        for product_id, quantity in args.items.items():
            product = await session.get(Product, product_id)
            if product is None:
                raise NotFoundError(f"Can't find product with id {product_id}")
            if product.quantity < quantity:
                raise NotEnoughProduct(
                    f"Not enough product with id {product_id} ({product.quantity}/{quantity})"
                )
            product.quantity -= quantity

            order_item = OrderItem(
                order_id=order.order_id, product_id=product_id, quantity=quantity
            )
            session.add(order_item)

        await session.flush()
        await session.commit()
        return order


async def get_orders(limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
    async with create_session() as session:
        query = (
            select(Order)
            .options(joinedload(Order.order_items).joinedload(OrderItem.product))
        )
        results = (await session.scalars(query)).unique().all()

        orders_list = []
        for order in results:
            order_dict = order.as_dict()
            order_dict["order_items"] = {}
            for item in order.order_items:
                product_name = item.product.name
                product_quantity = item.quantity
                order_dict["order_items"][product_name] = product_quantity
            orders_list.append(order_dict)
        if limit is not None:
            orders_list = orders_list[offset : offset + limit]
        return orders_list


async def get_order(id: int) -> dict[str, Any]:
    async with create_session() as session:
        query = (
            select(Order)
            .options(joinedload(Order.order_items).joinedload(OrderItem.product))
            .where(Order.order_id == id)
        )
        order = (await session.scalars(query)).first()

        if order is None:
            raise NotFoundError("Can't find order with this id")

        order_dict = order.as_dict()
        order_dict["order_items"] = {}
        for item in order.order_items:
            product_name = item.product.name
            product_quantity = item.quantity
            order_dict["order_items"][product_name] = product_quantity
        return order_dict


async def set_order_status(id: int, status: str) -> Order:
    async with create_session() as session:
        order = await session.get(Order, id)
        if order is None:
            raise NotFoundError("Can't find order with this id")

        order.status = status
        order.updated_at = datetime.now().isoformat()

        await session.commit()
        return order
