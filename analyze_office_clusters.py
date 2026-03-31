import pandas as pd
from sqlalchemy import create_engine
import re

engine = create_engine('postgresql://postgres:postgres@localhost:5432/hr_analytics')

# Your provided list
your_list = [
    '026400.Cluster Office - KPK',
    '027412.Cluster Office - Central Punjab',
    '026300.Cluster Office - Southern Punjab',
    '025113.Cluster Office - Internal Controls - North',
    '025111.Cluster Office - Internal Controls - Northern Punjab',
    '025112.Cluster Office - Internal Controls - Southern Punjab',
    '025114.Cluster Office - Internal Controls - South',
    '026200.Cluster Office - Northern Punjab',
    '025060.Cluster Office - North',
    '024000.Cluster Rural Office - South',
    '0510000.Cluster Islamic Trade Karachi',
    '037960.Cluster Trade Business Office - Southern Punjab',
    '0510003.Cluster Islamic Trade Northern Punjab',
    '0510001.Cluster Islamic Trade KPK',
    '037959.Cluster Trade Business Office - North',
    '0510005.Cluster Islamic Trade Southern punjab',
    '0510002.Cluster Islamic Trade North',
    '0510004.Cluster Islamic Trade Quetta',
]

def current_normalize(c):
    c = str(c)
    c = re.sub(r'^\d+\.\s*', '', c)
    c = re.sub(r'(?i)\s*-\s*(Ops|Sales|Operations)$', '', c)
    c = re.sub(r'(?i)^UBL Ameen Cluster\s+(Sales|Operations)\s+Office\s*-\s*', 'UBL Ameen Cluster ', c)
    c = re.sub(r'(?i)^Cluster\s+(Sales|Operations)\s+Office\s*-\s*', 'Cluster ', c)
    c = re.sub(r'(?i)^Cluster\s+Office\s*-\s*', 'Cluster ', c)
    return c.strip()

def enhanced_normalize(c):
    c = str(c)
    # Step 1: Remove numeric prefix
    c = re.sub(r'^\d+\.\s*', '', c)
    # Step 2: Remove Ops/Sales/Operations suffixes
    c = re.sub(r'(?i)\s*-\s*(Ops|Sales|Operations)$', '', c)
    # Step 3: Unify UBL Ameen patterns
    c = re.sub(r'(?i)^UBL Ameen Cluster\s+(Sales|Operations)\s+Office\s*-\s*', 'UBL Ameen Cluster ', c)
    # Step 4: General Sales/Operations Office pattern
    c = re.sub(r'(?i)^Cluster\s+(Sales|Operations)\s+Office\s*-\s*', 'Cluster ', c)
    # Step 5: Remove "Cluster Office - " prefix
    c = re.sub(r'(?i)^Cluster\s+Office\s*-\s*', 'Cluster ', c)
    # Step 6: Remove "Rural Office - " and "Trade Business Office - "
    c = re.sub(r'(?i)^Cluster\s+Rural\s+Office\s*-\s*', 'Cluster Rural ', c)
    c = re.sub(r'(?i)^Cluster\s+Trade\s+Business\s+Office\s*-\s*', 'Cluster Trade Business ', c)
    return c.strip()

print('Your filtered list normalized:\n')
for item in your_list:
    current = current_normalize(item)
    enhanced = enhanced_normalize(item)
    if current != enhanced:
        print(f'{item}')
        print(f'  Current:  {current}')
        print(f'  Enhanced: {enhanced}')
        print()
