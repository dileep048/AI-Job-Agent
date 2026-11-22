"""extend job matches for sprint 3 matching engine

Revision ID: 0005_match_engine
Revises: 0004_job_matches
Create Date: 2026-08-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_match_engine"
down_revision: str | None = "0004_job_matches"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "job_matches",
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        """
        UPDATE job_matches jm
        SET profile_id = cp.id
        FROM candidate_profiles cp
        WHERE cp.user_id = jm.user_id
        """
    )
    op.alter_column("job_matches", "profile_id", nullable=False)
    op.create_foreign_key(
        "fk_job_matches_profile_id",
        "job_matches",
        "candidate_profiles",
        ["profile_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint("uq_job_matches_user_job", "job_matches", type_="unique")
    op.create_unique_constraint("uq_job_matches_profile_job", "job_matches", ["profile_id", "job_id"])
    op.create_index("ix_job_matches_profile_id", "job_matches", ["profile_id"])
    op.create_index("ix_job_matches_profile_score", "job_matches", ["profile_id", "overall_score"])

    for column, col_type in [
        ("title_score", sa.Numeric(5, 2)),
        ("workplace_score", sa.Numeric(5, 2)),
        ("employment_score", sa.Numeric(5, 2)),
        ("confidence", sa.Numeric(4, 2)),
    ]:
        op.add_column("job_matches", sa.Column(column, col_type, nullable=True, server_default="0"))
        op.alter_column("job_matches", column, server_default=None)

    for column in ["title_score", "workplace_score", "employment_score", "confidence"]:
        op.execute(f"UPDATE job_matches SET {column} = 0 WHERE {column} IS NULL")
        op.alter_column("job_matches", column, nullable=False)

    op.add_column("job_matches", sa.Column("strengths", postgresql.JSONB(), nullable=True))
    op.add_column("job_matches", sa.Column("concerns", postgresql.JSONB(), nullable=True))
    op.add_column("job_matches", sa.Column("candidate_evidence", postgresql.JSONB(), nullable=True))
    op.add_column("job_matches", sa.Column("structured_score", postgresql.JSONB(), nullable=True))
    op.add_column("job_matches", sa.Column("ai_reasoning", postgresql.JSONB(), nullable=True))
    op.add_column("job_matches", sa.Column("hard_filter_passed", sa.Boolean(), nullable=True))
    op.add_column("job_matches", sa.Column("hard_filter_reasons", postgresql.JSONB(), nullable=True))
    op.add_column("job_matches", sa.Column("algorithm_version", sa.String(length=32), nullable=True))
    op.add_column("job_matches", sa.Column("model_name", sa.String(length=64), nullable=True))
    op.add_column("job_matches", sa.Column("model_version", sa.String(length=64), nullable=True))

    op.execute("UPDATE job_matches SET strengths = '[]'::jsonb WHERE strengths IS NULL")
    op.execute("UPDATE job_matches SET concerns = '[]'::jsonb WHERE concerns IS NULL")
    op.execute("UPDATE job_matches SET candidate_evidence = '{}'::jsonb WHERE candidate_evidence IS NULL")
    op.execute("UPDATE job_matches SET structured_score = breakdown WHERE structured_score IS NULL")
    op.execute("UPDATE job_matches SET ai_reasoning = '{}'::jsonb WHERE ai_reasoning IS NULL")
    op.execute("UPDATE job_matches SET hard_filter_passed = true WHERE hard_filter_passed IS NULL")
    op.execute("UPDATE job_matches SET hard_filter_reasons = '[]'::jsonb WHERE hard_filter_reasons IS NULL")
    op.execute("UPDATE job_matches SET algorithm_version = 's3.0.0' WHERE algorithm_version IS NULL")

    for column in [
        "strengths",
        "concerns",
        "candidate_evidence",
        "structured_score",
        "ai_reasoning",
        "hard_filter_reasons",
        "algorithm_version",
    ]:
        op.alter_column("job_matches", column, nullable=False)
    op.alter_column("job_matches", "hard_filter_passed", nullable=False)


def downgrade() -> None:
    op.drop_index("ix_job_matches_profile_score", table_name="job_matches")
    op.drop_index("ix_job_matches_profile_id", table_name="job_matches")
    op.drop_constraint("uq_job_matches_profile_job", "job_matches", type_="unique")
    op.create_unique_constraint("uq_job_matches_user_job", "job_matches", ["user_id", "job_id"])
    op.drop_constraint("fk_job_matches_profile_id", "job_matches", type_="foreignkey")
    for column in [
        "model_version",
        "model_name",
        "algorithm_version",
        "hard_filter_reasons",
        "hard_filter_passed",
        "ai_reasoning",
        "structured_score",
        "candidate_evidence",
        "concerns",
        "strengths",
        "confidence",
        "employment_score",
        "workplace_score",
        "title_score",
        "profile_id",
    ]:
        op.drop_column("job_matches", column)
