# model.py - Fixed version (handles rare classes by merging)
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

def load_and_preprocess_data():
    """Load and preprocess the dataset"""
    print("="*60)
    print("LOADING AND PREPROCESSING DATA")
    print("="*60)
    
    # Load the dataset
    file_path = 'data/student_performance.xlsx'
    try:
        df = pd.read_excel(file_path, sheet_name='Student Performance')
        print(f"✅ Loaded {len(df)} students from {file_path}")
    except:
        try:
            df = pd.read_excel(file_path, sheet_name='Sheet1')
            print(f"✅ Loaded {len(df)} students from {file_path} (Sheet1)")
        except Exception as e:
            print(f"Error loading file: {e}")
            raise
    
    print(f"\nColumns: {df.columns.tolist()}")
    
    # Handle missing values
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        df[col] = df[col].fillna(df[col].mean())
    
    categorical_columns = df.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        if col not in ['Student_ID']:
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna('Unknown')
    
    # Create target variable - ONLY 2 CLASSES to avoid rare class issue
    # At-Risk vs Not At-Risk (binary classification)
    def categorize_performance(score):
        if score < 40:
            return 'At-Risk'
        else:
            return 'Not At-Risk'  # Merges Average and Good together
    
    df['Performance'] = df['Final Exam'].apply(categorize_performance)
    
    print("\n" + "="*60)
    print("PERFORMANCE DISTRIBUTION (Binary Classification)")
    print("="*60)
    dist = df['Performance'].value_counts()
    print(dist)
    print("\nPercentage:")
    print(df['Performance'].value_counts(normalize=True) * 100)
    
    # Check if we have enough samples in each class
    if dist.min() < 2:
        print("\n⚠️ WARNING: Still too few samples in one class. Will use random split.")
        use_stratify = False
    else:
        use_stratify = True
    
    # Store original dataframe with Student_ID
    original_df = df.copy()
    
    # Encode categorical variables
    le_gender = LabelEncoder()
    df['Gender'] = le_gender.fit_transform(df['Gender'])
    
    # One-hot encode Course
    course_dummies = pd.get_dummies(df['Course'], prefix='Course')
    df = pd.concat([df, course_dummies], axis=1)
    
    # Encode Class Engagement
    if 'Class Engagement' in df.columns:
        engagement_map = {'Low': 0, 'Medium': 1, 'High': 2}
        df['Class Engagement'] = df['Class Engagement'].map(engagement_map).fillna(1)
    
    # Encode Extra Curricular if exists
    if 'Extra_Curricular' in df.columns:
        df['Extra_Curricular'] = df['Extra_Curricular'].map({'No': 0, 'Yes': 1}).fillna(0)
    
    # Drop unnecessary columns
    columns_to_drop = ['Student_ID', 'Course', 'Final Exam']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], axis=1)
    
    print(f"\n✅ Preprocessing complete. Final shape: {df.shape}")
    
    return df, original_df, le_gender, use_stratify

def prepare_features_target(df):
    """Separate features and target, scale features"""
    feature_columns = [col for col in df.columns if col != 'Performance']
    X = df[feature_columns]
    y = df['Performance']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"\n✅ Features: {len(feature_columns)} columns")
    print(f"✅ Target classes: {y.unique().tolist()}")
    
    return X_scaled, y, scaler, feature_columns

def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    """Train multiple models and compare performance"""
    
    print("\n" + "="*60)
    print("TRAINING AND EVALUATING MODELS (Binary Classification)")
    print("="*60)
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
        'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced'),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
        'SVM': SVC(kernel='rbf', random_state=42, probability=True, class_weight='balanced')
    }
    
    results = {}
    trained_models = {}
    
    for name, model in models.items():
        print(f"\n📊 Training {name}...")
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        results[name] = {
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1
        }
        
        trained_models[name] = model
        
        print(f"   ✅ Accuracy: {accuracy:.4f}")
        print(f"   ✅ F1-Score: {f1:.4f}")
        
        # Show per-class performance
        print(f"\n   Per-class performance for {name}:")
        print(classification_report(y_test, y_pred, zero_division=0))
    
    return results, trained_models

def save_models(model, scaler, feature_columns, feature_importance, le_gender):
    """Save the best model and preprocessing objects"""
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_columns': feature_columns,
        'feature_importance': feature_importance,
        'label_encoder_gender': le_gender,
        'performance_categories': ['At-Risk', 'Not At-Risk']
    }
    joblib.dump(model_data, 'best_model.pkl')
    print(f"\n✅ Model saved as 'best_model.pkl'")
    
    # Save feature importance separately for easy access
    import json
    with open('feature_importance.json', 'w') as f:
        json.dump(feature_importance, f)
    print(f"✅ Feature importance saved to 'feature_importance.json'")

def train_best_model():
    """Main function to train and save the best model"""
    
    # Load and preprocess data
    df, original_df, le_gender, use_stratify = load_and_preprocess_data()
    
    # Prepare features and target
    X, y, scaler, feature_columns = prepare_features_target(df)
    
    # Split data
    print("\n" + "="*60)
    print("SPLITTING DATA")
    print("="*60)
    
    if use_stratify:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            print("✅ Using stratified split")
        except ValueError as e:
            print(f"⚠️ Stratified split failed: {e}")
            print("✅ Falling back to random split")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        print("✅ Using random split")
    
    print(f"\n📊 Training set: {X_train.shape[0]} samples")
    print(f"📊 Test set: {X_test.shape[0]} samples")
    
    print("\nTraining set class distribution:")
    print(y_train.value_counts())
    print("\nTest set class distribution:")
    print(y_test.value_counts())
    
    # Train and evaluate models
    results, trained_models = train_and_evaluate_models(X_train, X_test, y_train, y_test)
    
    # Find best model based on F1-score
    best_model_name = max(results, key=lambda x: results[x]['F1-Score'])
    best_model = trained_models[best_model_name]
    
    print("\n" + "="*60)
    print(f"🏆 BEST MODEL: {best_model_name}")
    print("="*60)
    print(f"   Accuracy: {results[best_model_name]['Accuracy']:.4f}")
    print(f"   F1-Score: {results[best_model_name]['F1-Score']:.4f}")
    
    # Get feature importance
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = [
            {'feature': feature_columns[i], 'importance': float(best_model.feature_importances_[i])}
            for i in range(len(feature_columns))
        ]
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        print("\n" + "="*60)
        print("🏆 TOP 10 MOST IMPORTANT FEATURES")
        print("="*60)
        for i, fi in enumerate(feature_importance[:10]):
            print(f"   {i+1}. {fi['feature']}: {fi['importance']:.4f}")
    else:
        # For models without feature_importances_
        feature_importance = []
        print("\n⚠️ Model doesn't provide feature importance")
    
    # Save the best model
    save_models(best_model, scaler, feature_columns, feature_importance, le_gender)
    
    # Display final results table
    print("\n" + "="*60)
    print("MODEL COMPARISON SUMMARY")
    print("="*60)
    results_df = pd.DataFrame(results).T
    print(results_df.round(4))
    
    return best_model, scaler, feature_columns, feature_importance

if __name__ == "__main__":
    train_best_model()
    print("\n" + "="*60)
    print("🎉 MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("You can now run: streamlit run app.py")