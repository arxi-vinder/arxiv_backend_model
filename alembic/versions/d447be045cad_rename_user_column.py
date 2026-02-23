"""rename url column

Revision ID: d447be045cad
Revises: a40a78282e31
Create Date: 2026-02-21 21:08:26.451667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd447be045cad'
down_revision: Union[str, Sequence[str], None] = 'a40a78282e31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass