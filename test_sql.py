import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/hr_analytics')

def run_query():
    sql = """
      SELECT 
         REGEXP_REPLACE(
           REGEXP_REPLACE(
             REGEXP_REPLACE(
               REGEXP_REPLACE(
                 REGEXP_REPLACE(
                   REGEXP_REPLACE(
                     REGEXP_REPLACE(\"CLUSTERS\", '^\d+\.', ''),
                     ' -\s*(Ops|Sales|Operations)$', '', 'i'
                   ),
                   '^(UBL Ameen Cluster|Cluster)\s+(Sales|Operations)\s+Office\s*-\s*', '\\1 ', 'i'
                 ),
                 '^Cluster\s+Office\s*-\s*', 'Cluster ', 'i'
               ),
               '^Cluster\s+Rural\s+Office\s*-\s*', 'Cluster Rural ', 'i'
             ),
             '^Cluster\s+Trade\s+Business\s+Office\s*-\s*', 'Cluster Trade Business ', 'i'
           ),
           '\s+', ' ', 'g'
         ) as name,
         COUNT(*) as value
       FROM odbc
       WHERE \"EMPLOYMENT_STATUS\" = 'Active - Payroll Eligible' AND \"CLUSTERS\" IS NOT NULL
       GROUP BY name
       ORDER BY value DESC
    """
    try:
        df = pd.read_sql(sql, engine)
        print(f'Total clusters: {len(df)}')
        print(f'\nAll clusters:')
        for idx, row in df.iterrows():
            print(f'{row["name"]} ({row["value"]})')
    except Exception as e:
        print('Error:', str(e)[:500])
run_query()
