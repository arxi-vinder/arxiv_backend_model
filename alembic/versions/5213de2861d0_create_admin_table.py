"""create admin table

Revision ID: 5213de2861d0
Revises: af87089059bf
Create Date: 2026-01-15 22:47:50.422256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5213de2861d0'
down_revision: Union[str, Sequence[str], None] = 'af87089059bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'admin',
        sa.Column('id', sa.Integer, primary_key=True , autoincrement=True , index=True),
        sa.Column('username', sa.String(50), nullable=False , index=True,unique=False),
        sa.Column('password', sa.String(255),nullable=False , index=True , unique=True),
        sa.Column("role" , sa.String(50) , nullable=False,index=True),
        sa.Column("created_at",sa.TIMESTAMP(timezone=True),index=True)
    )

def downgrade():
    op.drop_table('admin')    
