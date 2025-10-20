"""NO-OP: persons already exist in baseline; keep linear history

Revision ID: 0013
Revises: 0012
Create Date: 2025-09-19 01:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer

revision = '0013'
down_revision = '0012'
branch_labels = None
depends_on = None


def upgrade():
    # No-op: el esquema actual ya incluye persons y users.person_id desde el baseline
    pass


def downgrade():
    # No-op
    pass
