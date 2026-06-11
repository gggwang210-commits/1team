# Preprocessing Validation Gate

## Purpose

This document defines the required preprocessing gate before model training, probability calibration, or tournament simulation.

The project must not move directly from raw data or feature generation into modeling unless the preprocessing validation gate passes.
This prevents downstream errors caused by missing values, duplicated rows, incorrect target labels, score leakage, or MVP/global scope confusion.

## Command Prompt Used for This Step

```text
GitHub 저장소 gggwang210-commits/1team의 preprocessing gate 문서화 작업을 진행한다.

현재 문제 인식:
- 모델 학습, probability calibration, tournament simulation은 모두 전처리 산출물에 의존한다.
- 전처리가 검증되지 않으면 결측치, 중복, 잘못된 target, score leakage, MVP/global scope 혼동이 뒤 단계 전체에 영향을 준다.
- 따라서 train_baseline.py, calibrate.py, run_tournament.py 실행 전 validate_preprocessing.py를 mandatory gate로 둔다.

현재 구현된 전처리 검증 스크립트:
- src/data/validate_preprocessing.py

이번 작업 목표:
- 전처리 검증 게이트의 목적, 실행 순서, PASS/FAIL 기준, 다음 단계 진행 조건을 문서화한다.
- 팀원이 README만 보지 않아도 전처리 검증의 의미를 이해할 수 있게 한다.
- generated validation reports는 커밋하지 않는다는 원칙을 명확히 한다.

생성 파일:
- docs/preprocessing_gate.md

문서 포함 내용:
1. Purpose
   - 전처리 검증이 필요한 이유
2. Mandatory execution order
   - build_dataset.py
   - make_features.py
   - validate_team_mapping.py
   - validate_preprocessing.py
3. What the gate checks
   - 파일 존재 여부
   - CSV read 가능 여부
   - row가 비어 있지 않은지
   - required columns
   - missing values
   - duplicate rows
   - target_result 값
   - Korea MVP scope
   - score leakage 방지
   - source_target_scope 일치 여부
4. Generated reports
   - reports/preprocessing_validation.csv
   - reports/preprocessing_validation.md
5. PASS 기준
   - 모든 check가 PASS
   - 그때만 train_baseline.py, calibrate.py, run_tournament.py 진행 가능
6. FAIL 기준
   - 하나라도 FAIL이면 다음 단계 중단
   - report 확인 후 결측치/중복/target/scope/leakage 수정
7. Team rule
   - 전처리 검증 통과 전 모델링, calibration, simulation 진행 금지

주의사항:
- 이 단계는 문서화 작업이다.
- generated report는 커밋하지 않는다.
- 실제 raw data 또는 official FIFA data를 단정하지 않는다.

권장 커밋 메시지:
docs: document preprocessing validation gate
```

## Mandatory Execution Order

Run the preprocessing and validation steps in this order:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea

python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home

python src/data/validate_team_mapping.py
python src/data/validate_preprocessing.py --scope both
```

## What the Gate Checks

`src/data/validate_preprocessing.py` checks both Korea MVP and global expansion preprocessing outputs.

### Korea MVP checks

Files:

- `data/processed/matches.csv`
- `data/processed/features.csv`

Checks:

- File exists.
- CSV can be read.
- Table is not empty.
- Required columns exist.
- Required columns do not contain missing values.
- Duplicate rows are not present.
- `target_result` values are limited to `Win`, `Draw`, and `Loss`.
- `target_result_korea_perspective` exists and is valid.
- Every MVP match includes `Korea Republic` as either `home_team` or `away_team`.
- Feature table does not contain final-score leakage columns such as `home_score` or `away_score`.
- `source_target_scope` is `korea`.

### Global expansion checks

Files:

- `data/processed/matches_global.csv`
- `data/processed/features_global.csv`

Checks:

- File exists.
- CSV can be read.
- Table is not empty.
- Required columns exist.
- Required columns do not contain missing values.
- Duplicate rows are not present.
- `target_result` values are limited to `Win`, `Draw`, and `Loss`.
- Feature table does not contain final-score leakage columns such as `home_score` or `away_score`.
- `source_target_scope` is `home`.

## Generated Reports

The validation gate writes local generated reports:

- `reports/preprocessing_validation.csv`
- `reports/preprocessing_validation.md`

These reports are local validation artifacts and should not be committed by default.

## PASS Criteria

The preprocessing gate passes only when every check returns `PASS`.

When the gate passes, the team can continue to:

```bash
python src/models/train_baseline.py
python src/models/calibrate.py
python src/simulation/run_tournament.py
```

For global expansion:

```bash
python src/models/train_baseline.py \
  --features-path data/processed/features_global.csv \
  --run-name global_baseline

python src/models/calibrate.py \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_model.pkl \
  --run-name global_baseline

python src/simulation/run_tournament.py
```

## FAIL Criteria

If any check returns `FAIL`, stop the downstream workflow.

Do not run:

- `src/models/train_baseline.py`
- `src/models/calibrate.py`
- `src/simulation/run_tournament.py`

until the preprocessing issue is fixed.

Common failure causes:

- Missing generated CSV files.
- Missing required columns.
- Required columns contain missing values.
- Duplicate rows remain.
- Target labels include values other than `Win`, `Draw`, or `Loss`.
- MVP data contains non-Korea matches.
- Feature table still contains final-score columns.
- `source_target_scope` is not aligned with the intended mode.

## Team Rule

Preprocessing validation is a mandatory gate.

The team should treat this rule as part of the project workflow:

```text
No preprocessing PASS, no modeling.
No preprocessing PASS, no calibration.
No preprocessing PASS, no simulation.
```

## Recommended Workflow Before Every Major Modeling Run

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/data/validate_team_mapping.py
python src/data/validate_preprocessing.py --scope both
```

If the final command exits with code `1`, inspect:

```text
reports/preprocessing_validation.md
reports/preprocessing_validation.csv
```

Fix the preprocessing issue first, then rerun the validation gate.
