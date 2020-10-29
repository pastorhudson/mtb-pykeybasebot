"""create message table

Revision ID: 50c32ff1611d
Revises: c7dbcaf6f33e
Create Date: 2020-10-29 15:26:48.823437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50c32ff1611d'
down_revision = 'c7dbcaf6f33e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('msg_id', sa.String(), nullable=True),
    sa.Column('wager_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['wager_id'], ['team.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_msg_id'), 'message', ['msg_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_message_msg_id'), table_name='message')
    op.drop_table('message')
    # ### end Alembic commands ###
