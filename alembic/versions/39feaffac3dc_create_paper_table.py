"""create paper table 

Revision ID: 39feaffac3dc
Revises: 5213de2861d0
Create Date: 2026-01-15 23:05:08.715561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import datetime

# revision identifiers, used by Alembic.
revision: str = '39feaffac3dc'
down_revision: Union[str, Sequence[str], None] = '5213de2861d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'paper',
        sa.Column('id', sa.Integer, primary_key=True , autoincrement=True , index=True),
        sa.Column("title",sa.String(255),index=True,nullable=False),
        sa.Column("abstract",sa.Text,index=True,nullable=False),
        sa.Column("published_date" , sa.DATETIME,index=True),
        sa.Column("category",sa.String(255),index=True),
        sa.Column("url",sa.String(255),index=True),
        sa.Column("doi",sa.String(255),index=True),
        sa.Column("created_at", sa.DATETIME,index=True,default=datetime.datetime.now)
    )

def downgrade():
    op.drop_table('paper')    
