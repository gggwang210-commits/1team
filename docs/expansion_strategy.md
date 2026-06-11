# 1TEAM Expansion Strategy

## Executive Summary

This document records the first expansion direction for the 2026 FIFA World Cup Prediction Project.

The project is moving from a Korea Republic MVP toward a global prediction system:

- AS-IS: Korea Republic match-level Win/Draw/Loss prediction
- TO-BE: All-participant match prediction, calibrated probabilities, tournament simulation, and champion probabilities
- Korea Republic position: application case filtered from the global model

The immediate goal is not to replace the working MVP. The goal is to preserve the MVP path while adding a safe expansion path.

## Scope Change

| Item | AS-IS | TO-BE |
| --- | --- | --- |
| Prediction target | Korea Republic matches | Global international matches and 2026 target fixtures |
| Output | Match-level W/D/L probabilities | Match probabilities + tournament simulation + champion probabilities |
| Korea role | Main project target | Filtered dashboard/application case |
| Model path | LR/RF baseline | LR/RF + calibrated model |
| Service path | Streamlit demo | Streamlit MVP, optional Django dashboard/API |
| Data pipeline | Korea filtering | Global standardization + team-name mapping |

## Phase 1: Data Expansion

Priority tasks:

1. Preserve the existing Korea MVP smoke-test path.
2. Add optional global dataset mode using `filter_korea=False`.
3. Prepare `data/mappings/` for `team_name_mapping.csv`.
4. Prepare `data/tournament/` for 2026 participants, schedule, and bracket data.
5. Document data-quality assumptions and data version information.

Expected outputs:

- `data/processed/matches.csv`
- `data/mappings/team_name_mapping.csv`
- `data/tournament/participants.json`
- `data/tournament/schedule.json`
- `data/tournament/bracket.json`
- `reports/data_quality_summary.md`

## Phase 2: Model Expansion

Priority tasks:

1. Train global baseline models.
2. Compare `ranking_context_only` against `with_team_identifiers`.
3. Document team-name memorization risk.
4. Add probability calibration using Platt Scaling or Isotonic Regression.
5. Compare calibrated and uncalibrated Log Loss and Brier Score.

Expected outputs:

- `reports/baseline_metrics.csv`
- `reports/calibration_report/`
- `reports/prediction_table.csv`

## Phase 3: Simulation and Service

Priority tasks:

1. Implement group-stage simulation.
2. Implement knockout simulation.
3. Fix random seed for reproducibility.
4. Generate round advancement and champion probability outputs.
5. Decide whether Django can be completed within the remaining schedule.

Expected outputs:

- `reports/simulation_summary.csv`
- `reports/champion_probabilities.csv`
- Global dashboard
- Korea Republic filtered dashboard tab

## Proposed Project Structure

```text
1team-worldcup-prediction/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── mappings/
│   │   └── team_name_mapping.csv
│   └── tournament/
│       ├── participants.json
│       ├── schedule.json
│       └── bracket.json
├── src/
│   ├── data/
│   │   ├── build_dataset.py
│   │   └── merge_rankings.py
│   ├── features/
│   │   └── make_features.py
│   ├── models/
│   │   ├── train_baseline.py
│   │   ├── calibrate.py
│   │   └── predict.py
│   └── simulation/
│       └── run_tournament.py
├── app/
│   └── streamlit_app.py
├── docs/
│   └── expansion_strategy.md
└── reports/
    ├── baseline_metrics.csv
    ├── calibration_report/
    ├── prediction_table.csv
    ├── simulation_summary.csv
    └── champion_probabilities.csv
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Team-name inconsistency | High | Create `team_name_mapping.csv` and validate early |
| Probability calibration quality | High | Use calibration curves and Brier Score comparison |
| Knockout draw handling | Medium | Make draw-to-winner assumption explicit |
| Tournament schedule changes | Medium | Record data version and reference date |
| Django schedule pressure | Medium | Keep Streamlit MVP stable and treat Django as Go/No-Go |
| Historical data bias | Medium | Consider time-aware splits and recent-match weighting |

## Meeting Decisions Needed

1. Confirm project naming: global prediction or Korea MVP with expansion.
2. Confirm whether champion probability is in the final presentation scope.
3. Assign owners for Phase 1, Phase 2, and Phase 3 tasks.
4. Decide whether team identifiers can be used in the final model.
5. Decide tournament draw handling assumption.
6. Decide Django Go/No-Go after MVP stability check.

## Next Actions

1. Share this strategy with the team.
2. Create the first draft of `team_name_mapping.csv`.
3. Add 2026 tournament input skeleton files.
4. Run MVP smoke test to confirm the default Korea path still works.
5. Start global dataset validation with `python src/data/build_dataset.py --global-scope`.
