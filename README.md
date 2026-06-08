# 2026 FIFA World Cup Prediction Model

## Team Project

Machine Learning based prediction and simulation system for the 2026 FIFA World Cup.

The final MVP direction is broader than a single Korea Republic group-stage prediction table. The system will combine match-level Win/Draw/Loss prediction with group-stage and knockout-stage simulation to estimate Korea Republic advancement probability, champion probability, and likely upset scenarios.

## Final MVP Scope

The MVP includes:

- Match Win/Draw/Loss prediction
- Group stage simulation
- Knockout stage simulation
- Korea Republic advancement probability
- Champion probability estimation
- Upset analysis
- SHAP feature importance analysis
- Streamlit demo for communication and presentation

## Tournament Format Assumption

The project assumes the 2026 FIFA World Cup format:

- 48 teams
- 12 groups of four teams
- Three group-stage matches per team
- Top two teams from each group advance to the Round of 32
- Eight best third-place teams also advance to the Round of 32
- Single-elimination knockout stage from Round of 32 to Final

If official fixtures, draw details, or tie-breaker rules change, the simulation module and reports must be updated before final submission.

## Main Outputs

### Match Prediction

For each target match, the model outputs:

- Win Probability
- Draw Probability
- Loss Probability

These probabilities are used directly by the group-stage simulator and transformed into team-vs-team advancement probabilities for knockout simulation.

### Baseline Feature and Target Flow

The MVP baseline uses a team-perspective long-form feature table:

1. `data/processed/matches.csv` stores match-level results in `target_result`.
2. `python src/features/make_features.py` expands home/away matches into one row per team and writes `data/processed/features.csv`.
3. `target_result` is preserved as the original match-level result, while `team_result` is the training label from the current row's team perspective. Away rows flip Win/Loss and keep Draw unchanged.
4. `python src/models/train_baseline.py` trains a 3-class classifier on `team_result` and saves `models/baseline_model.pkl` plus `reports/baseline_metrics.csv`.
5. `python src/models/predict.py` writes `reports/prediction_table.csv` with stable `Win`, `Draw`, and `Loss` probability columns.

### Group Stage Simulation

The group-stage simulator should produce:

- Expected points by team
- Probability of finishing 1st, 2nd, 3rd, or 4th
- Round of 32 qualification probability
- Korea Republic group-stage advancement probability
- Group table simulation summary

### Knockout Stage Simulation

The knockout-stage simulator should produce:

- Probability of reaching each knockout round
- Final appearance probability
- Champion probability estimation
- Korea Republic round-by-round advancement probability

Because knockout matches cannot end in a draw, the simulator must document how regular-time draw probabilities are converted into advancement probabilities, such as normalized non-draw probability or an overtime/penalty proxy.

### Korea Republic Focus

Korea Republic is the primary analysis story for the demo and final presentation.

Required Korea Republic outputs:

- Group match Win/Draw/Loss probabilities
- Expected group-stage points
- Round of 32 qualification probability
- Knockout round advancement probabilities when bracket simulation is available
- Main features driving Korea Republic predictions
- Upset opportunities and upset risks

### Champion Probability

The project estimates champion probability through repeated full-tournament simulations.

Champion probability tables should include:

- Team
- Champion probability
- Final probability
- Round-by-round advancement probabilities
- Number of simulations
- Model/data version notes

### Upset Analysis

Upset analysis highlights matches where an underdog has a meaningful chance to win or advance.

Suggested upset definitions:

- Large FIFA ranking gap
- Large Elo/rating gap, if available
- Lower baseline win probability but meaningful underdog chance
- Korea Republic-specific upset opportunity or upset risk

### SHAP Feature Importance

SHAP analysis is used to explain model behavior.

Expected explainability outputs:

- Global feature importance summary
- Local explanation for selected Korea Republic matches
- Interpretation notes for major features

SHAP should be described as model interpretation, not causal evidence.

## Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- SHAP
- Streamlit

Optional, if time allows:

- XGBoost or LightGBM
- Plotly or Altair for interactive charts

## Data Sources

Initial candidate sources:

- International Football Results
- FIFA Rankings
- FIFA World Cup historical match data

Optional enrichment sources:

- Elo ratings
- Squad market value
- Injuries and squad availability
- Recent form and schedule data
- Confederation and tournament metadata

