# Phase 2-2 Calibration Workflow Plan

## Purpose

This document defines the next implementation task for probability calibration.

The goal is to compare uncalibrated baseline probabilities with calibrated probabilities before tournament simulation.
Calibration is not an accuracy-improvement step. It is a probability-quality validation step.

## Command Prompt for Implementation

```text
GitHub 저장소 gggwang210-commits/1team의 Phase 2-2차 작업으로 probability calibration workflow를 구현한다.

현재 상태:
- MVP dataset and feature outputs are separated from global outputs.
- train_baseline.py supports --features-path, --model-path, --metrics-path, and --run-name.
- MVP baseline artifact: models/baseline_model.pkl
- Global baseline artifact: models/global_baseline_model.pkl

목표:
- src/models/calibrate.py를 추가한다.
- baseline model의 uncalibrated probability와 calibrated probability를 비교한다.
- Log Loss, multiclass Brier Score, calibration curve data를 생성한다.
- MVP와 global calibration outputs가 서로 덮어쓰지 않게 한다.

생성 파일:
- src/models/calibrate.py

기본 MVP 실행:
python src/models/calibrate.py

기본 입력:
- data/processed/features.csv
- models/baseline_model.pkl

기본 출력:
- models/calibrated_model.pkl
- reports/calibration_report/calibration_metrics.csv
- reports/calibration_report/calibration_curve.csv
- reports/calibration_report/summary.md

Global 실행:
python src/models/calibrate.py \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_model.pkl \
  --run-name global_baseline

Global 출력:
- models/global_baseline_calibrated_model.pkl
- reports/global_baseline_calibration_report/calibration_metrics.csv
- reports/global_baseline_calibration_report/calibration_curve.csv
- reports/global_baseline_calibration_report/summary.md

CLI 옵션:
- --features-path
- --model-path
- --calibrated-model-path
- --report-dir
- --run-name
- --method
- --cv
- --n-bins

지원 calibration method:
- sigmoid, default
- isotonic

구현 기준:
- CalibratedClassifierCV 사용
- train_baseline.py의 기존 함수를 재사용한다.
  - load_features
  - validate_input_data
  - get_feature_columns
  - split_train_test
  - calculate_multiclass_brier_score
- 신규 dependency는 추가하지 않는다.
- 기존 MVP smoke test는 깨지면 안 된다.
- tournament simulation은 이번 단계에서 구현하지 않는다.

calibration_metrics.csv 컬럼:
- model
- method
- split_method
- log_loss
- brier_score

calibration_curve.csv 컬럼:
- model
- class_label
- bin_index
- sample_count
- mean_predicted_probability
- observed_frequency

안전성:
- model_path가 없으면 FileNotFoundError를 발생시킨다.
- features_path가 없으면 FileNotFoundError를 발생시킨다.
- loaded model이 predict_proba를 지원하지 않으면 TypeError를 발생시킨다.
- run-name은 빈 문자열, 공백, /, \ 를 허용하지 않는다.
- generated model/report files는 GitHub에 커밋하지 않는다.

README.md 반영:
- MVP calibration 명령 추가
- global calibration 명령 추가
- generated artifact policy에 calibrated model/report 추가
- Log Loss와 Brier Score는 낮을수록 좋다고 설명

expansion_strategy.md 반영:
- Phase 2 Model Expansion에 calibration workflow 추가
- artifact table에 calibrated model/report 경로 추가
- Risks에 calibration overfitting 추가
- Next Actions를 run_tournament.py 설계로 갱신

권장 커밋 메시지:
feat: add baseline probability calibration workflow
```

## Verification Commands

### MVP calibration

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/models/train_baseline.py
python src/models/calibrate.py
```

### Global calibration

```bash
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/models/train_baseline.py \
  --features-path data/processed/features_global.csv \
  --run-name global_baseline
python src/models/calibrate.py \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_model.pkl \
  --run-name global_baseline
```

### Expected artifacts

```text
models/calibrated_model.pkl
reports/calibration_report/calibration_metrics.csv
reports/calibration_report/calibration_curve.csv
reports/calibration_report/summary.md
models/global_baseline_calibrated_model.pkl
reports/global_baseline_calibration_report/calibration_metrics.csv
reports/global_baseline_calibration_report/calibration_curve.csv
reports/global_baseline_calibration_report/summary.md
```

## Notes

- This is a design and implementation prompt for the next code step.
- The generated model and report artifacts should stay local by default.
- Calibration results should be used as probability-quality evidence before simulation.
