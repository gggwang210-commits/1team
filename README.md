# 2026 FIFA World Cup Prediction Model

## Team Project

Machine Learning based prediction system for Korea Republic outcomes.

Current MVP:

- Korea Republic match-level Win/Draw/Loss probabilities

Extension Goals:

- Round of 32 qualification probability
- World Cup tournament simulation
- Champion probability

This repository currently focuses on match-level outcomes first, not champion classification.

## MVP Scope

The current MVP focuses on predicting Korea Republic group-stage match outcome probabilities:

- Korea Republic Win Probability
- Korea Republic Draw Probability
- Korea Republic Loss Probability

All MVP labels and predictions use **Korea Republic's perspective**. For example,
`Win` means Korea Republic wins the match, regardless of whether Korea Republic
is listed as the home or away team.

MVP does not directly classify champion teams or run a tournament simulator.
Later phases may expand tournament simulation only in this lightweight order:
match probabilities → group simulation → knockout simulation → champion probability.

### Target column contract

The project intentionally uses result labels from different perspectives at
different pipeline stages. Keep this contract explicit to avoid target leakage
or accidentally training on the wrong label:

- `matches.csv.target_result` = home-team perspective result label.
- `matches.csv.target_result_korea_perspective` = Korea Republic perspective result label.
- `features.csv.target_result` = model target sourced from Korea Republic perspective.
- `features.csv.target_result_korea_perspective` = retained audit copy of the Korea Republic perspective target, excluded from every model input feature set.

`src/models/train_baseline.py` treats `features.csv.target_result` as the only
modeling target and excludes every target/result/score-like column from the
feature matrix before preprocessing and training.

## Stack

- Python
- Pandas
- Scikit-learn
- Streamlit

## Status

Research & MVP Phase

## MVP Data Flow

The implemented MVP pipeline now has five explicit stages:

Generated report files are intentionally not committed. Running the pipeline recreates `reports/data_quality_summary.md`, `reports/baseline_metrics.csv`, `reports/prediction_table.csv`, `reports/model_evaluation.md`, and `reports/smoke_test_report.md` from the current code, data, and model artifacts. Treat those files as local evidence for the current run rather than authoritative checked-in model results.

1. `src/data/build_dataset.py` standardizes international match-result data and writes `data/processed/matches.csv`.
   - If no compatible raw CSV exists in `data/raw/`, it creates a built-in demo dataset.
   - The demo dataset has 15 labeled rows and three target classes so baseline training can run locally.
   - Full international raw datasets are filtered to rows where Korea Republic is either `home_team` or `away_team`.
   - `target_result` is the score-derived home-team perspective label.
   - `target_result_korea_perspective` is the MVP label. It matches `target_result` when Korea Republic is the home team, reverses home `Win`/`Loss` when Korea Republic is the away team, and keeps `Draw` unchanged.
   - `reports/data_quality_summary.md` is generated with row count, missing counts, and target distribution for a quick MVP sanity check.
2. `src/features/make_features.py` converts processed match rows into model-ready pre-match features and writes `data/processed/features.csv`.
   - Final scores are used only to create result labels.
   - The training target is explicitly selected from `target_result_korea_perspective` and saved as `target_result` in the feature table for a stable modeling schema.
   - `target_result_korea_perspective` is also retained in `features.csv` as an audit column so reviewers can verify that the modeling target came from the Korea Republic perspective.
   - Score/result leakage columns are not included as model features.
3. `src/models/train_baseline.py` validates the feature table before model fitting.
   - Supported target column: `target_result`, defined as Korea Republic-perspective Win/Draw/Loss.
   - The audit column `target_result_korea_perspective` must match `target_result` when present, but it is excluded from all model input feature sets.
   - Minimum requirements: at least two target classes, at least one non-empty usable feature column, at least two rows per class, and enough rows for the configured train/test split.
   - With the default 20% split and three classes, the MVP needs at least 15 labeled rows.
   - Baseline metrics are recorded for two explicit feature sets: `ranking_context_only` excludes `home_team` and `away_team`, while `with_team_identifiers` keeps those team-name identifiers for comparison.
   - Implemented metrics include Accuracy, Macro F1, Log Loss, and one-vs-rest multiclass Brier Score. Log Loss and Brier Score are calculated from test-set `predict_proba` outputs, so they evaluate probability quality rather than only the final class label.

## Project Structure

```text
.
├── app/
│   └── streamlit_app.py              # Streamlit MVP application entry point
├── data/
│   ├── interim/                      # Intermediate cleaned data files
│   │   └── .gitkeep
│   ├── processed/                    # Model-ready datasets
│   │   └── .gitkeep
│   └── raw/                          # Original downloaded datasets
│       └── .gitkeep
├── models/                           # Saved baseline model artifacts
│   └── .gitkeep
├── notebooks/
│   ├── 01_data_quality_check.ipynb   # Data quality exploration notebook
│   ├── 02_feature_engineering.ipynb  # Feature engineering exploration notebook
│   └── 03_baseline_modeling.ipynb    # Baseline modeling exploration notebook
├── reports/                          # Runtime-generated reports; only .gitkeep is tracked
│   └── .gitkeep
├── scripts/
│   └── smoke_test.sh                 # Main-branch smoke test wrapper
├── src/
│   ├── data/
│   │   ├── build_dataset.py          # Dataset assembly and train/test split helpers
│   │   ├── clean_data.py             # Data cleaning helpers
│   │   └── load_data.py              # Raw data loading helpers
│   ├── features/
│   │   └── make_features.py          # MVP feature engineering helpers
│   ├── models/
│   │   ├── evaluate.py               # Model evaluation helpers
│   │   ├── predict.py                # Prediction helpers
│   │   └── train_baseline.py         # Baseline model training entry point
│   └── utils/
│       └── config.py                 # Shared configuration values
├── PROJECT_SPEC.md
├── README.md
├── requirements.txt
└── .gitignore
```

