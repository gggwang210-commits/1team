# PROJECT_SPEC

## Project

2026 FIFA World Cup Prediction Model

## Current Primary Scope

The current primary scope is a global-first international football match prediction pipeline with a focused 2026 World Cup application layer.

Primary outputs:

- Global match-level Win/Draw/Loss probabilities
- Model-comparison evidence across multiple classifiers
- Soft Voting probability output as the current main model candidate
- Poisson expected-scoreline output as a companion explanation layer
- Korea Republic scenario analysis as a presentation-focused use case
- Tournament-simulation-ready probability tables after validation gates
- Champion probabilities only after verified simulation evidence

The Korea Republic path is preserved as a focused filtered use case and presentation scenario. It is useful for explaining group-stage qualification conditions, but it is not the only modeling scope.

## Current Evidence Status

As of the latest Drive review on 2026-06-16, the project has moved beyond a pure skeleton stage and beyond the earlier baseline-only repository state.

Validated or reviewed evidence currently recorded:

- Raw source validation was previously executed with `data/raw/international_results.csv`.
- Source validation result previously recorded: PASS 6 / FAIL 0.
- Korea MVP processed matches previously recorded: 1,007 rows.
- Global processed matches previously recorded: 49,405 rows.
- Previous preprocessing validation after duplicate-row fix: PASS 30 / FAIL 0.
- The 2026-06-15 team lead preprocessing baseline defines a richer 52-feature model-input contract.
- The 2026-06-16 Drive model report records a model comparison over 41,299 training matches and 4,498 validation matches.
- Generated raw, processed, report, notebook, and model artifacts remain outside version control by default unless the team explicitly decides otherwise.

Reference documents:

- `docs/real_raw_validation_2026-06-12.md`
- `docs/team_lead_preprocessing_alignment_2026-06-15.md`
- `docs/drive_model_results_alignment_2026-06-16.md`
- `docs/model_strategy_2026-06-16.md`

## Current Model Strategy

Current selected story:

```text
Soft Voting = main Win/Draw/Loss probability model candidate
Poisson = expected-scoreline companion model
Korea Republic = focused scenario-analysis use case
```

The current Drive model-comparison report records:

| Model | Accuracy | Macro-F1 | Log Loss | Brier | Current role |
| --- | ---: | ---: | ---: | ---: | --- |
| Soft Voting | 0.6465 | 0.5273 | 0.8000 | 0.4668 | Main model candidate |
| Logistic Full | 0.6450 | 0.5148 | 0.8058 | 0.4683 | Strong interpretable baseline |
| XGBoost | 0.6452 | 0.5286 | 0.8073 | 0.4698 | Core non-linear candidate |
| Stacking | 0.6430 | - | 0.8060 | - | Experimental extension; limited gain so far |
| LightGBM | 0.6392 | 0.5366 | 0.8135 | 0.4720 | Fast gradient-boosting candidate |
| Poisson | 0.6332 | 0.4674 | 0.8161 | 0.4751 | Expected-scoreline companion |
| Logistic Elo-only | 0.6261 | 0.4621 | 0.8290 | 0.4834 | Minimal Elo benchmark |
| Random Forest | 0.6147 | 0.5660 | 0.8415 | 0.4931 | Draw-sensitivity reference |

Interpretation:

- Soft Voting currently has the best Log Loss and Brier Score, so it is the main probability-model candidate.
- Logistic Full and XGBoost are effectively close enough to remain important benchmarks.
- Poisson should remain in the pipeline because expected scoreline is presentation-critical.
- Random Forest has the strongest Macro-F1 but weaker probability quality, so it should be used to discuss draw sensitivity rather than as the main model.
- Stacking is not yet justified as the main model because added complexity has not produced a clear gain over Soft Voting.

## Validation Boundary

The project should not present generated metrics, prediction tables, simulation summaries, or champion probabilities as final claims unless the relevant run evidence is recorded.

Current safe status wording:

> Team 1 has a working model-comparison report over 41,299 training matches and 4,498 validation matches. Among the compared models, Soft Voting currently has the best Log Loss and Brier Score. The recommended presentation direction is Soft Voting for Win/Draw/Loss probabilities plus Poisson for expected scoreline explanation. Korea Republic scenario analysis should be treated as a focused presentation use case, not the only model scope. Final tournament simulation and champion-probability claims still require verified rules implementation and reproducible simulation evidence.

## Remaining Verification Tasks

The following items must remain explicit before final presentation or release:

1. Confirm whether the GitHub code fully reproduces the Drive notebook/model-comparison result.
2. Record reproducible command history, data snapshot, feature schema version, and random seed for the current model-comparison run.
3. Add Soft Voting calibration evidence before using probabilities for simulation-heavy claims.
4. Verify official FIFA competition regulations for group-stage tiebreakers.
5. Verify official FIFA ranking rules for best third-placed teams.
6. Verify official FIFA Round of 32 bracket mapping, including third-place qualifier combinations.
7. Decide whether source manifest candidate rows should remain `pending` or move to `verified`.
8. Define explicit knockout draw-resolution policy for converting W/D/L probabilities into advancement probabilities.

