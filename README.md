# 2026 FIFA World Cup Prediction Model

## Team Project

Machine Learning based prediction system for:

- Korea Republic group stage matches
- Round of 32 qualification probability
- World Cup tournament simulation

## MVP Scope

The current MVP focuses on predicting Korea Republic group-stage match outcome probabilities:

- Korea Republic Win Probability
- Korea Republic Draw Probability
- Korea Republic Loss Probability

All MVP labels and predictions use **Korea Republic's perspective**. For example,
`Win` means Korea Republic wins the match, regardless of whether Korea Republic
is listed as the home or away team.

Later phases may expand to Round of 32 qualification probability and full tournament simulation.

## Stack

- Python
- Pandas
- Scikit-learn
- Streamlit

## Status

Research & MVP Phase

## MVP Data Flow

The implemented MVP pipeline now has five explicit stages:

1. `src/data/build_dataset.py` standardizes international match-result data and writes `data/processed/matches.csv`.
   - If no compatible raw CSV exists in `data/raw/`, it creates a built-in demo dataset.
   - The demo dataset has 15 labeled rows and three target classes so baseline training can run locally.
   - Full international raw datasets are filtered to rows where Korea Republic is either `home_team` or `away_team`.
   - `target_result` is the score-derived home-team perspective label.
   - `target_result_korea_perspective` is the MVP label. It matches `target_result` when Korea Republic is the home team, reverses home `Win`/`Loss` when Korea Republic is the away team, and keeps `Draw` unchanged.
2. `src/features/make_features.py` converts processed match rows into model-ready pre-match features and writes `data/processed/features.csv`.
   - Final scores are used only to create result labels.
   - The training target is explicitly selected from `target_result_korea_perspective` and saved as `target_result` in the feature table for a stable modeling schema.
   - Score/result leakage columns are not included as model features.
3. `src/models/train_baseline.py` validates the feature table before model fitting.
   - Supported target column: `target_result`, defined as Korea Republic-perspective Win/Draw/Loss.
   - Minimum requirements: at least two target classes, at least one non-empty usable feature column, at least two rows per class, and enough rows for the configured train/test split.
   - With the default 20% split and three classes, the MVP needs at least 15 labeled rows.
   - Baseline metrics are recorded for two explicit feature sets: `ranking_context_only` excludes `home_team` and `away_team`, while `with_team_identifiers` keeps those team-name identifiers for comparison.

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
├── reports/                          # Data quality, evaluation, and prediction reports
│   └── .gitkeep
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

7. Generate the required prediction table.

   `src/models/predict.py` must run before `src/models/evaluate.py` in the MVP workflow. Evaluation now treats `reports/prediction_table.csv` as a required artifact, so it will fail if predictions are missing or empty.

   ```bash
   python src/models/predict.py
   ```

8. Evaluate baseline models.

   ```bash
   python src/models/evaluate.py
   ```

9. Launch the Streamlit demo.

   ```bash
   streamlit run app/streamlit_app.py
   ```

## MVP Deliverables

- Data Quality Report
- Baseline Model
- Prediction Table
- Streamlit Demo

## MVP Limitations

- The built-in demo dataset is intentionally small and is only meant to prove that the local pipeline runs end to end.
- Team-name identifiers such as `home_team` and `away_team` can make demo metrics look better than they really are because a model may memorize team-specific outcomes instead of learning generalizable ranking or match-context signals. Compare `ranking_context_only` against `with_team_identifiers` in `reports/baseline_metrics.csv` before interpreting baseline performance.
- MVP metrics should not be treated as production-ready claims until they are validated on larger historical datasets with time-aware splits and stronger leakage checks.

## Suggested Improvements

- Replace the demo dataset with real historical international match results and FIFA rankings.
- Add rolling recent-form features, rest-days features, and tournament-context features.
- Add probability calibration and report Log Loss/Brier Score alongside Accuracy and Macro F1.
- Add data governance checks before using any sensitive or licensed datasets.
