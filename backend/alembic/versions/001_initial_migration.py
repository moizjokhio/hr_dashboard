"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.String(20), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('department', sa.String(100), nullable=False),
        sa.Column('unit_name', sa.String(100), nullable=True),
        sa.Column('grade_level', sa.String(20), nullable=False),
        sa.Column('designation', sa.String(200), nullable=True),
        sa.Column('employment_type', sa.String(50), nullable=True),
        sa.Column('branch_city', sa.String(100), nullable=True),
        sa.Column('branch_country', sa.String(100), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('date_of_joining', sa.Date(), nullable=True),
        sa.Column('years_of_experience', sa.Float(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('marital_status', sa.String(30), nullable=True),
        sa.Column('religion', sa.String(50), nullable=True),
        sa.Column('education_level', sa.String(100), nullable=True),
        sa.Column('disability_status', sa.String(50), nullable=True),
        sa.Column('basic_salary', sa.Float(), nullable=True),
        sa.Column('housing_allowance', sa.Float(), nullable=True),
        sa.Column('transport_allowance', sa.Float(), nullable=True),
        sa.Column('other_allowances', sa.Float(), nullable=True),
        sa.Column('total_monthly_salary', sa.Float(), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.Column('reporting_manager_id', sa.String(20), nullable=True),
        sa.Column('status', sa.String(30), nullable=True, server_default='Active'),
        sa.Column('email', sa.String(200), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id')
    )
    
    # Create indexes for employees
    op.create_index('ix_employees_employee_id', 'employees', ['employee_id'])
    op.create_index('ix_employees_department', 'employees', ['department'])
    op.create_index('ix_employees_grade_level', 'employees', ['grade_level'])
    op.create_index('ix_employees_branch_country', 'employees', ['branch_country'])
    op.create_index('ix_employees_status', 'employees', ['status'])
    op.create_index('ix_employees_performance_score', 'employees', ['performance_score'])
    op.create_index('ix_employees_reporting_manager_id', 'employees', ['reporting_manager_id'])
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('permissions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(200), nullable=False),
        sa.Column('hashed_password', sa.String(200), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('employee_id', sa.String(20), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='unique_user_role')
    )
    
    # Create dashboard_snapshots table
    op.create_table(
        'dashboard_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('dashboard_type', sa.String(50), nullable=False),
        sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_dashboard_snapshots_date', 'dashboard_snapshots', ['snapshot_date'])
    op.create_index('ix_dashboard_snapshots_type', 'dashboard_snapshots', ['dashboard_type'])
    
    # Create prediction_results table
    op.create_table(
        'prediction_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.String(20), nullable=False),
        sa.Column('prediction_type', sa.String(50), nullable=False),
        sa.Column('prediction_score', sa.Float(), nullable=False),
        sa.Column('risk_category', sa.String(20), nullable=True),
        sa.Column('shap_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('top_factors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=True),
        sa.Column('prediction_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_prediction_results_employee_id', 'prediction_results', ['employee_id'])
    op.create_index('ix_prediction_results_type', 'prediction_results', ['prediction_type'])
    op.create_index('ix_prediction_results_date', 'prediction_results', ['prediction_date'])
    
    # Create analytics_queries table
    op.create_table(
        'analytics_queries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('natural_language_query', sa.Text(), nullable=False),
        sa.Column('generated_sql', sa.Text(), nullable=True),
        sa.Column('query_intent', sa.String(50), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('feedback_rating', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_analytics_queries_user_id', 'analytics_queries', ['user_id'])
    op.create_index('ix_analytics_queries_created_at', 'analytics_queries', ['created_at'])
    
    # Insert default roles
    op.execute("""
        INSERT INTO roles (name, description, permissions) VALUES
        ('admin', 'Full system access', '{"all": true}'),
        ('hr_manager', 'HR management access', '{"employees": true, "analytics": true, "reports": true}'),
        ('analyst', 'Analytics and reports access', '{"analytics": true, "reports": true}'),
        ('viewer', 'Read-only access', '{"employees": "read", "analytics": "read"}')
    """)


def downgrade() -> None:
    op.drop_table('analytics_queries')
    op.drop_table('prediction_results')
    op.drop_table('dashboard_snapshots')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('employees')
