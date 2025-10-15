"""add conntent column on posts table

Revision ID: 48a10f940ee4
Revises: fb8c4c809ab0
Create Date: 2025-10-11 21:46:15.398871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48a10f940ee4'
down_revision: Union[str, Sequence[str], None] = 'fb8c4c809ab0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
