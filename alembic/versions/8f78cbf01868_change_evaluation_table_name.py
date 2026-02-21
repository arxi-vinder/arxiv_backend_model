"""change evaluation table name

Revision ID: 8f78cbf01868
Revises: b72157991773
Create Date: 2026-02-21 20:55:30.908335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '8f78cbf01868'
down_revision: Union[str, Sequence[str], None] = 'b72157991773'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('evaluation', 'evaluations')