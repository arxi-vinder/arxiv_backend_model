"""create feedback table

Revision ID: d6616865894e
Revises: 39feaffac3dc
Create Date: 2026-01-16 13:47:35.240865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd6616865894e'
down_revision: Union[str, Sequence[str], None] = '39feaffac3dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column('id', sa.Integer, primary_key=True , autoincrement=True , index=True),
        sa.Column('response', sa.Integer, nullable=False , index=True),
        sa.Column("paper_id",sa.Integer,sa.ForeignKey("paper.id",name="fk_paper_id_users"),index=True),
        sa.Column("user_id",sa.Integer,sa.ForeignKey("user.id",name="fk_feedbacks_id_users"),index=True),
        sa.Column("created_at",sa.TIMESTAMP(timezone=True),index=True)
    )
    


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_constraint(
        "fk_paper_id_users",
        "feedbacks",
        type_="foreignkey"
    )
    
    op.drop_constraint(
        "fk_feedbacks_id_users",
        "feedbacks",
        type_="foreignkey"
    )
