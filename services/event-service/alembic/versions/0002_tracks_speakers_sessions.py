"""tracks, speakers, sessions

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-07 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # Tracks table
    op.create_table(
        "tracks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(512), nullable=False, server_default=""),
        sa.Column("room_location", sa.String(120), nullable=False, server_default=""),
        sa.Column("color_code", sa.String(30), nullable=False, server_default="#6366F1"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_tracks_event_id", "tracks", ["event_id"])

    # Speakers table
    op.create_table(
        "speakers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("role_title", sa.String(120), nullable=False, server_default=""),
        sa.Column("company", sa.String(120), nullable=False, server_default=""),
        sa.Column("bio", sa.Text(), nullable=False, server_default=""),
        sa.Column("avatar_url", sa.String(1024), nullable=False, server_default=""),
        sa.Column("github_url", sa.String(255), nullable=True),
        sa.Column("twitter_url", sa.String(255), nullable=True),
        sa.Column("linkedin_url", sa.String(255), nullable=True),
    )
    op.create_index("ix_speakers_event_id", "speakers", ["event_id"])

    # Sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("track_id", sa.String(36), sa.ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("speaker_id", sa.String(36), sa.ForeignKey("speakers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=False, server_default=""),
        sa.Column("session_type", sa.String(50), nullable=False, server_default="TALK"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("slides_url", sa.String(1024), nullable=True),
    )
    op.create_index("ix_sessions_event_id", "sessions", ["event_id"])
    op.create_index("ix_sessions_track_id", "sessions", ["track_id"])
    op.create_index("ix_sessions_speaker_id", "sessions", ["speaker_id"])


def downgrade():
    op.drop_index("ix_sessions_speaker_id", table_name="sessions")
    op.drop_index("ix_sessions_track_id", table_name="sessions")
    op.drop_index("ix_sessions_event_id", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("ix_speakers_event_id", table_name="speakers")
    op.drop_table("speakers")

    op.drop_index("ix_tracks_event_id", table_name="tracks")
    op.drop_table("tracks")
