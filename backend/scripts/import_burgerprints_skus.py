"""Import BurgerPrints SKU CSV into FinPulse product catalog.

Expected CSV columns (header row required):
  product_name, product_code, color, size, fulfillment_location, provider_sku, base_price, category

Example:
  Unisex T-Shirt,G5000,Black,M,US,G5000-BLK-M-US,6.75,apparel

Usage:
  cd backend && python -m scripts.import_burgerprints_skus path/to/skus.csv
  cd backend && python -m scripts.import_burgerprints_skus path/to/skus.csv --replace
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select

from app.core.database import async_session_factory
from app.integrations.burgerprints.schemas import BurgerPrintsSkuRow
from app.models.product import Product, ProductVariant

FULFILLMENT_PROVIDER = "burger_prints"

REQUIRED_COLUMNS = {
    "product_name",
    "product_code",
    "color",
    "size",
    "fulfillment_location",
    "provider_sku",
}


def _parse_decimal(value: str | None) -> Decimal | None:
    if not value or not value.strip():
        return None
    try:
        return Decimal(value.strip())
    except InvalidOperation:
        return None


def load_sku_rows(csv_path: Path) -> list[BurgerPrintsSkuRow]:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or missing a header row")

        columns = {name.strip().lower() for name in reader.fieldnames}
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        rows: list[BurgerPrintsSkuRow] = []
        for index, raw in enumerate(reader, start=2):
            normalized = {key.strip().lower(): (value or "").strip() for key, value in raw.items()}
            provider_sku = normalized.get("provider_sku", "")
            if not provider_sku:
                print(f"Skipping row {index}: missing provider_sku")
                continue

            rows.append(
                BurgerPrintsSkuRow(
                    product_name=normalized["product_name"],
                    product_code=normalized["product_code"],
                    color=normalized["color"],
                    size=normalized["size"],
                    fulfillment_location=normalized["fulfillment_location"],
                    provider_sku=provider_sku,
                    base_price=_parse_decimal(normalized.get("base_price")),
                    category=normalized.get("category") or "apparel",
                )
            )
    return rows


async def import_skus(csv_path: Path, replace: bool = False) -> None:
    rows = load_sku_rows(csv_path)
    if not rows:
        print("No SKU rows to import.")
        return

    grouped: dict[tuple[str, str, str, str], list[BurgerPrintsSkuRow]] = defaultdict(list)
    for row in rows:
        key = (row.product_code, row.product_name, row.fulfillment_location, row.category)
        grouped[key].append(row)

    async with async_session_factory() as session:
        if replace:
            existing = await session.execute(
                select(Product.id).where(
                    Product.organization_id.is_(None),
                    Product.fulfillment_provider == FULFILLMENT_PROVIDER,
                )
            )
            product_ids = [row[0] for row in existing.all()]
            if product_ids:
                await session.execute(delete(ProductVariant).where(ProductVariant.product_id.in_(product_ids)))
                await session.execute(
                    delete(Product).where(
                        Product.organization_id.is_(None),
                        Product.fulfillment_provider == FULFILLMENT_PROVIDER,
                    )
                )
                await session.flush()

        created_products = 0
        updated_products = 0
        created_variants = 0
        updated_variants = 0

        for (product_code, product_name, location, category), variants in grouped.items():
            existing_product = (
                await session.execute(
                    select(Product).where(
                        Product.organization_id.is_(None),
                        Product.external_product_code == product_code,
                        Product.fulfillment_location == location,
                        Product.fulfillment_provider == FULFILLMENT_PROVIDER,
                    )
                )
            ).scalar_one_or_none()

            if existing_product:
                product = existing_product
                product.name = product_name
                product.category = category
                product.is_active = True
                updated_products += 1
            else:
                product = Product(
                    organization_id=None,
                    name=product_name,
                    description=f"BurgerPrints {product_code} ({location})",
                    category=category,
                    fulfillment_provider=FULFILLMENT_PROVIDER,
                    external_product_code=product_code,
                    fulfillment_location=location,
                    is_active=True,
                )
                session.add(product)
                await session.flush()
                created_products += 1

            for row in variants:
                variant_name = f"{row.color} / {row.size}"
                base_price = row.base_price if row.base_price is not None else Decimal("0.00")
                existing_variant = (
                    await session.execute(
                        select(ProductVariant).where(
                            ProductVariant.product_id == product.id,
                            ProductVariant.provider_sku == row.provider_sku,
                        )
                    )
                ).scalar_one_or_none()

                if existing_variant:
                    existing_variant.name = variant_name
                    existing_variant.sku = row.provider_sku
                    existing_variant.base_price = base_price
                    existing_variant.color = row.color
                    existing_variant.external_variant_id = row.provider_sku
                    updated_variants += 1
                else:
                    session.add(
                        ProductVariant(
                            product_id=product.id,
                            name=variant_name,
                            sku=row.provider_sku,
                            base_price=base_price,
                            provider_sku=row.provider_sku,
                            color=row.color,
                            external_variant_id=row.provider_sku,
                        )
                    )
                    created_variants += 1

        await session.commit()
        print(
            f"Imported from {csv_path}: "
            f"{created_products} new product(s), {updated_products} updated product(s), "
            f"{created_variants} new variant(s), {updated_variants} updated variant(s)"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import BurgerPrints SKU CSV into FinPulse catalog")
    parser.add_argument("csv_path", type=Path, help="Path to SKU CSV file")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Remove existing global BurgerPrints catalog before import",
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        raise SystemExit(f"File not found: {args.csv_path}")

    asyncio.run(import_skus(args.csv_path, replace=args.replace))


if __name__ == "__main__":
    main()
