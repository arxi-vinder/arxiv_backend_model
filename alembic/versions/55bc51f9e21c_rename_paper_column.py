"""rename paper column

Revision ID: 55bc51f9e21c
Revises: cb47b035cf0b
Create Date: 2026-02-21 22:22:41.576618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55bc51f9e21c'
down_revision: Union[str, Sequence[str], None] = 'cb47b035cf0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('paper', 'papers')