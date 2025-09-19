"""create persons table and migrate user names

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
    conn = op.get_bind()
    # 1) create persons table
    op.create_table(
        'persons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('first_name', sa.String(length=80), nullable=True),
        sa.Column('last_name', sa.String(length=80), nullable=True),
        sa.Column('document_number', sa.String(length=40), nullable=True),
        sa.Column('phone', sa.String(length=40), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
    )

    # 2) add person_id column to users (nullable for now)
    op.add_column('users', sa.Column('person_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_person', 'users', 'persons', ['person_id'], ['id'])

    # 3) migrate data: for each user create a person and set person_id
    users_tbl = table('users', column('id', Integer), column('first_name', String), column('last_name', String), column('email', String))
    persons_tbl = table('persons', column('id', Integer), column('first_name', String), column('last_name', String), column('email', String))

    res = conn.execute(sa.text('SELECT id, first_name, last_name, email FROM users'))
    rows = res.fetchall()
    for r in rows:
        uid, fn, ln, email = r
        # Insert person
        ins = sa.text("INSERT INTO persons (first_name, last_name, email) VALUES (:fn, :ln, :email) RETURNING id")
        pid = conn.execute(ins, {'fn': fn, 'ln': ln, 'email': email}).scalar()
        # update user
        conn.execute(sa.text('UPDATE users SET person_id=:pid WHERE id=:uid'), {'pid': pid, 'uid': uid})

    # 4) drop first_name and last_name from users
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')


def downgrade():
    # reverse: add columns back, copy data, drop persons
    op.add_column('users', sa.Column('first_name', sa.String(length=80), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=80), nullable=True))
    conn = op.get_bind()
    res = conn.execute(sa.text('SELECT id, person_id FROM users'))
    for uid, pid in res.fetchall():
        if pid is None:
            continue
        p = conn.execute(sa.text('SELECT first_name, last_name FROM persons WHERE id=:pid'), {'pid': pid}).fetchone()
        if p:
            conn.execute(sa.text('UPDATE users SET first_name=:fn, last_name=:ln WHERE id=:uid'), {'fn': p[0], 'ln': p[1], 'uid': uid})
    op.drop_constraint('fk_users_person', 'users', type_='foreignkey')
    op.drop_column('users', 'person_id')
    op.drop_table('persons')
