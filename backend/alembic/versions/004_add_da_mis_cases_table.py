"""Add DA MIS Cases table

Revision ID: 004
Revises: 003
Create Date: 2025-12-22 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "da_mis_cases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("case_number", sa.String(100), nullable=False, index=True, comment="Case #"),
        sa.Column("s_number", sa.String(100), nullable=True, comment="S #"),
        sa.Column("emp_number", sa.String(100), nullable=True, index=True, comment="Emp. #"),
        sa.Column("name_of_staff_reported", sa.Text(), nullable=True, comment="Name of Staff Reported"),
        sa.Column("grade", sa.String(50), nullable=True, comment="Grade"),
        sa.Column("ft", sa.String(50), nullable=True, comment="FT"),
        sa.Column("branch_office", sa.String(200), nullable=True, comment="Branch / Office"),
        sa.Column("region", sa.String(100), nullable=True, comment="Region"),
        sa.Column("cluster", sa.String(100), nullable=True, comment="Cluster"),
        sa.Column("fixation_of_responsibility", sa.Text(), nullable=True, comment="Fixation of Responsibility"),
        sa.Column("misconduct", sa.Text(), nullable=True, comment="Misconduct"),
        sa.Column("misconduct_category", sa.String(200), nullable=True, comment="Misconduct Category"),
        sa.Column("case_revieved", sa.String(200), nullable=True, comment="Case Revieved"),
        sa.Column("case_received_from_audit", sa.String(200), nullable=True, comment="Case Received from Audit"),
        sa.Column("charge_sheeted_date", sa.Date(), nullable=True, comment="Charge Sheeted Date"),
        sa.Column("dac_decision", sa.String(200), nullable=True, comment="DAC Decision"),
        sa.Column("punishment_implementation", sa.String(200), nullable=True, comment="Punishment Implementation"),
        sa.Column("punishment_letter", sa.String(200), nullable=True, comment="Punishment Letter"),
        sa.Column("year", sa.Integer(), nullable=True, comment="Year"),
        sa.Column("quarter", sa.String(10), nullable=True, comment="Quarter"),
        sa.Column("month", sa.String(20), nullable=True, comment="Month"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for filtering
    op.create_index("idx_da_mis_cases_year", "da_mis_cases", ["year"])
    op.create_index("idx_da_mis_cases_cluster", "da_mis_cases", ["cluster"])
    op.create_index("idx_da_mis_cases_region", "da_mis_cases", ["region"])
    op.create_index("idx_da_mis_cases_grade", "da_mis_cases", ["grade"])
    op.create_index("idx_da_mis_cases_misconduct_category", "da_mis_cases", ["misconduct_category"])
    op.create_index("idx_da_mis_cases_dac_decision", "da_mis_cases", ["dac_decision"])


def downgrade() -> None:
    op.drop_index("idx_da_mis_cases_dac_decision", "da_mis_cases")
    op.drop_index("idx_da_mis_cases_misconduct_category", "da_mis_cases")
    op.drop_index("idx_da_mis_cases_grade", "da_mis_cases")
    op.drop_index("idx_da_mis_cases_region", "da_mis_cases")
    op.drop_index("idx_da_mis_cases_cluster", "da_mis_cases")
    op.drop_index("idx_da_mis_cases_year", "da_mis_cases")
    op.drop_table("da_mis_cases")
