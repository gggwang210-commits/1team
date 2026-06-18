import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_curve, f1_score, recall_score, precision_score, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

def run_advanced_experiments():
    # Load data
    data_path = '/home/ubuntu/1team/data/processed/nhanes_backpain_processed.csv'
    df = pd.read_csv(data_path)
    
    # Features and Target
    X = df.drop(['SEQN', 'target'], axis=1)
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 1. Threshold Comparison for Logistic Regression
    lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    y_probs = lr_model.predict_proba(X_test)[:, 1]
    
    thresholds = np.arange(0.3, 0.7, 0.05)
    thresh_results = []
    
    for t in thresholds:
        y_pred = (y_probs >= t).astype(int)
        thresh_results.append({
            'Threshold': round(t, 2),
            'Precision': precision_score(y_test, y_pred, zero_division=0),
            'Recall': recall_score(y_test, y_pred),
            'F1': f1_score(y_test, y_pred)
        })
    
    thresh_df = pd.DataFrame(thresh_results)
    print("\n--- Threshold Comparison (Logistic Regression) ---")
    print(thresh_df.to_string(index=False))
    
    os.makedirs('/home/ubuntu/1team/outputs', exist_ok=True)
    thresh_df.to_csv('/home/ubuntu/1team/outputs/threshold_comparison.csv', index=False)

    # 2. Class Weight Comparison
    experiments = [
        ('LR (Default)', LogisticRegression(max_iter=1000, random_state=42)),
        ('LR (Balanced)', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)),
        ('RF (Balanced)', RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42))
    ]
    
    exp_results = []
    for name, model in experiments:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        exp_results.append({
            'Model': name,
            'Recall': recall_score(y_test, y_pred),
            'F1': f1_score(y_test, y_pred),
            'ROC-AUC': roc_auc_score(y_test, y_prob)
        })
    
    exp_df = pd.DataFrame(exp_results)
    print("\n--- Model/Weight Experiment Comparison ---")
    print(exp_df.to_string(index=False))
    exp_df.to_csv('/home/ubuntu/1team/outputs/advanced_model_comparison.csv', index=False)

    # Visualization: Precision-Recall Trade-off
    plt.figure(figsize=(10, 6))
    plt.plot(thresh_df['Threshold'], thresh_df['Precision'], marker='o', label='Precision')
    plt.plot(thresh_df['Threshold'], thresh_df['Recall'], marker='s', label='Recall')
    plt.plot(thresh_df['Threshold'], thresh_df['F1'], marker='^', label='F1 Score')
    plt.axvline(x=0.5, color='gray', linestyle='--', label='Default Threshold (0.5)')
    plt.title('Precision-Recall-F1 Trade-off by Threshold')
    plt.xlabel('Threshold')
    plt.ylabel('Score')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('/home/ubuntu/1team/outputs/threshold_tradeoff.png')
    print("\nVisualization saved to /home/ubuntu/1team/outputs/threshold_tradeoff.png")

if __name__ == "__main__":
    run_advanced_experiments()
