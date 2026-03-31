import pandas as pd
from sqlalchemy import create_engine
import re

engine = create_engine('postgresql://postgres:postgres@localhost:5432/hr_analytics')
try:
    df_all = pd.read_sql('SELECT "CLUSTERS", "EMPLOYMENT_STATUS" FROM odbc', engine)
    
    # 1. Excel direct distinct count (all rows, no filtering, no cleaning)
    excel_all_count = len(df_all['CLUSTERS'].dropna().unique())
    print(f'Excel raw count (all rows, duplicates removed): {excel_all_count}')
    
    # 2. Active only distinct count
    df_active = df_all[df_all['EMPLOYMENT_STATUS'] == 'Active - Payroll Eligible'].copy()
    active_count = len(df_active['CLUSTERS'].dropna().unique())
    print(f'Active employees only (no normalization): {active_count}')
    
    # 3. Active + Normalized pattern
    def normalize_cluster(val):
        if pd.isna(val):
            return val
        # REGEXP_REPLACE("CLUSTERS", '^\d+\.', '')
        return re.sub(r'^\d+\.\s*', '', str(val)).strip()
        
    df_active['normalized'] = df_active['CLUSTERS'].apply(normalize_cluster)
    dashboard_count = len(df_active['normalized'].dropna().unique())
    print(f'Dashboard count (Active + Normalized): {dashboard_count}')
    
    print('\nDifferences showing normalization effect (Active only):')
    diff_df = df_active[['CLUSTERS', 'normalized']].drop_duplicates().dropna()
    print(diff_df[diff_df['CLUSTERS'] != diff_df['normalized']].head(20))

except Exception as e:
    print('Error:', e)
