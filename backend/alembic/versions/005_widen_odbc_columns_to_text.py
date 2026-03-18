"""Widen all odbc string columns to TEXT to prevent truncation errors

Revision ID: 005
Revises: 004
Create Date: 2026-03-04 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All VARCHAR columns in the odbc table that need to be TEXT
ODBC_TEXT_COLS = [
    "EMPLOYEE_NUMBER", "ASSIGNMENT_NUMBER", "TITLE", "EMPLOYEE_FULL_NAME",
    "GENDER", "FATHER_NAME", "NATIONALITY", "CNIC_NATIONAL_ID", "PHONE_TYPE",
    "CONTACT_NUMBER", "EMAIL_TYPE", "EMAIL_ADDRESS", "ADDRESS_TYPE",
    "BLOOD_GROUP", "RELIGION", "ACTION_CODE", "ASSIGNMENT_CATEGORY",
    "PROBATION_DURATION", "DEPARTMENT_NAME", "DEPARTMENT_TYPE", "POSITION_CODE",
    "POSITION_NAME", "CADRE", "GRADE", "LOCATION_NAME", "JOB_NAME",
    "CONTRACT_TYPE", "DEPT_GROUP", "SUB_GROUP", "DIVISION", "CLUSTERS",
    "REGION", "DISTRICT", "BRANCH", "BRANCH_LEVEL", "BRANCH_FLAGSHIP",
    "EMPLOYMENT_STATUS", "MANAGER_EMP_NAME", "MANAGER_EMP_NO", "MARITAL_STATUS",
    "ACTION_REASON", "NOTICE_PERIOD", "FESTIVAL_FLAG", "GRATUITY", "SPI_FLAG",
    "PF_CONVERTED", "PF", "PF_AMEEN", "GPF", "PENSION", "COMP_ABS",
    "POST_RET_MED", "BF", "REL_ALL", "UNION_MEM", "EXTG_FUEL_ENTIT_OR_BMC",
    "CANCEL_WORKRELSHIP_FLAG", "PERSON_TYPE", "CRC", "EXPENSE_POP", "LEAVE_FLAG",
]


def upgrade() -> None:
    for col in ODBC_TEXT_COLS:
        op.alter_column(
            "odbc", col,
            existing_type=sa.String(),
            type_=sa.Text(),
            existing_nullable=True,
        )


def downgrade() -> None:
    pass  # no need to shrink back