All external data must be checked for licensing, freshness, join keys, and leakage risk.

## Team Workflow

### Role Examples

- Data collection / cleaning
- Feature engineering
- Match modeling
- Simulation modeling
- Evaluation and calibration
- SHAP / explainability
- Streamlit demo
- Presentation/report

### Milestones

| Milestone | Owner | Expected Output | Due Date |
| --- | --- | --- | --- |
| Data quality check | TBD | Data quality report with missing values, duplicates, leakage risks, and dataset readiness notes | TBD |
| Feature table v1 | TBD | Model-ready feature table for baseline experiments | TBD |
| Match model v1 | TBD | Win/Draw/Loss Logistic Regression and/or Random Forest baseline model artifacts | TBD |
| Evaluation report | TBD | Accuracy, Macro F1, Log Loss, Brier Score, calibration notes, confusion matrix, and interpretation notes | TBD |
| Group simulation v1 | TBD | Reproducible group-stage Monte Carlo simulation with qualification probabilities | TBD |
| Knockout simulation v1 | TBD | Reproducible Round of 32 to Final simulation with round-by-round probabilities | TBD |
| Korea Republic report | TBD | Korea Republic group and knockout advancement probability summary | TBD |
| Champion probability table | TBD | Team-level champion and final probability estimates | TBD |
| Upset analysis | TBD | Top upset candidates and Korea Republic upset opportunity/risk notes | TBD |
| SHAP analysis | TBD | Global and selected local feature importance explanations | TBD |
| Streamlit MVP | TBD | Runnable Streamlit demo showing Korea Republic predictions, simulation outputs, champion probability, upset analysis, and SHAP summary | TBD |
| Final presentation | TBD | Final slide deck/report summarizing problem, data, model, simulation, results, risks, demo, and next steps | TBD |

## Revised MVP Deliverables

- Data Quality Report
- Feature Table v1
- Match Win/Draw/Loss Baseline Model
- Model Evaluation Report
- Group Stage Simulation Module
- Knockout Stage Simulation Module
- Korea Republic Advancement Probability Report
- Champion Probability Estimation Table
- Upset Analysis Report
- SHAP Feature Importance Analysis
- Streamlit Demo
- Final Presentation / Project Report

## Success Metrics

The MVP is successful when it can:

- Generate valid Win/Draw/Loss probabilities for target matches
- Run group-stage simulations reproducibly with a fixed random seed
- Estimate Korea Republic Round of 32 qualification probability
- Run knockout-stage simulations and produce round-by-round probabilities
- Estimate champion probability for all modeled teams
- Show at least one upset analysis table
- Show SHAP global feature importance or a documented explainability fallback
- Report Accuracy, Log Loss, Brier Score, and calibration notes
- Run with documented commands from data preparation to Streamlit demo
- Communicate assumptions and limitations clearly in the final report

## Risks and Limitations

- Data freshness: rankings, squads, injuries, fixtures, and form can change before the tournament.
- Data leakage: features must only use information available before each predicted match.
- Sample size: World Cup match history is limited, so estimates may be unstable.
- Probability calibration: accurate class prediction does not guarantee reliable probabilities.
- Tournament format complexity: third-place qualification and bracket mapping increase simulation risk.
- Knockout modeling: regular-time draw probabilities require additional assumptions for extra time and penalties.
- SHAP interpretation: SHAP explains model behavior, not real-world causality.
- External variables: injuries, tactics, weather, travel, and squad rotation may be missing or incomplete.
- Communication risk: probabilities must be presented as estimates, not guarantees.
- Scope risk: full simulation and explainability can delay MVP completion if baseline data/model work is not finished first.

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
├── reports/                          # Data quality, evaluation, simulation, and prediction reports
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

The full modeling logic is not implemented yet. After data preparation, baseline modeling, simulation, and explainability modules are added, the intended workflow is:

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

5. Train match Win/Draw/Loss baseline models.

   ```bash
   python src/models/train_baseline.py
   ```

6. Evaluate baseline models.

   ```bash
   python src/models/evaluate.py
   ```

7. Generate match predictions and simulation outputs.

   ```bash
   python src/models/predict.py
   ```

8. Launch the Streamlit demo.

   ```bash
   streamlit run app/streamlit_app.py
   ```
