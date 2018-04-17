"""empty message

Revision ID: 3a763375215c
Revises: 2acf13c5c70c
Create Date: 2018-04-08 19:07:48.600312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a763375215c'
down_revision = '2acf13c5c70c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('id', sa.String(length=100), nullable=False),
    sa.Column('title', sa.String(length=30), nullable=False),
    sa.Column('content', sa.String(length=100), nullable=True),
    sa.Column('all_day', sa.Boolean(), nullable=True),
    sa.Column('starttime', sa.DateTime(), nullable=True),
    sa.Column('endtime', sa.DateTime(), nullable=True),
    sa.Column('email_remind', sa.Boolean(), nullable=True),
    sa.Column('message_remind', sa.Boolean(), nullable=True),
    sa.Column('remindtime', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('FINISHED', 'UNFINISHED', name='taskstatusenum'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task')
    # ### end Alembic commands ###
