"""empty message

Revision ID: eeb012bd88e5
Revises: da234779816f
Create Date: 2023-04-10 13:46:10.367651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eeb012bd88e5'
down_revision = 'da234779816f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sign_up_timestamp', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('attended_sport', sa.Boolean(), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_sign_up_timestamp'), ['sign_up_timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_sign_up_timestamp'))
        batch_op.drop_column('attended_sport')
        batch_op.drop_column('sign_up_timestamp')

    # ### end Alembic commands ###
