"""add conv_id to Messages Table

Revision ID: ee8952a054f5
Revises: af722e6e50bb
Create Date: 2020-10-29 16:00:32.327731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee8952a054f5'
down_revision = 'af722e6e50bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('conv_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_message_conv_id'), 'message', ['conv_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_message_conv_id'), table_name='message')
    op.drop_column('message', 'conv_id')
    # ### end Alembic commands ###