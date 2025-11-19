"""merge heads

Revision ID: dae2eaa2ec50
Revises: bb699075faa1, df0c6e7f9905
Create Date: 2025-11-19 11:27:46.154083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dae2eaa2ec50'
down_revision: Union[str, Sequence[str], None] = ('bb699075faa1', 'df0c6e7f9905')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
