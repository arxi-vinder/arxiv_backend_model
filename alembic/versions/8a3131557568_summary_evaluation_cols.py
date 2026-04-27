"""summary-evaluation-cols

Revision ID: 8a3131557568
Revises: e63b65c8496e
Create Date: 2026-04-27 08:56:26.251618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a3131557568'
down_revision: Union[str, Sequence[str], None] = 'e63b65c8496e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('evaluation_results',
        sa.Column('id', sa.Integer(), nullable=False , autoincrement=True, primary_key=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('mean_average_precision', sa.Float(), nullable=True),
        sa.Column('k', sa.Integer(), nullable=True),
        sa.Column("user_id",sa.Integer,sa.ForeignKey("users.id",name="fk_summary_evaluation_id_users"),index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
