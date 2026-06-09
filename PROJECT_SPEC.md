# PROJECT_SPEC

## Project

2026 FIFA World Cup Prediction Model

## MVP

Predict Korea Republic group-stage match outcomes.

Outputs:

- Korea Republic Win Probability
- Korea Republic Draw Probability
- Korea Republic Loss Probability

Target definition: `Win`, `Draw`, and `Loss` are always from Korea Republic's
perspective, regardless of whether Korea Republic is home or away.

## Data Sources

- International Football Results (Kaggle)
- FIFA Rankings
- FIFA World Cup Data

## Baseline Models

- Logistic Regression
- Random Forest

## Evaluation

Implemented baseline metrics:

- Accuracy
- Macro F1
- Log Loss
- One-vs-rest multiclass Brier Score

## Deliverables

- Data Quality Report
- Baseline Model
- Prediction Table
- Streamlit Demo

## Instructions For Codex

Always prioritize MVP completion.

Data Quality
→ Feature Engineering
→ Modeling
→ Evaluation
→ Visualization
→ Streamlit
