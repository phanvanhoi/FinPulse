"""Add stores table for Phase 1 storefront settings.

Revision ID: 001_add_stores
Revises:
Create Date: 2026-05-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_add_stores"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

domain_verification_status = postgresql.ENUM(
    "unverified",
    "pending",
    "verified",
    name="domainverificationstatus",
    create_type=False,
)


def upgrade() -> None:
    domain_verification_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("favicon_url", sa.String(length=500), nullable=True),
        sa.Column("custom_domain", sa.String(length=255), nullable=True),
        sa.Column("domain_verification_token", sa.String(length=64), nullable=True),
        sa.Column(
            "domain_verification_status",
            domain_verification_status,
            nullable=False,
            server_default="unverified",
        ),
        sa.Column("tips_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tip_options", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[10, 15, 20]"),
        sa.Column("facebook_pixel_id", sa.String(length=50), nullable=True),
        sa.Column("google_analytics_id", sa.String(length=50), nullable=True),
        sa.Column("abandoned_checkout_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("abandoned_checkout_delay_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("abandoned_checkout_email_subject", sa.String(length=255), nullable=True),
        sa.Column("abandoned_checkout_email_body", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_stores_organization_id"), "stores", ["organization_id"], unique=False)
    op.create_index(op.f("ix_stores_slug"), "stores", ["slug"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stores_slug"), table_name="stores")
    op.drop_index(op.f("ix_stores_organization_id"), table_name="stores")
    op.drop_table("stores")
    domain_verification_status.drop(op.get_bind(), checkfirst=True)
