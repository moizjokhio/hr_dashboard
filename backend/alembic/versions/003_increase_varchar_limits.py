"""Increase VARCHAR limits

Revision ID: 003
Revises: 002
Create Date: 2025-12-15 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Widen employees columns to accommodate real ODBC data
    op.alter_column('employees', 'employee_id',  existing_type=sa.String(20),  type_=sa.String(50),  existing_nullable=False)
    op.alter_column('employees', 'full_name',    existing_type=sa.String(200), type_=sa.String(500), existing_nullable=False)
    op.alter_column('employees', 'department',   existing_type=sa.String(100), type_=sa.String(500), existing_nullable=False)
    op.alter_column('employees', 'grade_level',  existing_type=sa.String(20),  type_=sa.String(100), existing_nullable=False)
    op.alter_column('employees', 'designation',  existing_type=sa.String(200), type_=sa.String(500), existing_nullable=True)
    op.alter_column('employees', 'status',       existing_type=sa.String(30),  type_=sa.String(200), existing_nullable=True)
    op.alter_column('employees', 'branch_city',  existing_type=sa.String(100), type_=sa.String(500), existing_nullable=True)
    op.alter_column('employees', 'email',        existing_type=sa.String(200), type_=sa.String(500), existing_nullable=True)


def downgrade() -> None:
    op.alter_column('employees', 'employee_id',  existing_type=sa.String(50),  type_=sa.String(20),  existing_nullable=False)
    op.alter_column('employees', 'full_name',    existing_type=sa.String(500), type_=sa.String(200), existing_nullable=False)
    op.alter_column('employees', 'department',   existing_type=sa.String(500), type_=sa.String(100), existing_nullable=False)
    op.alter_column('employees', 'grade_level',  existing_type=sa.String(100), type_=sa.String(20),  existing_nullable=False)
    op.alter_column('employees', 'designation',  existing_type=sa.String(500), type_=sa.String(200), existing_nullable=True)
    op.alter_column('employees', 'status',       existing_type=sa.String(200), type_=sa.String(30),  existing_nullable=True)
    op.alter_column('employees', 'branch_city',  existing_type=sa.String(500), type_=sa.String(100), existing_nullable=True)
    op.alter_column('employees', 'email',        existing_type=sa.String(500), type_=sa.String(200), existing_nullable=True)
