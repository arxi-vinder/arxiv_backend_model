"""summary table evaluation

Revision ID: e63b65c8496e
Revises: 025bac2aaf83
Create Date: 2026-04-26 23:01:05.514255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e63b65c8496e'
down_revision: Union[str, Sequence[str], None] = '025bac2aaf83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
