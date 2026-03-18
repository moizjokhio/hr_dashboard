import psycopg2

conn = psycopg2.connect('postgresql://hr_admin:zbfXZpBPyxgEYEVm@localhost:5432/hr_analytics')
cur = conn.cursor()

queries = [
    ('EMPLOYMENT_STATUS', 'SELECT DISTINCT "EMPLOYMENT_STATUS" FROM odbc LIMIT 20'),
    ('ASSIGNMENT_CATEGORY', 'SELECT DISTINCT "ASSIGNMENT_CATEGORY" FROM odbc LIMIT 20'),
    ('CONTRACT_TYPE', 'SELECT DISTINCT "CONTRACT_TYPE" FROM odbc LIMIT 20'),
    ('ACTION_REASON', 'SELECT DISTINCT "ACTION_REASON" FROM odbc WHERE "ACTUAL_TERMINATION_DATE" IS NOT NULL LIMIT 20'),
    ('DEPT_GROUP sample', 'SELECT DISTINCT "DEPT_GROUP" FROM odbc LIMIT 5'),
    ('LOCATION_NAME sample', 'SELECT DISTINCT "LOCATION_NAME" FROM odbc LIMIT 5'),
    ('CLUSTERS sample', 'SELECT DISTINCT "CLUSTERS" FROM odbc WHERE "CLUSTERS" IS NOT NULL LIMIT 5'),
    ('HIRE_DATE check', 'SELECT COUNT(*) FROM odbc WHERE "DATE_OF_JOIN" IS NOT NULL'),
]

for label, q in queries:
    try:
        cur.execute(q)
        print(f'{label}: {[r[0] for r in cur.fetchall()]}')
    except Exception as e:
        print(f'{label}: ERROR - {e}')
        conn.rollback()

conn.close()
