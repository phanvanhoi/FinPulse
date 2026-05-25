"""Add abandoned checkout recovery tracking fields.

Revision ID: 003_abandoned_recovery
Revises: 002_add_commerce
Create Date: 2026-05-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_abandoned_recovery"
down_revision: Union[str, None] = "002_add_commerce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("carts", sa.Column("abandoned_email_sent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("orders", sa.Column("recovery_email_sent_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "recovery_email_sent_at")
    op.drop_column("carts", "abandoned_email_sent_at")
