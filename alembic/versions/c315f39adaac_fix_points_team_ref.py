"""Fix Points Team ref

Revision ID: c315f39adaac
Revises: 71986822288d
Create Date: 2020-10-27 01:56:15.541567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c315f39adaac'
down_revision = '71986822288d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('point', 'team_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('point', 'team_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
