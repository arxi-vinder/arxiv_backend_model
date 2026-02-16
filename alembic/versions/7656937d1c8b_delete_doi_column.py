"""delete doi column

Revision ID: 7656937d1c8b
Revises: 84335c24b29c
Create Date: 2026-02-16 14:10:07.978537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7656937d1c8b'
down_revision: Union[str, Sequence[str], None] = '84335c24b29c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column('paper', 'doi')
