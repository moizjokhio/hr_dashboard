-- PostgreSQL initialization script for HR Analytics System

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hr_analytics TO postgres;

-- Create indexes for full-text search (will be applied after tables are created by Alembic)
-- CREATE INDEX IF NOT EXISTS idx_employees_fulltext ON employees USING gin(to_tsvector('english', full_name || ' ' || COALESCE(designation, '') || ' ' || department));
