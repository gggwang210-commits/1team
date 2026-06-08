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

## How to Run the MVP Later

The full modeling logic is not implemented yet. After data preparation and baseline modeling are added, the intended workflow is:

1. Create and activate a Python virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Add raw datasets to `data/raw/`.

   Expected MVP data sources:

   - International Football Results
   - FIFA Rankings
   - FIFA World Cup Data

4. Run the data pipeline.

   ```bash
   python src/data/build_dataset.py
   ```

5. Train baseline models.

   ```bash
   python src/models/train_baseline.py
   ```

6. Evaluate baseline models.

   ```bash
   python src/models/evaluate.py
   ```

7. Launch the Streamlit demo.

   ```bash
   streamlit run app/streamlit_app.py
   ```

## MVP Deliverables

- Data Quality Report
- Baseline Model
- Prediction Table
- Streamlit Demo
