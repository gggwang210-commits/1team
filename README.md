# 2026 FIFA World Cup Prediction Model

## Team Project

Machine learning based prediction system for 2026 FIFA World Cup match outcomes.

The repository prioritizes a **global match prediction pipeline first**, with Korea Republic preserved as a reproducible filtered use case and legacy smoke-test path.

## Scope Summary

Primary scope:

- Global match-level Win/Draw/Loss probability prediction
- Global baseline and calibrated probability outputs
- Tournament-simulation-ready match probability tables
- Group-stage and knockout simulation scaffolding
- Champion probabilities as a later simulation output

Korea Republic role:

- Filtered application case from the global model
- Legacy reproducible MVP/smoke-test path
- Useful presentation example, not the primary modeling scope

The project now treats global match prediction as the main direction. Korea Republic prediction is preserved for reproducibility and demonstration, but it is no longer the first-priority project target.

## Global-first Project Scope

The current priority is to build a global match-level prediction pipeline that can estimate Win/Draw/Loss probabilities for international football fixtures.

Primary output concept:

- Home-team Win Probability
- Draw Probability
- Home-team Loss Probability

For Korea Republic views, predictions can be filtered and reinterpreted as a Korea application case when Korea Republic appears as either `home_team` or `away_team`.

The global pipeline does not directly claim official 2026 FIFA World Cup results. Later phases expand in this order:

match probabilities → probability calibration → group simulation → knockout simulation → champion probability.

### Korea Filtered Use Case / Legacy MVP Path

The Korea Republic path is retained as a reproducible filtered use case and local smoke-test path.

In this path:

- Korea Republic labels use Korea Republic's perspective.
- `Win` means Korea Republic wins the match, regardless of whether Korea Republic is listed as the home or away team.
- This path is useful for demonstration and regression checks, but it is no longer the primary project scope.

### Target column contract

The project intentionally uses result labels from different perspectives at different pipeline stages. Keep this contract explicit to avoid target leakage or accidentally training on the wrong label:

- `matches_global.csv.target_result` = home-team perspective result label for global modeling.
- `features_global.csv.target_result` = model target for the global pipeline.
- `matches.csv.target_result` = home-team perspective result label in the Korea-filtered match table.
- `matches.csv.target_result_korea_perspective` = Korea Republic perspective result label when the match includes Korea Republic.
- `features.csv.target_result` = model target for the Korea filtered/smoke-test path.
- `features.csv.target_result_korea_perspective` = retained audit copy for Korea Republic perspective when available, excluded from every model input feature set.
- `features.csv.source_target_column` and `features.csv.source_target_scope` = audit metadata showing which target definition was copied into `features.csv.target_result`.

`src/models/train_baseline.py` treats `features*.csv.target_result` as the only modeling target and excludes every target/result/score-like column from the feature matrix before preprocessing and training.

## Global-first Strategy

The project keeps the existing Korea smoke-test path while making the global prediction pipeline the primary path.

Key changes:

- `src/data/build_dataset.py` supports `filter_korea=False` through `--global-scope` for global data expansion.
- `src/features/make_features.py` supports `--target-scope home` for global feature generation and `--target-scope korea` for the Korea filtered path.
- Global and Korea processed outputs are separated by default to reduce accidental overwrites.
- `src/data/validate_preprocessing.py` is the required preprocessing gate before model training, calibration, or simulation.
- `scripts/validate_preprocessing_pipeline.sh` runs the complete preprocessing build and validation gate in one command.
- `src/models/train_baseline.py` supports `--features-path`, `--run-name`, `--model-path`, and `--metrics-path` so global and Korea artifacts can be separated.
- `src/models/calibrate.py` calibrates baseline probabilities and writes calibration metrics, curve data, and summary reports.
- `data/mappings/team_name_mapping.csv` provides an initial country alias mapping draft.
- `src/data/validate_team_mapping.py` validates raw team names against the mapping table.
- `data/tournament/participants.json`, `schedule.json`, and `bracket.json` provide skeleton interfaces for future simulation work.
- `src/simulation/` is reserved for tournament simulation code.
- `docs/preprocessing_gate.md` documents the preprocessing PASS/FAIL rule.
- `docs/preprocessing_runbook.md` provides a PC/Codespaces execution checklist.
- `docs/expansion_strategy.md` records the global-first roadmap and team decision points.

## Phase 1 Data Files

These files are committed because they are source data skeletons and interface definitions, not generated reports.

