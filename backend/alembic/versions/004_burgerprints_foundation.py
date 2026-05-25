"""BurgerPrints integration foundation: fulfillment fields and catalog mapping.

Revision ID: 004_burgerprints_foundation
Revises: 003_abandoned_recovery
Create Date: 2026-05-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_burgerprints_foundation"
down_revision: Union[str, None] = "003_abandoned_recovery"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

fulfillment_status = postgresql.ENUM(
    "pending",
    "submitted",
    "unpaid",
    "in_production",
    "shipped",
    "delivered",
    "failed",
    "cancelled",
    name="fulfillmentstatus",
    create_type=False,
)


def upgrade() -> None:
    fulfillment_status.create(op.get_bind(), checkfirst=True)

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                "ALTER TYPE connectionprovider ADD VALUE IF NOT EXISTS 'burger_prints'"
            )
        )

    op.add_column("products", sa.Column("fulfillment_provider", sa.String(length=50), nullable=True))
    op.add_column("products", sa.Column("external_product_code", sa.String(length=100), nullable=True))
    op.add_column("products", sa.Column("fulfillment_location", sa.String(length=10), nullable=True))

    op.add_column("product_variants", sa.Column("provider_sku", sa.String(length=100), nullable=True))
    op.add_column("product_variants", sa.Column("color", sa.String(length=50), nullable=True))
    op.add_column("product_variants", sa.Column("external_variant_id", sa.String(length=100), nullable=True))
    op.create_index(
        op.f("ix_product_variants_provider_sku"),
        "product_variants",
        ["provider_sku"],
        unique=False,
    )

    op.add_column("sales_campaigns", sa.Column("design_back_url", sa.String(length=500), nullable=True))
    op.add_column(
        "sales_campaigns",
        sa.Column("print_location", sa.String(length=20), nullable=False, server_default="front"),
    )

    op.add_column("orders", sa.Column("fulfillment_provider", sa.String(length=50), nullable=True))
    op.add_column("orders", sa.Column("external_order_id", sa.String(length=100), nullable=True))
    op.add_column("orders", sa.Column("fulfillment_status", fulfillment_status, nullable=True))
    op.add_column("orders", sa.Column("fulfillment_submitted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("fulfillment_error", sa.Text(), nullable=True))
    op.add_column("orders", sa.Column("tracking_number", sa.String(length=100), nullable=True))
    op.create_index(op.f("ix_orders_external_order_id"), "orders", ["external_order_id"], unique=False)

    op.add_column("order_items", sa.Column("provider_sku", sa.String(length=100), nullable=True))
    op.add_column("order_items", sa.Column("design_front_url", sa.String(length=500), nullable=True))
    op.add_column("order_items", sa.Column("design_back_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("order_items", "design_back_url")
    op.drop_column("order_items", "design_front_url")
    op.drop_column("order_items", "provider_sku")

    op.drop_index(op.f("ix_orders_external_order_id"), table_name="orders")
    op.drop_column("orders", "tracking_number")
    op.drop_column("orders", "fulfillment_error")
    op.drop_column("orders", "fulfillment_submitted_at")
    op.drop_column("orders", "fulfillment_status")
    op.drop_column("orders", "external_order_id")
    op.drop_column("orders", "fulfillment_provider")

    op.drop_column("sales_campaigns", "print_location")
    op.drop_column("sales_campaigns", "design_back_url")

    op.drop_index(op.f("ix_product_variants_provider_sku"), table_name="product_variants")
    op.drop_column("product_variants", "external_variant_id")
    op.drop_column("product_variants", "color")
    op.drop_column("product_variants", "provider_sku")

    op.drop_column("products", "fulfillment_location")
    op.drop_column("products", "external_product_code")
    op.drop_column("products", "fulfillment_provider")

    fulfillment_status.drop(op.get_bind(), checkfirst=True)