## How to Run the MVP

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

   Expected MVP data sources:

   - International Football Results
   - FIFA Rankings
   - FIFA World Cup Data

   If no compatible raw CSV is present, the MVP uses a small built-in demo dataset for local pipeline testing.

4. Build the processed match dataset.

   ```bash
   python src/data/build_dataset.py
   ```

5. Create model-ready features.

   ```bash
   python src/features/make_features.py
   ```

6. Train baseline models.

   ```bash
   python src/models/train_baseline.py
   ```

   This step generates `reports/baseline_metrics.csv` locally. The file is ignored by Git because it is a reproducible pipeline artifact, not an authoritative checked-in model result.

7. Generate the required prediction table.

   `src/models/predict.py` must run before `src/models/evaluate.py` in the MVP workflow. Evaluation treats `reports/prediction_table.csv` as a required local artifact, so it will fail if predictions are missing or empty. The generated prediction table is ignored by Git and should be recreated from the current code, data, and model artifacts.

   ```bash
   python src/models/predict.py
   ```

8. Evaluate baseline models.

   ```bash
   python src/models/evaluate.py
   ```

   This step generates `reports/model_evaluation.md` locally from the current metrics and prediction-table artifacts.

9. Launch the Streamlit demo.

   ```bash
   streamlit run app/streamlit_app.py
   ```

## CI and Local Smoke Test

The project has one official smoke-test entry point and one manual development
quick check. Both execute the same five MVP pipeline commands, but they are not
interchangeable:

- **Official smoke test:** `./scripts/smoke_test.sh` is the required wrapper for
  CI and reproducible `main` branch validation.
- **Development quick check:** the five individual Python commands are a
  feature-branch sanity check for local development only.

### Official smoke test

Run the official smoke test from the `main` branch so CI and local baseline
results are reproducible. Fetch and check out `main` immediately before the
smoke test, then run the wrapper:

```bash
git fetch origin main && git checkout main
./scripts/smoke_test.sh
```

The smoke test wrapper intentionally fails before running project commands when a
local `main` branch is missing or when the current branch is not `main`. This
policy prevents accidentally validating a feature branch or a detached checkout
as the MVP baseline. Use this wrapper, not the manual commands below, when
validating the main branch baseline before or after merge.

The wrapper writes `reports/smoke_test_report.md` as a local generated artifact and records:

- execution branch
- commit hash
- start and finish timestamps in UTC
- smoke test status
- failed command, when applicable
- commands executed

If the official smoke test fails, inspect these generated artifacts in order:

1. `reports/smoke_test_report.md` for the branch, commit, status, failed
   command, and command list captured by the wrapper.
2. `reports/data_quality_summary.md` for dataset-build output and input-data
   quality checks.
3. `data/processed/matches_features.csv` for the engineered feature table used
   by training and prediction.
4. `models/baseline_model.joblib` for the trained baseline model artifact.
5. `reports/baseline_metrics.csv` for training-time model metrics.
6. `reports/prediction_table.csv` for prediction output required by evaluation.
7. `reports/model_evaluation.md` for the final evaluation summary.

### Development quick check

During feature development, you may manually run the five individual commands
below from your feature branch for a fast local sanity check. This is useful
before opening a pull request, but it does not replace the official `main`
branch smoke test above because it skips the wrapper's branch and report
metadata guardrails. Treat these commands as a developer convenience only; CI
and main branch verification should continue to use `./scripts/smoke_test.sh`.

Run the MVP pipeline in order:

1. `python src/data/build_dataset.py`
2. `python src/features/make_features.py`
3. `python src/models/train_baseline.py`
4. `python src/models/predict.py`
5. `python src/models/evaluate.py`

## MVP Deliverables

- Data Quality Report (notebook/manual check currently; minimal summary generated at `reports/data_quality_summary.md` by `python src/data/build_dataset.py`)
- Baseline Model
- Prediction Table
- Streamlit Demo

## MVP Limitations

- The built-in demo dataset is intentionally small and is only meant to prove that the local pipeline runs end to end.
- Team-name identifiers such as `home_team` and `away_team` can make demo metrics look better than they really are because a model may memorize team-specific outcomes instead of learning generalizable ranking or match-context signals. After running the pipeline, compare `ranking_context_only` against `with_team_identifiers` in the locally generated `reports/baseline_metrics.csv` before interpreting baseline performance.
- MVP metrics should not be treated as production-ready claims until they are validated on larger historical datasets with time-aware splits and stronger leakage checks.

## Suggested Improvements

- Replace the demo dataset with real historical international match results and FIFA rankings.
- Add rolling recent-form features, rest-days features, and tournament-context features.
- Add probability calibration and compare calibrated vs. uncalibrated Log Loss/Brier Score alongside Accuracy and Macro F1.
- Add data governance checks before using any sensitive or licensed datasets.