| File | Purpose | Status |
| --- | --- | --- |
| `data/mappings/team_name_mapping.csv` | Country canonical-name, FIFA code, and alias mapping | Initial draft; validate against raw data |
| `data/tournament/participants.json` | Participant input schema for simulation | `SKELETON_NOT_OFFICIAL` |
| `data/tournament/schedule.json` | Match schedule input schema | `SKELETON_NOT_OFFICIAL` |
| `data/tournament/bracket.json` | Group and knockout bracket schema | `SKELETON_NOT_OFFICIAL` |

The tournament JSON files are not official FIFA data. Values marked `TBD` must be replaced only after official source verification.

## Generated File Paths

| Scope | Match file | Feature file | Validation outputs | Model file | Metrics file | Calibration outputs |
| --- | --- | --- | --- | --- | --- | --- |
| Global baseline | `data/processed/matches_global.csv` | `data/processed/features_global.csv` | `reports/preprocessing_validation.csv`, `reports/preprocessing_validation.md` | `models/global_baseline_model.pkl` | `reports/global_baseline_metrics.csv` | `models/global_baseline_calibrated_model.pkl`, `reports/global_baseline_calibration_report/` |
| Korea filtered path | `data/processed/matches.csv` | `data/processed/features.csv` | `reports/preprocessing_validation.csv`, `reports/preprocessing_validation.md` | `models/baseline_model.pkl` | `reports/baseline_metrics.csv` | `models/calibrated_model.pkl`, `reports/calibration_report/` |

Calibration is not tournament simulation yet. It checks probability quality before simulation by comparing uncalibrated and calibrated probabilities. Lower Log Loss and lower Brier Score are better.

## Stack

- Python
- Pandas
- Scikit-learn
- Streamlit
- Django, optional expansion phase

## Status

Global-first prediction pipeline with a preserved Korea filtered smoke-test path.

## Global-first Data Flow

Generated report files are intentionally not committed. Running the pipeline recreates reports and model artifacts from the current code, data, and model run. Treat those files as local evidence for the current run rather than authoritative checked-in model results.

The implemented global-first pipeline has seven explicit stages:

1. `src/data/build_dataset.py --global-scope` standardizes international match-result data and writes `data/processed/matches_global.csv`.
   - The Korea filtered path remains available with `python src/data/build_dataset.py`.
   - Custom output is available with `--output-path`.
2. `src/features/make_features.py --target-scope home` converts processed global match rows into model-ready pre-match features.
   - Global output: `data/processed/features_global.csv`.
   - Korea filtered output: `data/processed/features.csv`.
   - Custom input and output paths are available with `--input-path` and `--output-path`.
3. `src/data/validate_preprocessing.py` verifies preprocessing outputs before modeling.
   - Checks missing values, duplicates, required columns, target labels, Korea filtered scope, source target scope, and final-score leakage.
   - Writes `reports/preprocessing_validation.csv` and `reports/preprocessing_validation.md`.
   - If any check fails, downstream modeling, calibration, and simulation should stop.
4. `src/models/train_baseline.py` validates the feature table before model fitting.
   - Global input should use `--features-path data/processed/features_global.csv`.
   - `--run-name global_baseline` writes `models/global_baseline_model.pkl` and `reports/global_baseline_metrics.csv`.
   - The Korea filtered path remains available through the default `features.csv` input.
   - Implemented metrics include Accuracy, Macro F1, Log Loss, and one-vs-rest multiclass Brier Score.
5. `src/models/calibrate.py` calibrates baseline probabilities.
   - Global output with `--run-name global_baseline`: `models/global_baseline_calibrated_model.pkl` and `reports/global_baseline_calibration_report/`.
   - Korea filtered output remains available as `models/calibrated_model.pkl` and `reports/calibration_report/`.
   - Report files include `calibration_metrics.csv`, `calibration_curve.csv`, and `summary.md`.
6. `src/simulation/run_tournament.py` prepares tournament-simulation-stage probability inputs from the global calibrated model.
7. `src/models/predict.py` and `src/models/evaluate.py` remain available for the Korea filtered legacy demonstration path.

## Project Structure

