"""job fetch timestamps and board identity

Revision ID: 0003_job_fetch_schedule
Revises: 0002_jobs
Create Date: 2026-08-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_job_fetch_schedule"
down_revision: str | None = "0002_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("job_sources", sa.Column("external_key", sa.String(length=128), nullable=True))
    op.add_column(
        "job_sources",
        sa.Column("current_fetch_datetime", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "job_sources",
        sa.Column("last_fetch_datetime", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_job_sources_external_key", "job_sources", ["external_key"])
    op.create_unique_constraint(
        "uq_job_sources_type_external_key",
        "job_sources",
        ["source_type", "external_key"],
    )

    op.create_table(
        "job_fetch_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_fetch_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_fetch_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="running"),
        sa.Column("boards_attempted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("boards_succeeded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fetched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicates", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "errors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_job_fetch_runs_current_fetch_datetime",
        "job_fetch_runs",
        ["current_fetch_datetime"],
    )


def downgrade() -> None:
    op.drop_index("ix_job_fetch_runs_current_fetch_datetime", table_name="job_fetch_runs")
    op.drop_table("job_fetch_runs")
    op.drop_constraint("uq_job_sources_type_external_key", "job_sources", type_="unique")
    op.drop_index("ix_job_sources_external_key", table_name="job_sources")
    op.drop_column("job_sources", "last_fetch_datetime")
    op.drop_column("job_sources", "current_fetch_datetime")
    op.drop_column("job_sources", "external_key")
