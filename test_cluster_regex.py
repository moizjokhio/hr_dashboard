import pandas as pd
from sqlalchemy import create_engine
import re

engine = create_engine('postgresql://postgres:postgres@localhost:5432/hr_analytics')
df = pd.read_sql('SELECT \"CLUSTERS\", \"EMPLOYMENT_STATUS\" FROM odbc', engine)
clusters = df['CLUSTERS'].dropna().unique()

def normalize_cluster(c):
    if pd.isna(c): return c
    c = str(c)
    # 1. Remove prefix code and dot. E.g. '026400.'
    c = re.sub(r'^\d+\.\s*', '', c)
    # 2. General cleanup for variations of Sales/Ops at the end
    c = re.sub(r'(?i)\s*-\s*(Ops|Sales|Operations)$', '', c)
    # 3. Unify UBL Ameen Sales/Operations Office
    c = re.sub(r'(?i)^UBL Ameen Cluster\s+(Sales|Operations)\s+Office\s*-\s*', 'UBL Ameen Cluster ', c)
    # 4. Unify Standard Cluster Sales/Operations Office
    c = re.sub(r'(?i)^Cluster\s+(Sales|Operations)\s+Office\s*-\s*', 'Cluster ', c)
    # 5. Remove 'Office - ' if it appears
    c = re.sub(r'(?i)^Cluster\s+Office\s*-\s*', 'Cluster ', c)
    
    return c.strip()

df_active = df[df['EMPLOYMENT_STATUS'] == 'Active - Payroll Eligible'].copy()
df_active['norm'] = df_active['CLUSTERS'].apply(normalize_cluster)

print(f"Old approach counts:")
print(f"Distinct active clusters (unnormalized): {len(df_active['CLUSTERS'].dropna().unique())}")

# The old dashboard logic, for reference
def get_old_cluster(c):
    if pd.isna(c): return c
    return re.sub(r'^\d+\.\s*', '', str(c))

df_active['old_norm'] = df_active['CLUSTERS'].apply(get_old_cluster)
print(f"Dashboard original logic active count: {len(df_active['old_norm'].dropna().unique())}")
print(f"New normalized active count: {len(df_active['norm'].dropna().unique())}")

print('\nCheck mapping of old -> new:')
df_check = df_active[['CLUSTERS', 'old_norm', 'norm']].drop_duplicates().dropna()
df_check.sort_values(by='norm', inplace=True)
print(df_check[df_check['old_norm'] != df_check['norm']].head(30).to_string(index=False))

