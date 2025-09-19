"""make persons.email unique

Revision ID: 0015
Revises: 0014
Create Date: 2025-09-19 02:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0015'
down_revision = '0014'
branch_labels = None
depends_on = None


def upgrade():
    # add unique constraint on persons.email (only safe if no duplicates)
    op.create_unique_constraint('uq_persons_email', 'persons', ['email'])


def downgrade():
    op.drop_constraint('uq_persons_email', 'persons', type_='unique')
