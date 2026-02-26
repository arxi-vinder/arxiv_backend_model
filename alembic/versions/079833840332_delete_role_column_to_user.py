"""delete role column to user

Revision ID: 079833840332
Revises: 55bc51f9e21c
Create Date: 2026-02-26 11:47:26.636106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '079833840332'
down_revision: Union[str, Sequence[str], None] = '55bc51f9e21c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:    
    op.drop_column('users', 'role')