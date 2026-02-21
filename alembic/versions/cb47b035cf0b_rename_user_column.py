"""rename user column

Revision ID: cb47b035cf0b
Revises: d447be045cad
Create Date: 2026-02-21 21:33:34.559574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb47b035cf0b'
down_revision: Union[str, Sequence[str], None] = 'd447be045cad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('user', 'users')