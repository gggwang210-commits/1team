import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_report():
    data_path = '/home/ubuntu/1team/data/processed/nhanes_backpain_processed.csv'
    report_dir = '/home/ubuntu/1team/reports'
    os.makedirs(report_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    
    # 1. Basic Statistics
    summary = df.describe()
    summary.to_csv(os.path.join(report_dir, 'data_summary.csv'))
    
    # 2. Visualization
    plt.figure(figsize=(15, 10))
    
    # Target distribution
    plt.subplot(2, 2, 1)
    sns.countplot(x='target', data=df)
    plt.title('Target Distribution (0: No Pain, 1: Back Pain)')
    
    # BMI vs Target
    plt.subplot(2, 2, 2)
    sns.boxplot(x='target', y='bmi', data=df)
    plt.title('BMI by Back Pain Status')
    
    # Age vs Target
    plt.subplot(2, 2, 3)
    sns.boxplot(x='target', y='age', data=df)
    plt.title('Age by Back Pain Status')
    
    # Sedentary mins vs Target
    plt.subplot(2, 2, 4)
    sns.boxplot(x='target', y='sedentary_mins', data=df)
    plt.title('Sedentary Minutes by Back Pain Status')
    
    plt.tight_layout()
    plt.savefig(os.path.join(report_dir, 'feature_distribution.png'))
    print(f"Visualization saved to {os.path.join(report_dir, 'feature_distribution.png')}")

    # 3. Correlation
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Feature Correlation Matrix')
    plt.savefig(os.path.join(report_dir, 'correlation_matrix.png'))
    print(f"Correlation matrix saved to {os.path.join(report_dir, 'correlation_matrix.png')}")

if __name__ == "__main__":
    generate_report()
