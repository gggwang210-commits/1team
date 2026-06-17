import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

def train_and_evaluate():
    # Load data
    data_path = '/home/ubuntu/1team/data/processed/nhanes_backpain_processed.csv'
    df = pd.read_csv(data_path)
    
    # Features and Target
    X = df.drop(['SEQN', 'target'], axis=1)
    y = df['target']
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Train set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")

    # 1. Baseline Model (Most Frequent Class)
    y_baseline = np.zeros_like(y_test)
    
    # 2. Logistic Regression (with balanced weights)
    lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    y_prob_lr = lr_model.predict_proba(X_test)[:, 1]
    
    # 3. Random Forest (with balanced weights)
    rf_model = RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    y_prob_rf = rf_model.predict_proba(X_test)[:, 1]
    
    # Evaluation Metrics
    models = {
        'Baseline': (y_baseline, np.zeros_like(y_test)),
        'Logistic Regression': (y_pred_lr, y_prob_lr),
        'Random Forest': (y_pred_rf, y_prob_rf)
    }
    
    results = []
    for name, (pred, prob) in models.items():
        results.append({
            'Model': name,
            'Accuracy': accuracy_score(y_test, pred),
            'Precision': precision_score(y_test, pred, zero_division=0),
            'Recall': recall_score(y_test, pred),
            'F1': f1_score(y_test, pred),
            'ROC-AUC': roc_auc_score(y_test, prob)
        })
    
    results_df = pd.DataFrame(results)
    print("\n--- Model Performance Comparison ---")
    print(results_df.to_string(index=False))
    
    # Save results
    os.makedirs('/home/ubuntu/1team/outputs', exist_ok=True)
    results_df.to_csv('/home/ubuntu/1team/outputs/model_performance.csv', index=False)
    
    # Visualizations
    output_dir = '/home/ubuntu/1team/outputs'
    
    # Confusion Matrix (Random Forest)
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred_rf)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix - Random Forest (Balanced)')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix_rf.png'))
    
    # ROC Curve
    plt.figure(figsize=(8, 6))
    for name, (pred, prob) in models.items():
        if name != 'Baseline':
            fpr, tpr, _ = roc_curve(y_test, prob)
            plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc_score(y_test, prob):.2f})")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'roc_curve.png'))
    
    # Feature Importance (Random Forest)
    plt.figure(figsize=(10, 6))
    importances = pd.Series(rf_model.feature_importances_, index=X.columns).sort_values(ascending=False)
    sns.barplot(x=importances.values, y=importances.index)
    plt.title('Feature Importance - Random Forest')
    plt.savefig(os.path.join(output_dir, 'feature_importance_rf.png'))
    
    # Coefficients (Logistic Regression)
    plt.figure(figsize=(10, 6))
    coefs = pd.Series(lr_model.coef_[0], index=X.columns).sort_values(ascending=False)
    sns.barplot(x=coefs.values, y=coefs.index)
    plt.title('Coefficients - Logistic Regression')
    plt.savefig(os.path.join(output_dir, 'coefficients_lr.png'))

    print(f"\nVisualizations saved to {output_dir}")

if __name__ == "__main__":
    train_and_evaluate()
