# 생활습관 기반 만성 허리 통증 위험 예측 프로젝트

본 프로젝트는 CDC NHANES 2009-2010 데이터를 활용하여 생활습관 및 신체 지표가 만성 허리 통증 위험 분류에 미치는 영향을 분석한 교육용 머신러닝 프로젝트입니다.

## 1. 프로젝트 개요
- **목적**: 생활습관(수면, 활동, 흡연)과 신체 지표(BMI, 허리둘레)를 통한 허리 통증 위험군 탐색
- **데이터 출처**: [CDC NHANES 2009-2010](https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Questionnaire&Cycle=2009-2010)
- **주요 한계**: 본 프로젝트는 **교육용 분석**이며, 의료 진단 도구가 아닙니다. 결과는 통계적 경향성을 보여줄 뿐 개인의 건강 상태 판단에 사용할 수 없습니다.

## 2. 데이터 및 타겟 정의
- **대상**: NHANES 2009-2010 설문 응답자 4,734명
- **타겟 (Target=1)**: 지난 30일 동안 6주 이상 지속된 허리 통증 경험자 (`ARQ020D == 4`)
- **대조군 (Target=0)**: 통증 증상이 없거나 허리 외 타 부위 통증자

## 3. 재현성 검증 결과
- **최종 샘플 수**: 4,734명
- **양성 비율**: 19.37%
- **음성 비율**: 80.63%
- 모든 수치는 `reproducibility_check.py` 실행을 통해 공식 코드북과 일치함을 확인했습니다.

## 4. 모델 성능 요약
| 모델 | Accuracy | Recall | F1-Score | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (Balanced)** | 0.600 | **0.563** | 0.352 | 0.619 |
| **Random Forest (Balanced)** | 0.755 | 0.268 | 0.297 | 0.583 |

- **주요 위험 신호**: 허리둘레, 흡연 경험, 수면 부족이 모델 분류에 주요하게 기여하는 변수로 확인되었습니다.

## 5. 실행 방법
1. **데이터 전처리**: `python3 src/data/preprocess_nhanes.py`
2. **모델 학습 및 평가**: `python3 src/models/train_models.py`
3. **재현성 점검**: `python3 reproducibility_check.py`
4. **고도화 실험**: `python3 src/models/advanced_modeling.py`

## 6. 참고 문헌 및 링크
- [CDC NHANES ARQ_F Codebook](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2009/DataFiles/ARQ_F.htm)
- [WHO Low Back Pain Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/low-back-pain)
