"""
Model training scripts for HR Analytics predictive models.
Trains XGBoost, LightGBM, and CatBoost models for:
- Attrition prediction
- Performance prediction
- Promotion readiness prediction

Usage:
    python scripts/train_models.py --model attrition
    python scripts/train_models.py --model performance
    python scripts/train_models.py --model promotion
    python scripts/train_models.py --all
"""

import argparse
import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)

# ML Libraries
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Model save directory
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


class FeatureEngineer:
    """Feature engineering for HR predictive models."""
    
    def __init__(self):
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler = StandardScaler()
        self.feature_columns: List[str] = []
    
    def fit_transform(self, df: pd.DataFrame, target: str) -> Tuple[np.ndarray, np.ndarray]:
        """Fit encoders and transform data."""
        df = df.copy()
        
        # Calculate derived features
        df = self._engineer_features(df)
        
        # Encode categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        categorical_cols = [c for c in categorical_cols if c != target]
        
        for col in categorical_cols:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col].astype(str).fillna('Unknown'))
            else:
                df[col] = df[col].astype(str).fillna('Unknown')
                # Handle unseen categories
                le = self.label_encoders[col]
                df[col] = df[col].apply(lambda x: x if x in le.classes_ else 'Unknown')
                if 'Unknown' not in le.classes_:
                    le.classes_ = np.append(le.classes_, 'Unknown')
                df[col] = le.transform(df[col])
        
        # Select feature columns
        exclude_cols = [target, 'employee_id', 'full_name', 'date_of_birth', 'date_of_joining']
        self.feature_columns = [c for c in df.columns if c not in exclude_cols]
        
        X = df[self.feature_columns].fillna(0).values
        y = df[target].values if target in df.columns else None
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform new data using fitted encoders."""
        df = df.copy()
        df = self._engineer_features(df)
        
        for col, le in self.label_encoders.items():
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('Unknown')
                df[col] = df[col].apply(lambda x: x if x in le.classes_ else 'Unknown')
                df[col] = le.transform(df[col])
        
        X = df[self.feature_columns].fillna(0).values
        X = self.scaler.transform(X)
        
        return X
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features."""
        # Tenure in years
        if 'date_of_joining' in df.columns:
            df['date_of_joining'] = pd.to_datetime(df['date_of_joining'], errors='coerce')
            df['tenure_years'] = (datetime.now() - df['date_of_joining']).dt.days / 365.25
            df['tenure_years'] = df['tenure_years'].fillna(0).clip(lower=0)
        
        # Age
        if 'date_of_birth' in df.columns:
            df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
            df['age'] = (datetime.now() - df['date_of_birth']).dt.days / 365.25
            df['age'] = df['age'].fillna(30).clip(lower=18, upper=70)
        
        # Grade level numeric
        if 'grade_level' in df.columns:
            grade_map = {
                'OG-1': 1, 'OG-2': 2, 'OG-3': 3,
                'AVP': 4, 'VP': 5, 'SVP': 6,
                'EVP': 7, 'MD': 8, 'SMD': 9,
                'DMD': 10, 'President': 11, 'CEO': 12
            }
            df['grade_numeric'] = df['grade_level'].map(grade_map).fillna(2)
        
        # Salary to grade ratio (normalized compensation)
        if 'total_monthly_salary' in df.columns and 'grade_numeric' in df.columns:
            grade_avg_salary = df.groupby('grade_numeric')['total_monthly_salary'].transform('mean')
            df['salary_ratio'] = df['total_monthly_salary'] / grade_avg_salary.replace(0, 1)
        
        # Performance bucket
        if 'performance_score' in df.columns:
            df['high_performer'] = (df['performance_score'] >= 4.0).astype(int)
            df['low_performer'] = (df['performance_score'] < 3.0).astype(int)
        
        return df
    
    def save(self, path: Path):
        """Save feature engineer state."""
        state = {
            'label_encoders': {k: {'classes': v.classes_.tolist()} for k, v in self.label_encoders.items()},
            'scaler_mean': self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else None,
            'scaler_scale': self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else None,
            'feature_columns': self.feature_columns
        }
        with open(path, 'w') as f:
            json.dump(state, f)
    
    def load(self, path: Path):
        """Load feature engineer state."""
        with open(path, 'r') as f:
            state = json.load(f)
        
        for col, le_state in state['label_encoders'].items():
            self.label_encoders[col] = LabelEncoder()
            self.label_encoders[col].classes_ = np.array(le_state['classes'])
        
        if state['scaler_mean']:
            self.scaler.mean_ = np.array(state['scaler_mean'])
            self.scaler.scale_ = np.array(state['scaler_scale'])
        
        self.feature_columns = state['feature_columns']


