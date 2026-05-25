"""Add PayPal payment fields to orders.

Revision ID: 006_paypal_payments
Revises: 005_burgerprints_phase2
Create Date: 2026-05-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_paypal_payments"
down_revision: Union[str, None] = "005_burgerprints_phase2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("payment_provider", sa.String(length=20), nullable=True))
    op.add_column("orders", sa.Column("paypal_order_id", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_orders_paypal_order_id"), "orders", ["paypal_order_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_orders_paypal_order_id"), table_name="orders")
    op.drop_column("orders", "paypal_order_id")
    op.drop_column("orders", "payment_provider")