```text
.
├── app/
│   └── streamlit_app.py
├── data/
│   ├── mappings/
│   │   └── team_name_mapping.csv
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   └── .gitkeep
│   └── tournament/
│       ├── bracket.json
│       ├── participants.json
│       └── schedule.json
├── docs/
│   ├── calibration_workflow.md
│   ├── expansion_strategy.md
│   ├── preprocessing_gate.md
│   ├── preprocessing_runbook.md
│   └── simulation_contract.md
├── models/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── scripts/
│   ├── smoke_test.sh
│   └── validate_preprocessing_pipeline.sh
├── src/
│   ├── data/
│   │   ├── build_dataset.py
│   │   ├── clean_data.py
│   │   ├── load_data.py
│   │   ├── validate_preprocessing.py
│   │   └── validate_team_mapping.py
│   ├── features/
│   │   └── make_features.py
│   ├── models/
│   │   ├── calibrate.py
│   │   ├── evaluate.py
│   │   ├── predict.py
│   │   └── train_baseline.py
│   └── simulation/
│       ├── .gitkeep
│       └── run_tournament.py
├── PROJECT_SPEC.md
├── README.md
├── requirements.txt
└── .gitignore
```

## How to Run the Global-first Pipeline

1. Create and activate a Python virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Add raw datasets to `data/raw/` when available.

4. Run the source validation gate.

   ```bash
   python src/data/validate_sources.py
   ```

   Stop here if source validation fails. Do not run preprocessing until the raw files and expected columns pass this check.

5. Build the global processed match dataset.

   ```bash
   python src/data/build_dataset.py --global-scope
   ```

6. Create global model-ready features.

   ```bash
   python src/features/make_features.py --target-scope home
   ```

7. Run the preprocessing validation gate.

   Recommended one-command PC/Codespaces path, including both global and Korea filtered checks:

   ```bash
   bash scripts/validate_preprocessing_pipeline.sh
   ```

   Global-only validation path:

   ```bash
   python src/data/validate_preprocessing.py --scope global
   ```

   Continue only if preprocessing validation passes. The project rule is:

   ```text
   No source validation PASS, no preprocessing.
   No preprocessing PASS, no modeling.
   No preprocessing PASS, no calibration.
   No preprocessing PASS, no simulation.
   ```

8. Train the global baseline model.

   ```bash
   python src/models/train_baseline.py \
     --features-path data/processed/features_global.csv \
     --run-name global_baseline
   ```

9. Calibrate global baseline probabilities.

   ```bash
   python src/models/calibrate.py \
     --features-path data/processed/features_global.csv \
     --model-path models/global_baseline_model.pkl \
     --run-name global_baseline
   ```

10. Prepare simulation-stage match probabilities.

   ```bash
   python src/simulation/run_tournament.py
   ```

## Korea Filtered Use Case / Legacy Smoke-test Path

Use this path when the team needs a quick reproducible Korea Republic demonstration or regression check:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/data/validate_preprocessing.py --scope korea
python src/models/train_baseline.py
python src/models/predict.py
python src/models/evaluate.py
```

## Preprocessing Validation Gate

Run this gate after data build and feature generation, and before any model training, calibration, or simulation.

Recommended one-command path:

```bash
bash scripts/validate_preprocessing_pipeline.sh
```

Manual validation-only path:

```bash
python src/data/validate_preprocessing.py --scope both
```

Primary global-only validation path:

```bash
python src/data/validate_preprocessing.py --scope global
```

The validation gate checks:

- Required output files exist and are readable.
- Match and feature tables are not empty.
- Required columns are present.
- Required columns do not contain missing values.
- Duplicate rows are not present.
- Target labels are limited to `Win`, `Draw`, and `Loss`.
- Korea filtered rows are Korea Republic matches only.
- Feature tables do not contain final-score leakage columns such as `home_score` or `away_score`.
- `source_target_scope` matches the intended scope: `home` for global and `korea` for the Korea filtered path.

Generated reports:

- `reports/preprocessing_validation.csv`
- `reports/preprocessing_validation.md`

If the gate fails, inspect the reports and fix preprocessing before running model or simulation steps.

## Global Calibration Check

```bash
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/data/validate_preprocessing.py --scope global
python src/models/train_baseline.py \
  --features-path data/processed/features_global.csv \
  --run-name global_baseline
python src/models/calibrate.py \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_model.pkl \
  --run-name global_baseline
```

Calibration artifact check:

```bash
python - <<'PY'
from pathlib import Path

paths = [
    "models/global_baseline_calibrated_model.pkl",
    "reports/global_baseline_calibration_report/calibration_metrics.csv",
    "reports/global_baseline_calibration_report/calibration_curve.csv",
    "reports/global_baseline_calibration_report/summary.md",
    "models/calibrated_model.pkl",
    "reports/calibration_report/calibration_metrics.csv",
    "reports/calibration_report/calibration_curve.csv",
    "reports/calibration_report/summary.md",
]

for path in paths:
    p = Path(path)
    print(path, "OK" if p.exists() else "MISSING")
