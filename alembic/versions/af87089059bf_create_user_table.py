"""create user table

Revision ID: af87089059bf
Revises: 
Create Date: 2026-01-15 19:44:42.959422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af87089059bf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True , autoincrement=True , index=True),
        sa.Column('username', sa.String(50), nullable=False , index=True,unique=False),
        sa.Column('password', sa.String(255),nullable=False , index=True , unique=True),
        sa.Column("role" , sa.String(50) , nullable=False,index=True),
        sa.Column("created_at",sa.TIMESTAMP(timezone=True),index=True)
    )

def downgrade():
    op.drop_table('user')