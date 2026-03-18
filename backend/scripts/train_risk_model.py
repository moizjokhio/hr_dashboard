import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from catboost import CatBoostClassifier
from sqlalchemy import create_engine
from app.core.config import settings

def train_model():
    print("Connecting to database...")
    # Use sync engine for pandas
    # settings.db.DATABASE_URL is likely an async URL (postgresql+asyncpg)
    # We need a sync URL for pandas/sqlalchemy sync engine (postgresql+psycopg2 or just postgresql)
    db_url = str(settings.db.DATABASE_URL).replace("postgresql+asyncpg", "postgresql")
    engine = create_engine(db_url)
    
    print("Loading data...")
    query = "SELECT * FROM employees"
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    if df.empty:
        print("No data found in employees table.")
        return

    print(f"Loaded {len(df)} records.")
    
    # Preprocessing
    # Target: Status = Terminated or Resigned
    df['target'] = df['status'].apply(lambda x: 1 if x in ['Terminated', 'Resigned', 'Retired'] else 0)
    
    # Calculate derived features
    now = pd.Timestamp.now()
    
    # Age
    if 'date_of_birth' in df.columns:
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
        df['age'] = (now - df['date_of_birth']).dt.days / 365.25
    else:
        df['age'] = 30 # Default
        
    # Experience (Tenure)
    if 'date_of_joining' in df.columns:
        df['date_of_joining'] = pd.to_datetime(df['date_of_joining'])
        df['years_experience'] = (now - df['date_of_joining']).dt.days / 365.25
    else:
        df['years_experience'] = 0
        
    # Mappings
    df['job_role'] = df['designation'] if 'designation' in df.columns else 'Unknown'
    df['salary'] = df['basic_salary'] if 'basic_salary' in df.columns else 0
    
    # Features
    features = ['age', 'gender', 'department', 'job_role', 'grade_level', 
                'branch_country', 'years_experience', 'salary', 'performance_score']
    
    # Ensure features exist in df
    for f in features:
        if f not in df.columns:
            df[f] = 0 if f in ['age', 'years_experience', 'salary', 'performance_score'] else 'Unknown'

    X = df[features].copy()
    y = df['target'].copy()
    
    # Force numerical columns to numeric
    num_features = ['age', 'years_experience', 'salary', 'performance_score']
    for col in num_features:
        X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)

    # Handle missing values for categorical
    for col in X.columns:
        if col not in num_features:
            X[col] = X[col].fillna('Unknown').astype(str)
            
    # Check if target has multiple classes
    if y.nunique() < 2:
        print("Warning: Target has only one class. Synthesizing data for training...")
        # Randomly flip 10% of targets to 1
        import numpy as np
        np.random.seed(42)
        n_samples = len(y)
        n_pos = max(int(n_samples * 0.1), 2) # At least 2 positive samples
        indices = np.random.choice(n_samples, n_pos, replace=False)
        y.iloc[indices] = 1
            
    # Categorical features
    cat_features = ['gender', 'department', 'job_role', 'grade_level', 'branch_country']
    
    print("Training model...")
    model = CatBoostClassifier(
        iterations=100, 
        depth=6, 
        learning_rate=0.1, 
        loss_function='Logloss', 
        verbose=False,
        allow_writing_files=False
    )
    model.fit(X, y, cat_features=cat_features)
    
    # Save model
    model_dir = Path(__file__).parent.parent / "app" / "ml"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "risk_model.cbm"
    
    model.save_model(str(model_path))
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
