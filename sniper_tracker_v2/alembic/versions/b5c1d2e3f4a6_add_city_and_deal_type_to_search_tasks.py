"""add city and deal_type to search_tasks

Revision ID: b5c1d2e3f4a6
Revises: 7be4b1213f15
Create Date: 2026-10-18 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c1d2e3f4a6'
down_revision: Union[str, None] = '7be4b1213f15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('search_tasks', sa.Column('city', sa.String(length=50), nullable=True))
    op.add_column('search_tasks', sa.Column('deal_type', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('search_tasks', 'deal_type')
    op.drop_column('search_tasks', 'city')
