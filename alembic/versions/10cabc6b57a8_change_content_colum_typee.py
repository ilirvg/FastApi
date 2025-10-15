"""change content colum typee

Revision ID: 10cabc6b57a8
Revises: 48a10f940ee4
Create Date: 2025-10-11 21:53:21.960330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10cabc6b57a8'
down_revision: Union[str, Sequence[str], None] = '48a10f940ee4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('posts', 'content', type_=sa.String())
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('posts', 'content', type_=sa.Integer())
    pass
