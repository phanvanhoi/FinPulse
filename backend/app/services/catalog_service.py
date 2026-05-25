from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductVariant

DEFAULT_CATALOG = [
    {
        "name": "Classic T-Shirt",
        "description": "100% cotton unisex t-shirt, perfect for custom designs",
        "category": "apparel",
        "variants": [
            ("S", Decimal("12.00")),
            ("M", Decimal("12.00")),
            ("L", Decimal("12.00")),
            ("XL", Decimal("13.00")),
            ("2XL", Decimal("14.00")),
        ],
    },
    {
        "name": "Premium Hoodie",
        "description": "Soft fleece hoodie with front pouch pocket",
        "category": "apparel",
        "variants": [
            ("S", Decimal("28.00")),
            ("M", Decimal("28.00")),
            ("L", Decimal("28.00")),
            ("XL", Decimal("30.00")),
            ("2XL", Decimal("32.00")),
        ],
    },
    {
        "name": "Ceramic Mug",
        "description": "11oz white ceramic mug, dishwasher safe",
        "category": "drinkware",
        "variants": [("One Size", Decimal("8.00"))],
    },
]


async def seed_catalog(db: AsyncSession) -> None:
    result = await db.execute(select(Product).where(Product.organization_id.is_(None)))
    if result.scalars().first():
        return

    for item in DEFAULT_CATALOG:
        product = Product(
            organization_id=None,
            name=item["name"],
            description=item["description"],
            category=item["category"],
        )
        db.add(product)
        await db.flush()

        for variant_name, price in item["variants"]:
            db.add(
                ProductVariant(
                    product_id=product.id,
                    name=variant_name,
                    sku=f"{product.name[:3].upper()}-{variant_name}",
                    base_price=price,
                )
            )
    await db.flush()


async def list_catalog(db: AsyncSession, fulfillment_provider: str | None = None) -> list[Product]:
    await seed_catalog(db)
    query = (
        select(Product)
        .where(Product.is_active.is_(True), Product.organization_id.is_(None))
        .options(selectinload(Product.variants))
        .order_by(Product.name)
    )
    if fulfillment_provider:
        query = query.where(Product.fulfillment_provider == fulfillment_provider)
    result = await db.execute(query)
    return list(result.scalars().all())
