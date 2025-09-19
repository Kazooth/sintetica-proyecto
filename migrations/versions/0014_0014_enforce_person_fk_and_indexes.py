"""enforce person fk and indexes

Revision ID: 0014
Revises: 0013
Create Date: 2025-09-19 01:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0014'
down_revision = '0013'
branch_labels = None
depends_on = None


def upgrade():
    # add index on persons.email
    op.create_index('ix_persons_email', 'persons', ['email'], unique=False)
    # add index on users.person_id
    op.create_index('ix_users_person_id', 'users', ['person_id'], unique=False)

    # ensure person_id is NOT NULL - only if all rows have value (we checked earlier)
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('person_id', existing_type=sa.Integer(), nullable=False)


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('person_id', existing_type=sa.Integer(), nullable=True)
    op.drop_index('ix_users_person_id', table_name='users')
    op.drop_index('ix_persons_email', table_name='persons')
