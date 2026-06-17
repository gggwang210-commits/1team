# 데이터 전처리 소스 코드 요약

본 문서는 NHANES 2009-2010 데이터를 활용한 허리 통증 위험 예측 프로젝트의 데이터 전처리 및 시각화 리포트 생성에 사용된 핵심 소스 코드를 포함하고 있습니다.

## 1. 데이터 전처리 파이프라인 (`src/data/preprocess_nhanes.py`)

이 스크립트는 NHANES의 여러 모듈(인구통계, 관절염 설문, 신체활동, 신체계측, 수면, 흡연)을 병합하고, 기획전략서의 정의에 따라 타겟 변수 및 피처를 생성합니다.

```python
import pandas as pd
import numpy as np
import os

def load_xpt(file_path):
    """SAS XPT 파일을 판다스 데이터프레임으로 로드"""
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

    # SEQN(응답자 번호) 기준 통합 병합
    print("Merging dataframes...")
    df = demo.merge(arq[['SEQN', 'ARQ010', 'ARQ020D']], on='SEQN', how='left')
    df = df.merge(paq, on='SEQN', how='left')
    df = df.merge(bmx, on='SEQN', how='left')
    df = df.merge(slq, on='SEQN', how='left')
    df = df.merge(smq, on='SEQN', how='left')

    # 1. 타겟 변수 생성: ARQ020D (만성 허리 통증)
    # ARQ020D: 4 (Low back pain) -> 1 (양성), 그 외 설문 참여자 -> 0 (음성)
    print("Creating target variable...")
    df['target'] = 0
    df.loc[df['ARQ020D'] == 4, 'target'] = 1
    
    # 관절염 설문(ARQ010)에 응답한 인원만 분석 대상으로 한정
    df = df[df['ARQ010'].isin([1, 2])].copy()

    # 2. 피처 엔지니어링
    print("Engineering features...")
    
    # 좌식 시간 (PAD680)
    df['sedentary_mins'] = df['PAD680'].replace({7777: np.nan, 9999: np.nan})
    
    # 신체 계측 (BMI, 허리둘레)
    df['bmi'] = df['BMXBMI']
    df['waist'] = df['BMXWAIST']
    
    # 수면 시간 (SLD010H)
    df['sleep_hours'] = df['SLD010H'].replace({77: np.nan, 99: np.nan})
    
    # 흡연 여부 (SMQ020)
    df['smoke_100'] = df['SMQ020'].replace({7: np.nan, 9: np.nan})
    
    # 인구통계 (성별, 나이)
    df['gender'] = df['RIAGENDR']
    df['age'] = df['RIDAGEYR']
    
    # 최종 분석 변수 선택
    features = ['SEQN', 'target', 'age', 'gender', 'bmi', 'waist', 'sedentary_mins', 'sleep_hours', 'smoke_100']
    final_df = df[features].copy()
    
    # 결측치 처리 (주요 변수 결측 행 제거)
    final_df = final_df.dropna()
    
    # 결과 저장
    output_path = os.path.join(processed_dir, 'nhanes_backpain_processed.csv')
    final_df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    preprocess_nhanes()
```

## 2. 데이터 분석 및 리포트 생성 (`reports/preprocessing_report.py`)

전처리가 완료된 데이터를 바탕으로 기초 통계량 산출 및 주요 변수의 분포를 시각화합니다.

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_report():
    data_path = '/home/ubuntu/1team/data/processed/nhanes_backpain_processed.csv'
    report_dir = '/home/ubuntu/1team/reports'
    os.makedirs(report_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    
    # 1. 기초 통계량 저장
    summary = df.describe()
    summary.to_csv(os.path.join(report_dir, 'data_summary.csv'))
    
    # 2. 데이터 시각화
    plt.figure(figsize=(15, 10))
    
    # 타겟 분포
    plt.subplot(2, 2, 1)
    sns.countplot(x='target', data=df)
    plt.title('Target Distribution (0: No Pain, 1: Back Pain)')
    
    # BMI와 통증 여부
    plt.subplot(2, 2, 2)
    sns.boxplot(x='target', y='bmi', data=df)
    plt.title('BMI by Back Pain Status')
    
    # 나이와 통증 여부
    plt.subplot(2, 2, 3)
    sns.boxplot(x='target', y='age', data=df)
    plt.title('Age by Back Pain Status')
    
    # 좌식 시간과 통증 여부
    plt.subplot(2, 2, 4)
    sns.boxplot(x='target', y='sedentary_mins', data=df)
    plt.title('Sedentary Minutes by Back Pain Status')
    
    plt.tight_layout()
    plt.savefig(os.path.join(report_dir, 'feature_distribution.png'))

    # 3. 상관관계 매트릭스
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Feature Correlation Matrix')
    plt.savefig(os.path.join(report_dir, 'correlation_matrix.png'))

if __name__ == "__main__":
    generate_report()
```
