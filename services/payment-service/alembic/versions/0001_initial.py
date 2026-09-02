"""initial payments table

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
payment_status=postgresql.ENUM("CREATED","SUCCEEDED","FAILED","REFUNDED",name="payment_status",create_type=False)
def upgrade():
    bind=op.get_bind(); payment_status.create(bind,checkfirst=True)
    op.create_table("payments",sa.Column("id",sa.String(36),primary_key=True),sa.Column("booking_id",sa.String(36),nullable=False),sa.Column("user_id",sa.String(36),nullable=False),sa.Column("organizer_id",sa.String(36),nullable=False),sa.Column("event_id",sa.String(36),nullable=False),sa.Column("razorpay_order_id",sa.String(64),nullable=False),sa.Column("razorpay_payment_id",sa.String(64),nullable=True),sa.Column("razorpay_signature",sa.String(256),nullable=True),sa.Column("amount",sa.Numeric(10,2),nullable=False),sa.Column("currency",sa.String(8),nullable=False,server_default="INR"),sa.Column("status",payment_status,nullable=False,server_default="CREATED"),sa.Column("failure_reason",sa.String(512),nullable=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_payments_booking_id","payments",["booking_id"],unique=True); op.create_index("ix_payments_user_id","payments",["user_id"]); op.create_index("ix_payments_organizer_id","payments",["organizer_id"]); op.create_index("ix_payments_event_id","payments",["event_id"]); op.create_index("ix_payments_razorpay_order_id","payments",["razorpay_order_id"],unique=True); op.create_index("ix_payments_razorpay_payment_id","payments",["razorpay_payment_id"],unique=True)
def downgrade():
    op.drop_table("payments"); payment_status.drop(op.get_bind(),checkfirst=True)
