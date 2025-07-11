"""Initial migration

Revision ID: b99b4c03d4dd
Revises: ea8ffc9d70fb
Create Date: 2025-07-11 21:02:49.337592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b99b4c03d4dd'
down_revision: Union[str, Sequence[str], None] = 'ea8ffc9d70fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
