# 2026 FIFA World Cup Prediction Model

## Team Project

Machine Learning based prediction system for:

- Korea Republic group stage matches
- Round of 32 qualification probability
- World Cup tournament simulation

## MVP Scope

The current MVP focuses on predicting Korea Republic group-stage match outcome probabilities:

- Win Probability
- Draw Probability
- Loss Probability

Later phases may expand to Round of 32 qualification probability and full tournament simulation.

## Stack

- Python
- Pandas
- Scikit-learn
- Streamlit

## Status

Research & MVP Phase

## MVP Data Flow

The implemented MVP pipeline now has three explicit stages:

1. `src/data/build_dataset.py` standardizes international match-result data and writes `data/processed/matches.csv`.
   - If no compatible raw CSV exists in `data/raw/`, it creates a built-in demo dataset.
   - The demo dataset has 15 labeled rows and three target classes so baseline training can run locally.
2. `src/features/make_features.py` converts processed match rows into model-ready pre-match features and writes `data/processed/features.csv`.
   - Final scores are used only to create `target_result`.
   - Score/result leakage columns are not included as model features.
3. `src/models/train_baseline.py` validates the feature table before model fitting.
   - Supported target columns: `target_result` or `target`.
   - Minimum requirements: at least two target classes, at least one non-empty usable feature column, at least two rows per class, and enough rows for the configured train/test split.
   - With the default 20% split and three classes, the MVP needs at least 15 labeled rows.

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

7. Evaluate baseline models.

   ```bash
   python src/models/evaluate.py
   ```

8. Launch the Streamlit demo.

   ```bash
   streamlit run app/streamlit_app.py
   ```

## CI and Local Smoke Test

Run smoke tests from the `main` branch so CI and local results are reproducible.
Fetch and check out `main` immediately before the smoke test, then run the wrapper:

```bash
git fetch origin main && git checkout main
./scripts/smoke_test.sh
```

The smoke test wrapper intentionally fails before running project commands when a
local `main` branch is missing. This prevents accidentally validating a feature
branch or a detached checkout as the MVP baseline.

The wrapper writes `reports/smoke_test_report.md` and records:

- execution branch
- commit hash
- start and finish timestamps in UTC
- smoke test status
- failed command, when applicable
- commands executed

The wrapper executes the MVP pipeline in order:

1. `python src/data/build_dataset.py`
2. `python src/features/make_features.py`
3. `python src/models/train_baseline.py`
4. `python src/models/evaluate.py`

## MVP Deliverables

- Data Quality Report
- Baseline Model
- Prediction Table
- Streamlit Demo

## Suggested Improvements

- Replace the demo dataset with real historical international match results and FIFA rankings.
- Add rolling recent-form features, rest-days features, and tournament-context features.
- Add probability calibration and report Log Loss/Brier Score alongside Accuracy and Macro F1.
- Add data governance checks before using any sensitive or licensed datasets.
