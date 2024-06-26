"""Fix message/wager relationship

Revision ID: 889e5cb3676c
Revises: 50c32ff1611d
Create Date: 2020-10-29 15:39:51.206284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '889e5cb3676c'
down_revision = '50c32ff1611d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('message_wager_id_fkey', 'message', type_='foreignkey')
    op.create_foreign_key(None, 'message', 'wager', ['wager_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'message', type_='foreignkey')
    op.create_foreign_key('message_wager_id_fkey', 'message', 'team', ['wager_id'], ['id'])
    # ### end Alembic commands ###
