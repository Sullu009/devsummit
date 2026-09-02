"""initial users table

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
user_role=postgresql.ENUM("ATTENDEE","ORGANIZER","ADMIN",name="user_role",create_type=False)
def upgrade():
    bind=op.get_bind(); user_role.create(bind,checkfirst=True)
    op.create_table("users",sa.Column("id",sa.String(36),primary_key=True),sa.Column("email",sa.String(255),nullable=False,unique=True),sa.Column("full_name",sa.String(255),nullable=False),sa.Column("password_hash",sa.String(255),nullable=False),sa.Column("role",user_role,nullable=False,server_default="ATTENDEE"),sa.Column("phone",sa.String(32),nullable=True),sa.Column("is_active",sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_users_email","users",["email"],unique=True)
def downgrade():
    op.drop_index("ix_users_email",table_name="users"); op.drop_table("users"); user_role.drop(op.get_bind(),checkfirst=True)
