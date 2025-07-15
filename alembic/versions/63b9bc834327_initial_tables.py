"""Initial tables

Revision ID: 63b9bc834327
Revises: 
Create Date: 2025-07-13 17:47:28.870234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63b9bc834327'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('telegram_id', sa.String, nullable=False, unique=True),
        sa.Column('name', sa.String),
        sa.Column('registered_at', sa.DateTime),
        sa.Column('subscription_settings', sa.String)
    )

    op.create_table(
        'logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('command', sa.String),
        sa.Column('timestamp', sa.DateTime)
    )


def downgrade():
    op.drop_table('logs')
    op.drop_table('users')
