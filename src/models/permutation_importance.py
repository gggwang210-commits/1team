import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_permutation_importance():
    data_path = '/home/ubuntu/1team/data/processed/nhanes_backpain_processed.csv'
    df = pd.read_csv(data_path)
    X = df.drop(['SEQN', 'target'], axis=1)
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Use Logistic Regression as it had better recall/AUC
    model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    print("Calculating permutation importance (this may take a moment)...")
    result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)
    
    importance_df = pd.DataFrame({
        'Feature': X.columns,
        'Importance_Mean': result.importances_mean,
        'Importance_Std': result.importances_std
    }).sort_values(by='Importance_Mean', ascending=False)

    print("\n--- Permutation Importance (Logistic Regression) ---")
    print(importance_df.to_string(index=False))

    # Visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance_Mean', y='Feature', data=importance_df)
    plt.errorbar(x=importance_df['Importance_Mean'], y=range(len(importance_df)), 
                 xerr=importance_df['Importance_Std'], fmt='none', c='black', capsize=3)
    plt.title('Permutation Importance (on Test Set)')
    plt.xlabel('Mean Accuracy Decrease')
    
    output_dir = '/home/ubuntu/1team/outputs'
    plt.savefig(os.path.join(output_dir, 'permutation_importance.png'))
    print(f"Visualization saved to {os.path.join(output_dir, 'permutation_importance.png')}")

if __name__ == "__main__":
    calculate_permutation_importance()