PY
```

## Data Skeleton Syntax Check

```bash
python -m json.tool data/tournament/participants.json
python -m json.tool data/tournament/schedule.json
python -m json.tool data/tournament/bracket.json
python - <<'PY'
import pandas as pd
pd.read_csv('data/mappings/team_name_mapping.csv')
print('team_name_mapping.csv is readable')
PY
```

## Team Mapping Validation

Run this after adding real raw match CSV files to `data/raw/`:

```bash
python src/data/validate_team_mapping.py
```

This creates generated data-quality reports:

- `reports/unmapped_teams.csv`
- `reports/team_mapping_validation.md`

These reports are local validation outputs and are not committed by default.

## CI and Local Smoke Test

### Generated artifact policy

Running `verify_mvp_pipeline.sh`, `./scripts/smoke_test.sh`, `scripts/validate_preprocessing_pipeline.sh`, the manual global pipeline commands, Korea filtered path commands, calibration commands, `src/data/validate_team_mapping.py`, or `src/data/validate_preprocessing.py` can refresh local generated artifacts. These files are reproducible outputs from the current code, data, and model run, so they are generally not committed:

- `data/processed/matches.csv`
- `data/processed/features.csv`
- `data/processed/matches_global.csv`
- `data/processed/features_global.csv`
- `models/baseline_model.pkl`
- `models/global_baseline_model.pkl`
- `models/calibrated_model.pkl`
- `models/global_baseline_calibrated_model.pkl`
- `reports/data_quality_summary.md`
- `reports/preprocessing_validation.csv`
- `reports/preprocessing_validation.md`
- `reports/baseline_metrics.csv`
- `reports/global_baseline_metrics.csv`
- `reports/calibration_report/`
- `reports/global_baseline_calibration_report/`
- `reports/prediction_table.csv`
- `reports/model_evaluation.md`
- `reports/smoke_test_report.md`
- `reports/unmapped_teams.csv`
- `reports/team_mapping_validation.md`

The `.gitkeep` files are placeholders that keep otherwise-empty directories in Git. By default, pull requests should include only source code, scripts, and README/documentation changes unless a reviewer explicitly asks for generated artifacts.

### Official smoke test

Run the official smoke test from the `main` branch so CI and local baseline results are reproducible:

```bash
git fetch origin main && git checkout main
./scripts/smoke_test.sh
```

The smoke test gate is intentionally limited to the reproducible Korea filtered path commands. Post-MVP features such as calibration, simulation, and Django must not be added as mandatory smoke test requirements until the team explicitly changes the acceptance criteria.

### Development quick check

For the full global + Korea preprocessing gate, run:

```bash
bash scripts/validate_preprocessing_pipeline.sh
```

For the primary global path, run:

1. `python src/data/build_dataset.py --global-scope`
2. `python src/features/make_features.py --target-scope home`
3. `python src/data/validate_preprocessing.py --scope global`
4. `python src/models/train_baseline.py --features-path data/processed/features_global.csv --run-name global_baseline`
5. `python src/models/calibrate.py --features-path data/processed/features_global.csv --model-path models/global_baseline_model.pkl --run-name global_baseline`
6. `python src/simulation/run_tournament.py`

## Global-first Deliverables

- Global processed match dataset
- Global model-ready feature table
- Preprocessing Validation Report
- Global baseline metrics
- Calibration report
- Calibrated prediction model
- Match probability table for simulation
- Simulation summary
- Champion probabilities
- Global dashboard / Django API if schedule allows

## Korea Filtered Deliverables

- Korea filtered data-quality report
- Korea filtered preprocessing validation report
- Korea filtered baseline model
- Korea filtered prediction table
- Streamlit demonstration path

## Limitations

- The built-in demo dataset is intentionally small and is only meant to prove that the local pipeline runs end to end.
- Team-name identifiers such as `home_team` and `away_team` can make demo metrics look better than they really are because a model may memorize team-specific outcomes instead of learning generalizable ranking or match-context signals.
- Global and Korea metrics should not be treated as production-ready claims until they are validated on larger historical datasets with time-aware splits and stronger leakage checks.
- Tournament JSON files are skeleton interfaces and must not be presented as official FIFA schedule, participant, or bracket data until source verification is complete.

## Post-MVP Improvements

- Replace the demo dataset with real historical international match results and FIFA rankings.
- Add rolling recent-form features, rest-days features, and tournament-context features.
- Use preprocessing validation before every major modeling, calibration, or simulation run.
- Use calibration metrics and calibration curves before tournament simulation.
- Add tournament simulation with fixed seed reproducibility.
- Add data governance checks before using sensitive, licensed, or API-based datasets.
