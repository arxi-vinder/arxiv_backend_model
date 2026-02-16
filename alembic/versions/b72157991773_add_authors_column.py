"""add authors column

Revision ID: b72157991773
Revises: 7656937d1c8b
Create Date: 2026-02-16 22:40:22.828716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b72157991773'
down_revision: Union[str, Sequence[str], None] = '7656937d1c8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('paper',sa.Column(
        'author',sa.String(length=255),nullable=True
    ))
