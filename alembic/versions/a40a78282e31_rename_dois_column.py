"""rename dois column

Revision ID: a40a78282e31
Revises: 8f78cbf01868
Create Date: 2026-02-21 21:07:00.278387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a40a78282e31'
down_revision: Union[str, Sequence[str], None] = '8f78cbf01868'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('feedback', 'feedbacks')