class AttritionModelTrainer:
    """Train attrition prediction models."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models: Dict[str, object] = {}
        self.metrics: Dict[str, Dict] = {}
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for attrition prediction."""
        # Create synthetic attrition target if not present
        if 'attrition' not in df.columns:
            # Generate based on heuristics
            np.random.seed(42)
            
            # Base attrition probability
            probs = np.full(len(df), 0.1)
            
            # Higher attrition for low performers
            if 'performance_score' in df.columns:
                low_perf_mask = df['performance_score'] < 3.0
                probs[low_perf_mask] += 0.15
            
            # Higher attrition for low tenure
            if 'tenure_years' in df.columns or 'date_of_joining' in df.columns:
                df_temp = self.feature_engineer._engineer_features(df.copy())
                if 'tenure_years' in df_temp.columns:
                    low_tenure_mask = df_temp['tenure_years'] < 2
                    probs[low_tenure_mask] += 0.1
            
            # Higher attrition for junior grades
            if 'grade_level' in df.columns:
                junior_grades = ['OG-1', 'OG-2']
                junior_mask = df['grade_level'].isin(junior_grades)
                probs[junior_mask] += 0.05
            
            # Generate attrition labels
            df['attrition'] = (np.random.random(len(df)) < probs).astype(int)
            print(f"Generated synthetic attrition labels: {df['attrition'].sum()} / {len(df)} ({100*df['attrition'].mean():.1f}%)")
        
        X, y = self.feature_engineer.fit_transform(df, 'attrition')
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train ensemble of models."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nTraining data: {X_train.shape[0]} samples")
        print(f"Test data: {X_test.shape[0]} samples")
        print(f"Attrition rate: {100*y_train.mean():.1f}%")
        
        # XGBoost
        print("\n--- Training XGBoost ---")
        xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=len(y_train[y_train==0]) / max(len(y_train[y_train==1]), 1),
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        self.models['xgboost'] = xgb_model
        self._evaluate_model('xgboost', xgb_model, X_test, y_test)
        
        # LightGBM
        print("\n--- Training LightGBM ---")
        lgb_model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            class_weight='balanced',
            random_state=42,
            verbose=-1
        )
        lgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
        )
        self.models['lightgbm'] = lgb_model
        self._evaluate_model('lightgbm', lgb_model, X_test, y_test)
        
        # CatBoost
        print("\n--- Training CatBoost ---")
        cb_model = cb.CatBoostClassifier(
            iterations=200,
            depth=6,
            learning_rate=0.1,
            auto_class_weights='Balanced',
            random_state=42,
            verbose=False
        )
        cb_model.fit(X_train, y_train, eval_set=(X_test, y_test))
        self.models['catboost'] = cb_model
        self._evaluate_model('catboost', cb_model, X_test, y_test)
        
        # Ensemble predictions
        print("\n--- Ensemble Results ---")
        probs = np.mean([
            xgb_model.predict_proba(X_test)[:, 1],
            lgb_model.predict_proba(X_test)[:, 1],
            cb_model.predict_proba(X_test)[:, 1]
        ], axis=0)
        preds = (probs >= 0.5).astype(int)
        
        self.metrics['ensemble'] = {
            'accuracy': accuracy_score(y_test, preds),
            'precision': precision_score(y_test, preds, zero_division=0),
            'recall': recall_score(y_test, preds, zero_division=0),
            'f1': f1_score(y_test, preds, zero_division=0),
            'roc_auc': roc_auc_score(y_test, probs)
        }
        print(f"Ensemble ROC-AUC: {self.metrics['ensemble']['roc_auc']:.4f}")
        print(f"Ensemble F1-Score: {self.metrics['ensemble']['f1']:.4f}")
    
    def _evaluate_model(self, name: str, model, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate a single model."""
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        self.metrics[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_prob)
        }
        
        print(f"{name} ROC-AUC: {self.metrics[name]['roc_auc']:.4f}")
        print(f"{name} F1-Score: {self.metrics[name]['f1']:.4f}")
    
    def save(self, output_dir: Path):
        """Save trained models and artifacts."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            model_path = output_dir / f"attrition_{name}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Saved {name} model to {model_path}")
        
        # Save feature engineer
        fe_path = output_dir / "attrition_feature_engineer.json"
        self.feature_engineer.save(fe_path)
        print(f"Saved feature engineer to {fe_path}")
        
        # Save metrics
        metrics_path = output_dir / "attrition_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"Saved metrics to {metrics_path}")


class PerformanceModelTrainer:
    """Train performance prediction models."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models: Dict[str, object] = {}
        self.metrics: Dict[str, Dict] = {}
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for performance prediction."""
        # Create high performer binary target
        if 'performance_score' not in df.columns:
            raise ValueError("performance_score column required")
        
        df = df.copy()
        df['high_performer'] = (df['performance_score'] >= 4.0).astype(int)
        
        # Remove performance_score from features to prevent leakage
        df_features = df.drop(columns=['performance_score'])
        
        X, y = self.feature_engineer.fit_transform(df_features, 'high_performer')
        
        print(f"High performers: {y.sum()} / {len(y)} ({100*y.mean():.1f}%)")
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train performance prediction models."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nTraining data: {X_train.shape[0]} samples")
        print(f"Test data: {X_test.shape[0]} samples")
        
        # XGBoost
        print("\n--- Training XGBoost ---")
        xgb_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        self.models['xgboost'] = xgb_model
        self._evaluate_model('xgboost', xgb_model, X_test, y_test)
        
        # LightGBM
        print("\n--- Training LightGBM ---")
        lgb_model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
        lgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
        self.models['lightgbm'] = lgb_model
        self._evaluate_model('lightgbm', lgb_model, X_test, y_test)
        
        # CatBoost
        print("\n--- Training CatBoost ---")
        cb_model = cb.CatBoostClassifier(
            iterations=200,
            depth=6,
            learning_rate=0.1,
            random_state=42,
            verbose=False
        )
        cb_model.fit(X_train, y_train, eval_set=(X_test, y_test))
        self.models['catboost'] = cb_model
        self._evaluate_model('catboost', cb_model, X_test, y_test)
    
    def _evaluate_model(self, name: str, model, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate model performance."""
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        self.metrics[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_prob)
        }
        
        print(f"{name} ROC-AUC: {self.metrics[name]['roc_auc']:.4f}")
    
    def save(self, output_dir: Path):
        """Save trained models."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for name, model in self.models.items():
            model_path = output_dir / f"performance_{name}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Saved {name} model to {model_path}")
        
        fe_path = output_dir / "performance_feature_engineer.json"
        self.feature_engineer.save(fe_path)
        
        metrics_path = output_dir / "performance_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)


