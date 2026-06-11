# PROJECT_SPEC

## Project

2026 FIFA World Cup Prediction Model

## Current MVP Scope

The current MVP predicts Korea Republic group-stage match outcomes.

Outputs:

- Korea Republic Win Probability
- Korea Republic Draw Probability
- Korea Republic Loss Probability

Target definition: `Win`, `Draw`, and `Loss` are always from Korea Republic's perspective, regardless of whether Korea Republic is home or away.

## Expansion Scope

The first expansion target is to move from a Korea-only MVP toward a global 2026 FIFA World Cup prediction system.

Expansion outputs:

- Match-level Win/Draw/Loss probabilities for all target fixtures
- Calibrated match probabilities for simulation input
- Group-stage advancement probabilities
- Knockout-round advancement probabilities
- Champion probabilities
- Korea Republic dashboard view as an application case filtered from the global model

## Data Scope

### MVP

- Korea Republic matches only
- Korea Republic perspective target labels
- Lightweight demo data fallback when no compatible raw CSV exists

### Expansion

- Full international match-result dataset where available
- Standardized global `matches.csv`
- Team-name mapping table for country names, FIFA codes, and historical aliases
- 2026 tournament participants, schedule, and bracket data as versioned input files

## Data Sources

Candidate sources:

- International Football Results
- FIFA Rankings
- FIFA World Cup Data
- Kaggle datasets as auxiliary sources
- Public football APIs only when the usage terms and data version are clear

## Baseline Models

Implemented / MVP baseline:

- Logistic Regression
- Random Forest

Expansion candidates:

- Global baseline model
- Calibrated model using Platt Scaling or Isotonic Regression
- Ranking/context-only model for generalization comparison
- Team-identifier model for controlled memorization-risk comparison

## Evaluation

Implemented baseline metrics:

- Accuracy
- Macro F1
- Log Loss
- One-vs-rest multiclass Brier Score

Expansion evaluation additions:

- Calibration curve
- Calibrated vs. uncalibrated Log Loss comparison
- Calibrated vs. uncalibrated Brier Score comparison
- Time-aware leakage checks where data allows

## Deliverables

MVP deliverables:

- Data Quality Report
- Baseline Model
- Prediction Table
- Streamlit Demo

Expansion deliverables:

- `data/mappings/team_name_mapping.csv`
- `data/tournament/participants.json`
- `data/tournament/schedule.json`
- `data/tournament/bracket.json`
- `reports/calibration_report/`
- `reports/simulation_summary.csv`
- `reports/champion_probabilities.csv`
- Global dashboard or Django API, depending on schedule feasibility

## Implementation Phases

### Phase 1: Data Expansion

- Keep the existing Korea MVP path reproducible.
- Add an optional global dataset path using `filter_korea=False`.
- Add mapping and tournament input directories.
- Document the expansion strategy in `docs/`.

### Phase 2: Model Expansion

- Train global baseline models.
- Compare ranking/context-only features against team identifiers.
- Add probability calibration.
- Generate calibrated prediction tables.

### Phase 3: Simulation and Service

- Add group-stage and knockout simulation.
- Generate champion probabilities with a fixed random seed.
- Decide whether Django implementation is feasible within the project schedule.

## Instructions For Codex

Always preserve the current MVP smoke-test path unless the team explicitly decides to replace it.

Default priority order:

Data Quality
→ Feature Engineering
→ Modeling
→ Evaluation
→ Prediction Table
→ Streamlit Demo
→ Calibration
→ Simulation
→ Django/API