## Data Scope

### Global Primary Path

- Full international match-result dataset where available
- Standardized global processed match table
- Home-team perspective Win / Draw / Loss target labels
- Country/team-name mapping table for canonical names, FIFA codes, and historical aliases
- Team lead 52-feature model-input contract
- Tournament participant, schedule, and bracket interface files

### Korea Scenario Path

- Korea Republic matches and 2026 group-stage scenario filtering
- Korea Republic perspective interpretation when Korea appears as home or away
- Presentation use case for 16강 진출 조건, 승점, 득실, 상대별 확률
- Not the only project scope

## Data Sources

Candidate and current sources:

- International Football Results (`martj42/international_results`) for historical match results
- Elo history from eloratings.net or equivalent documented Elo source
- FIFA ranking or rating sources for team-strength features
- 2026 tournament participants, schedule, and bracket interface files
- Public football APIs only when terms, coverage, and data version are clear

All source rows should keep source URL, owner, license/terms status, download date, expected columns, use case, and verification status in the raw manifest or related source documentation.

## Baseline and Candidate Models

Implemented or reviewed candidate models:

- Logistic Regression, Elo-only
- Logistic Regression, full feature set
- Random Forest
- XGBoost
- LightGBM
- Poisson score model
- Soft Voting ensemble
- Stacking ensemble

Current main candidate:

- Soft Voting

Current companion model:

- Poisson expected-scoreline model

Near-term improvement candidates:

- Weighted Soft Voting only if weights are justified by validation evidence
- Calibration for Soft Voting probabilities
- Draw-recall improvement experiments
- SHAP or permutation importance for presentation interpretation

## Evaluation

Core metrics:

- Accuracy
- Macro F1
- Log Loss
- One-vs-rest multiclass Brier Score
- Calibration curve and calibrated-vs-uncalibrated metric comparison

Required evaluation safeguards:

- Source validation before preprocessing
- Preprocessing validation before modeling
- Leakage checks against final-score columns
- Time-aware split where data allows
- Feature schema versioning
- Reproducible random seed and command history

## Deliverables

Current evidence and interface deliverables:

- `docs/real_raw_validation_2026-06-12.md`
- `docs/team_lead_preprocessing_alignment_2026-06-15.md`
- `docs/drive_model_results_alignment_2026-06-16.md`
- `docs/model_strategy_2026-06-16.md`
- `data/mappings/team_name_mapping.csv`
- `data/tournament/participants.json`
- `data/tournament/schedule.json`
- `data/tournament/bracket.json`
- Source and preprocessing validation scripts
- Korea filtered/scenario path
- Global-first pipeline commands documented in README/runbooks

Generated deliverables, not committed by default:

- Processed match and feature tables
- Baseline model files
- Soft Voting model files
- Poisson scoreline outputs
- Calibration model files
- Metrics reports
- Prediction tables
- Korea scenario tables
- Simulation summaries
- Champion probability outputs

## Implementation Phases

### Phase 1: Evidence-aligned Data Foundation

- Preserve global-first data foundation.
- Preserve Korea scenario path.
- Maintain source validation and preprocessing validation as mandatory gates.
- Keep generated artifacts out of version control unless reviewers explicitly request otherwise.

### Phase 2: Model and Calibration Evidence

- Reproduce the Drive model-comparison run from an agreed validated data snapshot.
- Record Soft Voting, Logistic Full, XGBoost, LightGBM, Random Forest, Poisson, and Stacking metrics.
- Add probability calibration for Soft Voting.
- Record Log Loss and Brier Score before and after calibration.

### Phase 3: Scenario and Simulation Layer

- Generate match-level probability table for 2026 World Cup fixtures.
- Generate Korea Republic group-stage scenario table.
- Verify FIFA group ranking, third-place ranking, and Round of 32 bracket rules.
- Define knockout draw-resolution policy.
- Generate simulation summary and champion probabilities only with fixed random seed and verified rule implementation.
- Decide whether Streamlit, Django API, or both are feasible within the project schedule.

## Instructions For Codex

Always preserve the global-first scope and Korea scenario path unless the team explicitly decides to replace them.

Default priority order:

Source Validation
→ Preprocessing Validation
→ Data Quality Evidence
→ Feature Engineering
→ Model Comparison
→ Evaluation
→ Soft Voting Selection
→ Calibration
→ Poisson Scoreline Companion
→ Match Probability Table
→ Korea Scenario Analysis
→ Simulation
→ Dashboard/API

Do not upgrade `pending` or `web-verified` source statuses to `verified` without an explicit team decision and documented official-source review.

Do not present Drive notebook results as fully reproduced GitHub pipeline evidence until the repository contains the command, data snapshot, feature schema, random seed, and generated report path needed to reproduce them.