class PromotionModelTrainer:
    """Train promotion readiness prediction models."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models: Dict[str, object] = {}
        self.metrics: Dict[str, Dict] = {}
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for promotion prediction."""
        df = df.copy()
        
        # Create promotion readiness target based on:
        # - High performance
        # - Sufficient tenure in current grade
        # - Not already at top grade
        
        np.random.seed(42)
        
        # Initialize promotion probability
        probs = np.full(len(df), 0.2)
        
        # High performers more likely
        if 'performance_score' in df.columns:
            high_perf = df['performance_score'] >= 4.0
            probs[high_perf] += 0.3
        
        # Longer tenure more likely
        if 'date_of_joining' in df.columns:
            df_temp = self.feature_engineer._engineer_features(df.copy())
            if 'tenure_years' in df_temp.columns:
                probs += np.clip(df_temp['tenure_years'] * 0.02, 0, 0.2)
        
        # Senior grades less likely
        senior_grades = ['EVP', 'MD', 'SMD', 'DMD', 'President', 'CEO']
        if 'grade_level' in df.columns:
            senior_mask = df['grade_level'].isin(senior_grades)
            probs[senior_mask] *= 0.3
        
        # Generate promotion ready labels
        df['promotion_ready'] = (np.random.random(len(df)) < probs).astype(int)
        print(f"Promotion ready: {df['promotion_ready'].sum()} / {len(df)} ({100*df['promotion_ready'].mean():.1f}%)")
        
        X, y = self.feature_engineer.fit_transform(df, 'promotion_ready')
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train promotion models."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\nTraining data: {X_train.shape[0]} samples")
        print(f"Test data: {X_test.shape[0]} samples")
        
        # Train all models
        for name, ModelClass, params in [
            ('xgboost', xgb.XGBClassifier, {
                'n_estimators': 200, 'max_depth': 6, 'learning_rate': 0.1,
                'random_state': 42, 'use_label_encoder': False, 'eval_metric': 'logloss'
            }),
            ('lightgbm', lgb.LGBMClassifier, {
                'n_estimators': 200, 'max_depth': 6, 'learning_rate': 0.1,
                'random_state': 42, 'verbose': -1
            }),
            ('catboost', cb.CatBoostClassifier, {
                'iterations': 200, 'depth': 6, 'learning_rate': 0.1,
                'random_state': 42, 'verbose': False
            })
        ]:
            print(f"\n--- Training {name} ---")
            model = ModelClass(**params)
            if name == 'catboost':
                model.fit(X_train, y_train, eval_set=(X_test, y_test))
            else:
                model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False if name == 'xgboost' else None)
            
            self.models[name] = model
            self._evaluate_model(name, model, X_test, y_test)
    
    def _evaluate_model(self, name: str, model, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate model."""
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        self.metrics[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_prob)
        }
        
        print(f"{name} ROC-AUC: {self.metrics[name]['roc_auc']:.4f}")
    
    def save(self, output_dir: Path):
        """Save models."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for name, model in self.models.items():
            model_path = output_dir / f"promotion_{name}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"Saved {name} model to {model_path}")
        
        fe_path = output_dir / "promotion_feature_engineer.json"
        self.feature_engineer.save(fe_path)
        
        metrics_path = output_dir / "promotion_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)


def load_data(csv_path: str) -> pd.DataFrame:
    """Load employee data from CSV."""
    print(f"\nLoading data from {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records with {len(df.columns)} columns")
    return df


def main():
    parser = argparse.ArgumentParser(description='Train HR Analytics predictive models')
    parser.add_argument('--model', choices=['attrition', 'performance', 'promotion', 'all'],
                        default='all', help='Model type to train')
    parser.add_argument('--data', type=str, help='Path to employee CSV data')
    parser.add_argument('--output', type=str, default=str(MODELS_DIR),
                        help='Output directory for models')
    args = parser.parse_args()
    
    # Find data file
    if args.data:
        data_path = args.data
    else:
        # Look for data in common locations
        possible_paths = [
            Path(__file__).parent.parent / "data" / "pak_bank_employees_100k.csv",
            Path(__file__).parent.parent.parent / "pak_bank_employees_100k.csv",
            Path(__file__).parent.parent / "data" / "bank_employee_dataset_5000.csv",
        ]
        data_path = None
        for p in possible_paths:
            if p.exists():
                data_path = str(p)
                break
        
        if not data_path:
            print("Error: No data file found. Please specify --data path")
            sys.exit(1)
    
    # Load data
    df = load_data(data_path)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Train models
    if args.model in ['attrition', 'all']:
        print("\n" + "="*60)
        print("Training Attrition Prediction Models")
        print("="*60)
        trainer = AttritionModelTrainer()
        X, y = trainer.prepare_data(df)
        trainer.train(X, y)
        trainer.save(output_dir)
    
    if args.model in ['performance', 'all']:
        print("\n" + "="*60)
        print("Training Performance Prediction Models")
        print("="*60)
        trainer = PerformanceModelTrainer()
        try:
            X, y = trainer.prepare_data(df)
            trainer.train(X, y)
            trainer.save(output_dir)
        except ValueError as e:
            print(f"Skipping performance model: {e}")
    
    if args.model in ['promotion', 'all']:
        print("\n" + "="*60)
        print("Training Promotion Readiness Models")
        print("="*60)
        trainer = PromotionModelTrainer()
        X, y = trainer.prepare_data(df)
        trainer.train(X, y)
        trainer.save(output_dir)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print(f"Models saved to: {output_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
