"""initial events, ticket_types, availability_adjustments

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0001"; down_revision=None; branch_labels=None; depends_on=None
event_status=postgresql.ENUM("DRAFT","PUBLISHED","CANCELLED",name="event_status",create_type=False)
event_category=postgresql.ENUM("MUSIC","TECH","BUSINESS","ARTS","SPORTS","FOOD","COMMUNITY","OTHER",name="event_category",create_type=False)
def upgrade():
    bind=op.get_bind(); event_status.create(bind,checkfirst=True); event_category.create(bind,checkfirst=True)
    op.create_table("events",sa.Column("id",sa.String(36),primary_key=True),sa.Column("organizer_id",sa.String(36),nullable=False),sa.Column("title",sa.String(255),nullable=False),sa.Column("slug",sa.String(280),nullable=False),sa.Column("description",sa.Text(),nullable=False,server_default=""),sa.Column("category",event_category,nullable=False,server_default="OTHER"),sa.Column("status",event_status,nullable=False,server_default="DRAFT"),sa.Column("cover_image_url",sa.String(1024),nullable=True),sa.Column("venue_name",sa.String(255),nullable=False,server_default=""),sa.Column("venue_address",sa.String(512),nullable=False,server_default=""),sa.Column("city",sa.String(120),nullable=False,server_default=""),sa.Column("starts_at",sa.DateTime(timezone=True),nullable=False),sa.Column("ends_at",sa.DateTime(timezone=True),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_events_organizer_id","events",["organizer_id"]); op.create_index("ix_events_slug","events",["slug"],unique=True); op.create_index("ix_events_city","events",["city"])
    op.create_table("ticket_types",sa.Column("id",sa.String(36),primary_key=True),sa.Column("event_id",sa.String(36),sa.ForeignKey("events.id",ondelete="CASCADE"),nullable=False),sa.Column("name",sa.String(120),nullable=False),sa.Column("description",sa.String(512),nullable=False,server_default=""),sa.Column("price",sa.Numeric(10,2),nullable=False),sa.Column("quantity_total",sa.Integer(),nullable=False),sa.Column("quantity_available",sa.Integer(),nullable=False),sa.Column("sale_starts_at",sa.DateTime(timezone=True),nullable=False),sa.Column("sale_ends_at",sa.DateTime(timezone=True),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_ticket_types_event_id","ticket_types",["event_id"])
    op.create_table("availability_adjustments",sa.Column("idempotency_key",sa.String(120),primary_key=True),sa.Column("ticket_type_id",sa.String(36),nullable=False),sa.Column("quantity",sa.Integer(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_index("ix_availability_adjustments_ticket_type_id","availability_adjustments",["ticket_type_id"])
def downgrade():
    op.drop_table("availability_adjustments"); op.drop_index("ix_ticket_types_event_id",table_name="ticket_types"); op.drop_table("ticket_types"); op.drop_index("ix_events_city",table_name="events"); op.drop_index("ix_events_slug",table_name="events"); op.drop_index("ix_events_organizer_id",table_name="events"); op.drop_table("events"); event_category.drop(op.get_bind(),checkfirst=True); event_status.drop(op.get_bind(),checkfirst=True)
