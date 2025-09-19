"""baseline schema

Revision ID: 0001
Revises: 
Create Date: 2025-09-09 13:03:22.374902

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Crear todas las tablas del modelo
    from app.models import Base
    bind = op.get_bind()
    Base.metadata.create_all(bind)


def downgrade() -> None:
    """Downgrade baseline — nothing to undo."""
    pass