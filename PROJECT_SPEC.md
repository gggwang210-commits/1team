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

MVP does not directly classify champion teams or run a tournament simulator.
Post-MVP tournament simulation should remain a lightweight extension in this
order: match probabilities → group simulation → knockout simulation → champion
probability.

## Data Sources

- International Football Results (Kaggle)
- FIFA Rankings
- FIFA World Cup Data

## Baseline Models

- Logistic Regression
- Random Forest

## Evaluation

MVP implemented metrics:

- Accuracy
- Macro F1

The MVP pipeline writes these run-specific metrics to `reports/baseline_metrics.csv`
and summarizes them in `reports/model_evaluation.md`. Generated report files are
not committed, so this spec should not include fixed performance claims unless
they come from a clearly identified pipeline run, dataset, split strategy, and
commit.

Later extension / nice to have after probability calibration:

- Log Loss
- Brier Score

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
