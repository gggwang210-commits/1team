# PROJECT_SPEC

## Project

2026 FIFA World Cup Prediction Model

## Current Primary Scope

The current primary scope is a global-first international football match prediction pipeline.

Primary outputs:

- Global match-level Win/Draw/Loss probabilities
- Global baseline metrics
- Calibrated match probabilities for simulation input
- Tournament-simulation-ready probability tables
- Group-stage and knockout simulation scaffolding
- Champion probabilities as a later simulation output

The Korea Republic path is preserved as a reproducible filtered use case and legacy smoke-test path. It is useful for demonstration, regression checks, and presentation examples, but it is not the main modeling scope.

## Current Evidence Status

As of the latest validation evidence, the project has moved beyond a pure skeleton stage.

Validated evidence currently recorded in the repository:

- Raw source validation was executed with `data/raw/international_results.csv`.
- Source validation result: PASS 6 / FAIL 0.
- Korea MVP processed matches: 1,007 rows.
- Global processed matches: 49,405 rows.
- Global feature output was generated and then corrected for one duplicate feature-row issue.
- Final preprocessing validation result after the duplicate-row fix: PASS 30 / FAIL 0.
- Generated raw, processed, report, and model artifacts remain outside version control by default.

Reference document:

- `docs/real_raw_validation_2026-06-12.md`

## Validation Boundary

The project should not present generated metrics, prediction tables, simulation summaries, or champion probabilities as final claims unless the relevant run evidence is recorded.

Current safe status wording:

> The project has a global-first ML pipeline with documented raw-source validation and preprocessing validation evidence. Korea Republic remains a reproducible filtered demonstration path. Tournament simulation is structurally prepared, but official FIFA rule verification and final model evidence are still required before making final prediction or champion-probability claims.

## Remaining Verification Tasks

The following items must remain explicit before final presentation or release:

1. Official FIFA competition regulations for group-stage tiebreakers.
2. Official FIFA ranking rules for best third-placed teams.
3. Official FIFA Round of 32 bracket mapping, including third-place qualifier combinations.
4. Team decision on whether source manifest candidate rows should remain `pending` or move to `verified`.
5. Reproducible global baseline and calibration metrics generated from the agreed data snapshot.
6. Explicit knockout draw-resolution policy for converting W/D/L probabilities into advancement probabilities.

## Data Scope

### Global Primary Path

- Full international match-result dataset where available
- Standardized global processed match table
- Home-team perspective `Win` / `Draw` / `Loss` target labels
- Country/team-name mapping table for canonical names, FIFA codes, and historical aliases
- Tournament participant, schedule, and bracket interface files

### Korea Filtered Path

- Korea Republic matches only
- Korea Republic perspective target labels
- Lightweight fallback/demo data only for smoke-test resilience
- Presentation/demo use case, not the primary global model claim

## Data Sources

Candidate and current sources:

- International Football Results (`martj42/international_results`) for historical match results
- FIFA ranking or rating sources for team-strength features
- 2026 tournament participants, schedule, and bracket interface files
- Public football APIs only when terms, coverage, and data version are clear

All source rows should keep source URL, owner, license/terms status, download date, expected columns, use case, and verification status in the raw manifest or related source documentation.

## Baseline Models

Implemented / near-term baseline:

- Logistic Regression
- Random Forest

Expansion candidates:

- Ranking/context-only global baseline
- Team-identifier comparison baseline for memorization-risk review
- Calibrated model using Platt Scaling or Isotonic Regression
- XGBoost / LightGBM only after validation gates and baseline evidence are stable

## Evaluation

Core metrics:

- Accuracy
- Macro F1
- Log Loss
- One-vs-rest multiclass Brier Score

Required evaluation safeguards:

- Source validation before preprocessing
- Preprocessing validation before modeling
- Leakage checks against final-score columns
- Time-aware split where data allows
- Calibration curve and calibrated vs. uncalibrated metric comparison before tournament simulation

## Deliverables

Current evidence and interface deliverables:

- `docs/real_raw_validation_2026-06-12.md`
- `data/mappings/team_name_mapping.csv`
- `data/tournament/participants.json`
- `data/tournament/schedule.json`
- `data/tournament/bracket.json`
- Source and preprocessing validation scripts
- Korea filtered smoke-test path
- Global-first pipeline commands documented in README/runbooks

Generated deliverables, not committed by default:

- Processed match and feature tables
- Baseline model files
- Calibration model files
- Metrics reports
- Prediction tables
- Simulation summaries
- Champion probability outputs

## Implementation Phases

### Phase 1: Evidence-aligned Data Foundation

- Preserve Korea filtered smoke-test path.
- Maintain global-first dataset and feature pipeline.
- Keep source validation and preprocessing validation as mandatory gates.
- Keep generated artifacts out of version control unless reviewers explicitly request otherwise.

### Phase 2: Model and Calibration Evidence

- Train global baseline models from an agreed validated data snapshot.
- Compare ranking/context-only features against team identifiers.
- Add probability calibration.
- Record reproducible calibration metrics and curve summaries.

### Phase 3: Simulation and Service

- Verify FIFA group ranking, third-place ranking, and Round of 32 bracket rules.
- Define knockout draw-resolution policy.
- Generate simulation summary and champion probabilities with a fixed random seed.
- Decide whether Streamlit, Django API, or both are feasible within the project schedule.

## Instructions For Codex

Always preserve the Korea filtered smoke-test path unless the team explicitly decides to replace it.

Default priority order:

Source Validation
→ Preprocessing Validation
→ Data Quality Evidence
→ Feature Engineering
→ Baseline Modeling
→ Evaluation
→ Calibration
→ Prediction Table
→ Simulation
→ Dashboard/API

Do not upgrade `pending` or `web-verified` source statuses to `verified` without an explicit team decision and documented official-source review.
