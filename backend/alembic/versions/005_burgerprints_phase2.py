"""Phase 2: structured shipping + connection uniqueness.

Revision ID: 005_burgerprints_phase2
Revises: 004_burgerprints_foundation
Create Date: 2026-05-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_burgerprints_phase2"
down_revision: Union[str, None] = "004_burgerprints_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("shipping_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_unique_constraint(
        "uq_org_connection_provider",
        "connections",
        ["organization_id", "provider"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_org_connection_provider", "connections", type_="unique")
    op.drop_column("orders", "shipping_details")
