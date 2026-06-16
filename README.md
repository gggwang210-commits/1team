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

## Reproducibility Evidence Path

This repository is organized to connect presentation numbers with reproducible GitHub evidence.

Stable command:

```bash
python src/run_model_comparison.py --config configs/model_comparison.yaml
```

Reference metrics file:

```text
outputs/model_comparison_metrics.csv
```

Current model interpretation:

- Soft Voting is the current main probability model candidate.
- Poisson is an auxiliary expected score explanation model.
- Full tournament simulation and champion probability are later-stage outputs, not final presentation conclusions until rule logic is verified.

## Current Reference Metrics

These values are synced from the latest Drive review document dated 2026-06-16.

| Model | Accuracy | Macro-F1 | Log Loss | Brier Score | Role |
|---|---:|---:|---:|---:|---|
| Soft Voting | 0.6465 | 0.5273 | 0.8000 | 0.4668 | Main probability model candidate |
| Logistic Full | 0.6450 | 0.5148 | 0.8058 | 0.4683 | Strong linear baseline |
| XGBoost | 0.6452 | 0.5286 | 0.8073 | 0.4698 | Nonlinear candidate |
| Stacking | 0.6430 | N/A | 0.8060 | N/A | Limited gain relative to complexity |
| LightGBM | 0.6392 | 0.5366 | 0.8135 | 0.4720 | Fast training candidate |
| Poisson | 0.6332 | 0.4674 | 0.8161 | 0.4751 | Score explanation auxiliary |
| Logistic Elo-only | 0.6261 | 0.4621 | 0.8290 | 0.4834 | Elo baseline |
| Random Forest | 0.6147 | 0.5660 | 0.8415 | 0.4931 | Draw sensitivity reference |

## Latest Drive Sync Notes

The latest Drive review states that all reviewed models used the same train/validation split and 52-feature contract. It also identifies draw prediction as a common weak point and recommends follow-up work on hyperparameter tuning, feature-importance interpretation, Poisson score-combination logic, Korea scenario analysis, and draw improvement.

GitHub tracking document:

```text
docs/drive_sync_latest_model_results_2026-06-16.md
```

## Global-first Project Scope

The current priority is to build a global match-level prediction pipeline that can estimate Win/Draw/Loss probabilities for international football fixtures.

Primary output concept:

- Home-team Win Probability
- Draw Probability
- Home-team Loss Probability

For Korea Republic views, predictions can be filtered and reinterpreted as a Korea application case when Korea Republic appears as either `home_team` or `away_team`.

The global pipeline does not directly claim official 2026 FIFA World Cup results. Later phases expand in this order:

match probabilities -> probability calibration -> group simulation -> knockout simulation -> champion probability.

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
