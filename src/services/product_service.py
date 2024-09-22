from datetime import datetime

from sqlalchemy import select

from src.exceptions import NotFoundError
from src.models import Product
from src.schemas import PostProduct, PutProduct
from src.services import create_session


async def post_product(args: PostProduct) -> Product:
    async with create_session() as session:
        product = Product(
            name=args.name,
            description=args.description,
            price=args.price,
            quantity=args.quantity,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        session.add(product)
        await session.flush()
        await session.commit()
        return product


async def get_products(
    limit: int | None = None, offset: int | None = 0
) -> list[Product]:
    async with create_session() as session:
        query = select(Product)
        results: list[Product] = (await session.scalars(query)).all()
        if limit is not None:
            results = results[offset : offset + limit]
        return results


async def get_product(id: int) -> Product:
    async with create_session() as session:
        query = select(Product).where(Product.product_id == id)
        results: list[Product] = (await session.scalars(query)).all()
        if len(results) < 1:
            raise NotFoundError("Can't find product with this id")
        product = results[0]
        return product


async def put_product(id: int, args: PutProduct) -> Product:
    async with create_session() as session:
        product = await session.get(Product, id)
        if product is None:
            raise NotFoundError("Can't find product with this id")

        if args.name is not None:
            product.name = args.name
        if args.description is not None:
            product.description = args.description
        if args.price is not None:
            product.price = args.price
        if args.quantity is not None:
            product.quantity = args.quantity
        product.updated_at = datetime.now().isoformat()

        await session.commit()
        return product


async def delete_product(id: int):
    async with create_session() as session:
        product = await session.get(Product, id)
        if product is None:
            raise NotFoundError("Can't find product with this id")

        await session.delete(product)
        await session.commit()
