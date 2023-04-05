"""Added edit sports page form

Revision ID: 12896e22bf45
Revises: 5782b443a7c4
Create Date: 2023-04-05 11:10:00.273893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12896e22bf45'
down_revision = '5782b443a7c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('description', sa.String(length=140), nullable=True),
    sa.Column('sport_oic', sa.String(length=32), nullable=True),
    sa.Column('sport_oic_email', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('timing', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sports')
    # ### end Alembic commands ###
