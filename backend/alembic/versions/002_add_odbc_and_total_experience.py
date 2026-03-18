"""Add ODBC and total_experience tables

Revision ID: 002
Revises: 001
Create Date: 2025-12-07 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "odbc",
        sa.Column("EMPLOYEE_NUMBER", sa.String(50), nullable=False),
        sa.Column("ASSIGNMENT_NUMBER", sa.String(50), nullable=True),
        sa.Column("TITLE", sa.String(100), nullable=True),
        sa.Column("EMPLOYEE_FULL_NAME", sa.String(200), nullable=True),
        sa.Column("GENDER", sa.String(20), nullable=True),
        sa.Column("DATE_OF_BIRTH", sa.Date(), nullable=True),
        sa.Column("FATHER_NAME", sa.String(200), nullable=True),
        sa.Column("NATIONALITY", sa.String(100), nullable=True),
        sa.Column("CNIC_NATIONAL_ID", sa.String(100), nullable=True),
        sa.Column("DATE_OF_JOIN", sa.Date(), nullable=True),
        sa.Column("PHONE_TYPE", sa.String(50), nullable=True),
        sa.Column("CONTACT_NUMBER", sa.String(100), nullable=True),
        sa.Column("EMAIL_TYPE", sa.String(50), nullable=True),
        sa.Column("EMAIL_ADDRESS", sa.String(200), nullable=True),
        sa.Column("ADDRESS_TYPE", sa.String(50), nullable=True),
        sa.Column("HOME_ADDRESS", sa.Text(), nullable=True),
        sa.Column("BLOOD_GROUP", sa.String(20), nullable=True),
        sa.Column("RELIGION", sa.String(50), nullable=True),
        sa.Column("ACTION_CODE", sa.String(100), nullable=True),
        sa.Column("ASSIGNMENT_START_DATE", sa.Date(), nullable=True),
        sa.Column("ASSIGNMENT_END_DATE", sa.Date(), nullable=True),
        sa.Column("ASSIGNMENT_CATEGORY", sa.String(100), nullable=True),
        sa.Column("DATE_PROBATION_END", sa.Date(), nullable=True),
        sa.Column("PROBATION_DURATION", sa.String(50), nullable=True),
        sa.Column("CONFIRMED_DATE", sa.Date(), nullable=True),
        sa.Column("DEPARTMENT_NAME", sa.String(200), nullable=True),
        sa.Column("DEPARTMENT_TYPE", sa.String(100), nullable=True),
        sa.Column("POSITION_CODE", sa.String(100), nullable=True),
        sa.Column("POSITION_NAME", sa.String(200), nullable=True),
        sa.Column("CADRE", sa.String(100), nullable=True),
        sa.Column("GRADE", sa.String(50), nullable=True),
        sa.Column("LOCATION_NAME", sa.String(200), nullable=True),
        sa.Column("JOB_NAME", sa.String(200), nullable=True),
        sa.Column("CONTRACT_TYPE", sa.String(100), nullable=True),
        sa.Column("DEPT_GROUP", sa.String(100), nullable=True),
        sa.Column("SUB_GROUP", sa.String(100), nullable=True),
        sa.Column("DIVISION", sa.String(100), nullable=True),
        sa.Column("CLUSTERS", sa.String(100), nullable=True),
        sa.Column("REGION", sa.String(100), nullable=True),
        sa.Column("DISTRICT", sa.String(100), nullable=True),
        sa.Column("BRANCH", sa.String(100), nullable=True),
        sa.Column("BRANCH_LEVEL", sa.String(50), nullable=True),
        sa.Column("BRANCH_FLAGSHIP", sa.String(50), nullable=True),
        sa.Column("EMPLOYMENT_STATUS", sa.String(100), nullable=True),
        sa.Column("MANAGER_EMP_NAME", sa.String(200), nullable=True),
        sa.Column("MANAGER_EMP_NO", sa.String(100), nullable=True),
        sa.Column("DATE_OF_DEATH", sa.Date(), nullable=True),
        sa.Column("MARITAL_STATUS", sa.String(100), nullable=True),
        sa.Column("LAST_WORKING_DATE", sa.Date(), nullable=True),
        sa.Column("ACTUAL_TERMINATION_DATE", sa.Date(), nullable=True),
        sa.Column("ACTION_REASON", sa.String(200), nullable=True),
        sa.Column("NOTIFIED_TERMINATION_DATE", sa.Date(), nullable=True),
        sa.Column("PROJECTED_TERMINATION_DATE", sa.Date(), nullable=True),
        sa.Column("NOTICE_PERIOD", sa.String(50), nullable=True),
        sa.Column("GROSS_SALARY", sa.Numeric(18, 2), nullable=True),
        sa.Column("FESTIVAL_FLAG", sa.String(10), nullable=True),
        sa.Column("GRATUITY", sa.String(10), nullable=True),
        sa.Column("SPI_FLAG", sa.String(10), nullable=True),
        sa.Column("PF_CONVERTED", sa.String(10), nullable=True),
        sa.Column("PF_CON_DATE", sa.Date(), nullable=True),
        sa.Column("PF", sa.String(10), nullable=True),
        sa.Column("PF_AMEEN", sa.String(10), nullable=True),
        sa.Column("GPF", sa.String(10), nullable=True),
        sa.Column("PENSION", sa.String(10), nullable=True),
        sa.Column("COMP_ABS", sa.String(10), nullable=True),
        sa.Column("POST_RET_MED", sa.String(10), nullable=True),
        sa.Column("BF", sa.String(10), nullable=True),
        sa.Column("REL_ALL", sa.String(10), nullable=True),
        sa.Column("UNION_MEM", sa.String(10), nullable=True),
        sa.Column("EXTG_FUEL_ENTIT_OR_BMC", sa.String(50), nullable=True),
        sa.Column("CANCEL_WORKRELSHIP_FLAG", sa.String(10), nullable=True),
        sa.Column("CANCEL_WORK_RELATIONSHIP_DATE", sa.Date(), nullable=True),
        sa.Column("CONTRACT_END_DATE", sa.Date(), nullable=True),
        sa.Column("PERSON_TYPE", sa.String(100), nullable=True),
        sa.Column("CRC", sa.String(50), nullable=True),
        sa.Column("EXPENSE_POP", sa.String(50), nullable=True),
        sa.Column("LEAVE_FLAG", sa.String(10), nullable=True),
        sa.Column("SEQ", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("EMPLOYEE_NUMBER")
    )

    op.create_table(
        "total_experience",
        sa.Column("EMPLOYEE_NUMBER", sa.String(50), nullable=False),
        sa.Column("TITLE", sa.String(100), nullable=True),
        sa.Column("FULL_NAME", sa.String(200), nullable=True),
        sa.Column("Grade", sa.String(50), nullable=True),
        sa.Column("Hiring_date", sa.Date(), nullable=True),
        sa.Column("USER_STATUS", sa.String(100), nullable=True),
        sa.Column("Total_Experience", sa.String(50), nullable=True),
        sa.Column("Previous_Employer", sa.String(200), nullable=True),
        sa.Column("Postion", sa.String(200), nullable=True),
        sa.PrimaryKeyConstraint("EMPLOYEE_NUMBER")
    )


def downgrade() -> None:
    op.drop_table("total_experience")
    op.drop_table("odbc")
