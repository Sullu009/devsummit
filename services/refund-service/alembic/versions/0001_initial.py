"""initial refunds table

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
refund_status=postgresql.ENUM("PENDING","COMPLETED","FAILED",name="refund_status",create_type=False)
def upgrade():
    bind=op.get_bind(); refund_status.create(bind,checkfirst=True)
    op.create_table("refunds",sa.Column("id",sa.String(36),primary_key=True),sa.Column("booking_id",sa.String(36),nullable=False),sa.Column("payment_id",sa.String(36),nullable=False),sa.Column("user_id",sa.String(36),nullable=False),sa.Column("amount",sa.Numeric(10,2),nullable=False),sa.Column("reason",sa.String(255),nullable=False,server_default="Attendee-requested cancellation"),sa.Column("status",refund_status,nullable=False,server_default="PENDING"),sa.Column("razorpay_refund_id",sa.String(64),nullable=True),sa.Column("failure_reason",sa.String(512),nullable=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_refunds_booking_id","refunds",["booking_id"],unique=True); op.create_index("ix_refunds_payment_id","refunds",["payment_id"]); op.create_index("ix_refunds_user_id","refunds",["user_id"])
    op.create_table("processed_events",sa.Column("event_id",sa.String(64),primary_key=True),sa.Column("processed_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
def downgrade():
    op.drop_table("processed_events"); op.drop_index("ix_refunds_user_id",table_name="refunds"); op.drop_index("ix_refunds_payment_id",table_name="refunds"); op.drop_index("ix_refunds_booking_id",table_name="refunds"); op.drop_table("refunds"); refund_status.drop(op.get_bind(),checkfirst=True)
