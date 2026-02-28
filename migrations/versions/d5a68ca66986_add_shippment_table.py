"""add shippment table

Revision ID: d5a68ca66986
Revises:
Create Date: 2026-03-01 04:00:39.471012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5a68ca66986'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "shipment",
        sa.Column("id", sa.UUID,primary_key=True),
        sa.Column("content",sa.CHAR,nullable=False),
        sa.Column("status",sa.CHAR,nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("shipment")
