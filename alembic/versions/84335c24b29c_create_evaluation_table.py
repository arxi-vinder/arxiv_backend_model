"""create evaluation table 

Revision ID: 84335c24b29c
Revises: d6616865894e
Create Date: 2026-01-17 22:08:46.357744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '84335c24b29c'
down_revision: Union[str, Sequence[str], None] = 'd6616865894e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evaluation",
        sa.Column('id', sa.Integer, primary_key=True , autoincrement=True , index=True),
        sa.Column('metric_name', sa.String(255), nullable=False , index=True),
        sa.Column("score",sa.Integer,nullable=False,index=True),
        sa.Column("feedback_id",sa.Integer,sa.ForeignKey("feedback.id",name="fk_evaluation_feedback_ids"),index=True),
        sa.Column("created_at",sa.TIMESTAMP(timezone=True),index=True)
    )


def downgrade() -> None:
    op.drop_table("evaluation")
    op.drop_constraint(
        "fk_evaluation_feedback_ids",
        "evaluation",
        type_="foreignkey"
    )
