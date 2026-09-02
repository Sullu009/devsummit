"""initial bookings, booking_items, idempotent_requests

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
booking_status=postgresql.ENUM("PENDING_PAYMENT","CONFIRMED","CANCELLED","EXPIRED","REFUND_PENDING","REFUNDED",name="booking_status",create_type=False)
def upgrade():
    bind=op.get_bind(); booking_status.create(bind,checkfirst=True)
    op.create_table("bookings",sa.Column("id",sa.String(36),primary_key=True),sa.Column("reservation_id",sa.String(64),nullable=False),sa.Column("user_id",sa.String(36),nullable=False),sa.Column("event_id",sa.String(36),nullable=False),sa.Column("organizer_id",sa.String(36),nullable=False),sa.Column("status",booking_status,nullable=False,server_default="PENDING_PAYMENT"),sa.Column("total_amount",sa.Numeric(10,2),nullable=False,server_default="0"),sa.Column("expires_at",sa.DateTime(timezone=True),nullable=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_bookings_reservation_id","bookings",["reservation_id"],unique=True); op.create_index("ix_bookings_user_id","bookings",["user_id"]); op.create_index("ix_bookings_event_id","bookings",["event_id"]); op.create_index("ix_bookings_organizer_id","bookings",["organizer_id"])
    op.create_table("booking_items",sa.Column("id",sa.String(36),primary_key=True),sa.Column("booking_id",sa.String(36),sa.ForeignKey("bookings.id",ondelete="CASCADE"),nullable=False),sa.Column("ticket_type_id",sa.String(36),nullable=False),sa.Column("ticket_type_name",sa.String(120),nullable=False),sa.Column("unit_price",sa.Numeric(10,2),nullable=False),sa.Column("quantity",sa.Integer(),nullable=False)); op.create_index("ix_booking_items_booking_id","booking_items",["booking_id"])
    op.create_table("idempotent_requests",sa.Column("idempotency_key",sa.String(120),primary_key=True),sa.Column("booking_id",sa.String(36),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
def downgrade():
    op.drop_table("idempotent_requests"); op.drop_index("ix_booking_items_booking_id",table_name="booking_items"); op.drop_table("booking_items"); op.drop_index("ix_bookings_organizer_id",table_name="bookings"); op.drop_index("ix_bookings_event_id",table_name="bookings"); op.drop_index("ix_bookings_user_id",table_name="bookings"); op.drop_index("ix_bookings_reservation_id",table_name="bookings"); op.drop_table("bookings"); booking_status.drop(op.get_bind(),checkfirst=True)
