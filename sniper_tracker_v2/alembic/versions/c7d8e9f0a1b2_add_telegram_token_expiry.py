"""add telegram_connect_token_expires_at to users

Revision ID: c7d8e9f0a1b2
Revises: b5c1d2e3f4a6
Create Date: 2026-10-18 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, None] = 'b5c1d2e3f4a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('telegram_connect_token_expires_at', sa.DateTime(timezone=True), nullable=True))
    # Старые ссылки привязки были бессрочными — аннулируем их
    op.execute("UPDATE users SET telegram_connect_token = NULL")


def downgrade() -> None:
    op.drop_column('users', 'telegram_connect_token_expires_at')
