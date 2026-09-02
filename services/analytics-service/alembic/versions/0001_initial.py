"""initial event_stats table

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_stats",
        sa.Column("event_id", sa.String(36), primary_key=True),
        sa.Column("organizer_id", sa.String(36), nullable=False, server_default=""),
        sa.Column("views", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bookings_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bookings_confirmed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bookings_cancelled", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tickets_sold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("refunds_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("refunds_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("attendance_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_event_stats_organizer_id", "event_stats", ["organizer_id"])

    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.String(64), primary_key=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("processed_events")
    op.drop_index("ix_event_stats_organizer_id", table_name="event_stats")
    op.drop_table("event_stats")
