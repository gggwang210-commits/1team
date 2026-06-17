import pandas as pd
import numpy as np
import os

def load_xpt(file_path):
    return pd.read_sas(file_path, format='xport')

def preprocess_nhanes():
    raw_dir = '/home/ubuntu/1team/data/raw/nhanes_2009_2010'
    processed_dir = '/home/ubuntu/1team/data/processed'
    os.makedirs(processed_dir, exist_ok=True)

    print("Loading data files...")
    arq = load_xpt(os.path.join(raw_dir, 'ARQ_F.XPT'))
    paq = load_xpt(os.path.join(raw_dir, 'PAQ_F.XPT'))
    bmx = load_xpt(os.path.join(raw_dir, 'BMX_F.XPT'))
    slq = load_xpt(os.path.join(raw_dir, 'SLQ_F.XPT'))
    smq = load_xpt(os.path.join(raw_dir, 'SMQ_F.XPT'))
    demo = load_xpt(os.path.join(raw_dir, 'DEMO_F.XPT'))

    # Master Merge
    print("Merging dataframes...")
    df = demo.merge(arq[['SEQN', 'ARQ010', 'ARQ020D']], on='SEQN', how='left')
    df = df.merge(paq, on='SEQN', how='left')
    df = df.merge(bmx, on='SEQN', how='left')
    df = df.merge(slq, on='SEQN', how='left')
    df = df.merge(smq, on='SEQN', how='left')

    # 1. Target Variable: ARQ020D (Low back pain)
    # ARQ010: Had symptoms of arthritis? (1: Yes, 2: No)
    # ARQ020D: Low back pain (4: Yes, or missing/other values)
    print("Creating target variable...")
    df['target'] = 0  # Default to 0
    
    # If ARQ020D is 4, it means Yes for Low Back Pain
    df.loc[df['ARQ020D'] == 4, 'target'] = 1
    
    # Keep only those who answered the Arthritis questionnaire (ARQ010 is 1 or 2)
    # This ensures we are only including people who were actually asked about pain
    df = df[df['ARQ010'].isin([1, 2])].copy()

    # 2. Features Engineering
    print("Engineering features...")
    
    # Physical Activity (PAQ)
    # PAD680: Minutes sedentary per day
    df['sedentary_mins'] = df['PAD680'].replace({7777: np.nan, 9999: np.nan})
    
    # Body Measures (BMX)
    # BMXBMI: Body Mass Index, BMXWAIST: Waist Circumference
    df['bmi'] = df['BMXBMI']
    df['waist'] = df['BMXWAIST']
    
    # Sleep (SLQ)
    # SLD010H: How much sleep do you get (hours)
    df['sleep_hours'] = df['SLD010H'].replace({77: np.nan, 99: np.nan})
    
    # Smoking (SMQ)
    # SMQ020: Smoked at least 100 cigarettes in life (1: Yes, 2: No)
    df['smoke_100'] = df['SMQ020'].replace({7: np.nan, 9: np.nan})
    
    # Demographics (DEMO)
    # RIAGENDR: Gender (1: Male, 2: Female)
    # RIDAGEYR: Age in years
    df['gender'] = df['RIAGENDR']
    df['age'] = df['RIDAGEYR']
    
    # Select final features
    features = ['SEQN', 'target', 'age', 'gender', 'bmi', 'waist', 'sedentary_mins', 'sleep_hours', 'smoke_100']
    final_df = df[features].copy()
    
    # Handle missing values for features
    initial_count = len(final_df)
    final_df = final_df.dropna()
    print(f"Dropped {initial_count - len(final_df)} rows with missing values.")
    print(f"Final dataset size: {len(final_df)}")
    print(f"Target distribution:\n{final_df['target'].value_counts(normalize=True)}")
    print(f"Target raw counts:\n{final_df['target'].value_counts()}")

    # Save processed data
    output_path = os.path.join(processed_dir, 'nhanes_backpain_processed.csv')
    final_df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    preprocess_nhanes()
