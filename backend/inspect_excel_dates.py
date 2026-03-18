"""
Quick script to inspect date formats in the Excel file
"""
import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Usage: python inspect_excel_dates.py <path-to-excel-file>")
    sys.exit(1)

file_path = sys.argv[1]

# Read Excel
print(f"Reading {file_path}...")
df = pd.read_excel(file_path, dtype=str, engine="openpyxl")

# Normalize column names
df.columns = [str(c).strip().upper() for c in df.columns]

# Date columns to inspect
date_cols = ["DATE_OF_BIRTH", "DATE_OF_JOIN", "ASSIGNMENT_START_DATE"]

for col in date_cols:
    if col in df.columns:
        print(f"\n{col}:")
        # Get first 10 non-null values
        non_null = df[col].dropna()
        non_null = non_null[non_null.str.upper() != 'NAN'][:10]
        
        if len(non_null) > 0:
            print(f"  Sample values:")
            for val in non_null:
                print(f"    - {val}")
        else:
            print("  All values are null/empty")
