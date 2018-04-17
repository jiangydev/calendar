"""empty message

Revision ID: 7b65a814d700
Revises: 3a763375215c
Create Date: 2018-04-08 19:17:57.682374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b65a814d700'
down_revision = '3a763375215c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('user_id', sa.String(length=100), nullable=False))
    op.create_foreign_key(None, 'task', 'front_user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task', type_='foreignkey')
    op.drop_column('task', 'user_id')
    # ### end Alembic commands ###
