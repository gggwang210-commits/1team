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

## Target Scope, File, and Artifact Strategy

The project separates dataset scope, target scope, generated processed files, and model artifacts so MVP and global expansion runs do not overwrite each other by default.

| Step | MVP mode | Global baseline mode |
| --- | --- | --- |
| Dataset build command | `python src/data/build_dataset.py` | `python src/data/build_dataset.py --global-scope` |
| Match output | `data/processed/matches.csv` | `data/processed/matches_global.csv` |
| Feature build command | `python src/features/make_features.py --target-scope korea` | `python src/features/make_features.py --target-scope home` |
| Feature input | `data/processed/matches.csv` | `data/processed/matches_global.csv` |
| Feature output | `data/processed/features.csv` | `data/processed/features_global.csv` |
| Source target | `target_result_korea_perspective` | `target_result` |
| Meaning of output `target_result` | Korea Republic perspective | Home-team perspective |
| Baseline training command | `python src/models/train_baseline.py` | `python src/models/train_baseline.py --features-path data/processed/features_global.csv --run-name global_baseline` |
| Model artifact | `models/baseline_model.pkl` | `models/global_baseline_model.pkl` |
| Metrics artifact | `reports/baseline_metrics.csv` | `reports/global_baseline_metrics.csv` |

This separation prevents the global dataset from depending on Korea-only labels. In global mode, `target_result_korea_perspective` may be missing for non-Korea matches; that is expected and allowed. The global feature path uses the home-team perspective target instead.

## Phase 1 Data Skeleton Files

The Phase 1 data expansion files are interface-design inputs, not official tournament data and not generated reports.

| File | Purpose | Status |
| --- | --- | --- |
| `data/mappings/team_name_mapping.csv` | Maps country aliases to canonical team names and FIFA codes | Initial draft; must be validated against raw data |
| `data/tournament/participants.json` | Defines the expected participant input schema for simulation | Skeleton only; not an official participant list |
| `data/tournament/schedule.json` | Defines the expected match schedule schema for prediction/simulation | Skeleton only; not an official schedule |
| `data/tournament/bracket.json` | Defines group ranking and knockout bracket schema | Skeleton only; official rules must be verified |

All tournament JSON skeleton files include `data_status`, `source_note`, and `last_updated`. Values marked `TBD` must be replaced only after official source verification.

## Team Mapping Validation

`src/data/validate_team_mapping.py` validates whether raw match team names are covered by `data/mappings/team_name_mapping.csv`.

Validation flow:

1. Scan `data/raw/*.csv`.
2. Standardize column names and find files with `home_team` and `away_team` columns.
3. Extract unique raw team names.
4. Build a lookup from `canonical_name` and semicolon-separated `aliases`.
5. Report unmapped names to `reports/unmapped_teams.csv`.
6. Report summary and duplicate aliases to `reports/team_mapping_validation.md`.

This is a data-quality workflow, not a model-training workflow. The generated report files should not be committed by default.

## Phase 1: Data Expansion

Priority tasks:

1. Preserve the existing Korea MVP smoke-test path.
2. Add optional global dataset mode using `filter_korea=False`.
3. Add target scope support in feature engineering.
4. Separate MVP and global generated processed outputs.
5. Prepare and validate `data/mappings/team_name_mapping.csv` against raw data.
6. Prepare `data/tournament/` for 2026 participants, schedule, and bracket data.
7. Document data-quality assumptions and data version information.

Expected outputs:

- `data/processed/matches.csv`
- `data/processed/features.csv`
- `data/processed/matches_global.csv`
- `data/processed/features_global.csv`
- `data/mappings/team_name_mapping.csv`
- `reports/unmapped_teams.csv`
- `reports/team_mapping_validation.md`
- `data/tournament/participants.json`
- `data/tournament/schedule.json`
- `data/tournament/bracket.json`
- `reports/data_quality_summary.md`

## Phase 2: Model Expansion

Priority tasks:

1. Train MVP baseline and global baseline without overwriting each other.
2. Use `train_baseline.py --features-path` and `--run-name` for global baseline runs.
3. Compare MVP metrics and global metrics at a high level, while remembering they are trained on different scopes.
4. Compare `ranking_context_only` against `with_team_identifiers`.
5. Document team-name memorization risk.
6. Add probability calibration using Platt Scaling or Isotonic Regression.
7. Compare calibrated and uncalibrated Log Loss and Brier Score.

Expected outputs:

- `models/baseline_model.pkl`
- `models/global_baseline_model.pkl`
- `reports/baseline_metrics.csv`
- `reports/global_baseline_metrics.csv`
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
│   │   ├── matches.csv
│   │   ├── features.csv
│   │   ├── matches_global.csv
│   │   └── features_global.csv
│   ├── mappings/
│   │   └── team_name_mapping.csv
│   └── tournament/
│       ├── participants.json
│       ├── schedule.json
│       └── bracket.json
├── src/
│   ├── data/
│   │   ├── build_dataset.py
│   │   ├── merge_rankings.py
│   │   └── validate_team_mapping.py
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
    ├── global_baseline_metrics.csv
    ├── calibration_report/
    ├── prediction_table.csv
    ├── unmapped_teams.csv
    ├── team_mapping_validation.md
    ├── simulation_summary.csv
    └── champion_probabilities.csv
```

## Verification Commands

Korea MVP check:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/models/train_baseline.py
python src/models/predict.py
python src/models/evaluate.py
```

Global baseline check:

```bash
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/models/train_baseline.py --features-path data/processed/features_global.csv --run-name global_baseline
```

Model artifact existence check:

```bash
python - <<'PY'
from pathlib import Path

paths = [
    "models/baseline_model.pkl",
    "reports/baseline_metrics.csv",
    "models/global_baseline_model.pkl",
    "reports/global_baseline_metrics.csv",
]

for path in paths:
    p = Path(path)
    print(path, "OK" if p.exists() else "MISSING")
PY
```

Custom baseline output example:

```bash
python src/models/train_baseline.py \
  --features-path data/processed/features_global.csv \
  --model-path models/custom_global_model.pkl \
  --metrics-path reports/custom_global_metrics.csv
```

Data skeleton syntax check:

```bash
python -m json.tool data/tournament/participants.json
python -m json.tool data/tournament/schedule.json
python -m json.tool data/tournament/bracket.json
python - <<'PY'
import pandas as pd
pd.read_csv('data/mappings/team_name_mapping.csv')
print('team_name_mapping.csv is readable')
PY
```

Team mapping validation:

```bash
python src/data/validate_team_mapping.py
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Team-name inconsistency | High | Create `team_name_mapping.csv` and validate early |
| Target meaning confusion | High | Use explicit `--target-scope korea/home` and audit columns |
| Official vs skeleton data confusion | High | Keep `SKELETON_NOT_OFFICIAL`, `source_note`, and `TBD` values until verified |
| Generated file overwrite between MVP/global modes | Lower after Phase 1-5 | MVP and global processed outputs use separate default paths |
| Global model artifact overwrite | Lower after Phase 2-1 | `--features-path`, `--run-name`, `--model-path`, and `--metrics-path` separate artifacts |
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

1. Run MVP baseline verification.
2. Run global baseline verification.
3. Compare `reports/baseline_metrics.csv` and `reports/global_baseline_metrics.csv` carefully, noting that dataset scopes differ.
4. Design probability calibration workflow.
5. Add `src/models/calibrate.py` in the next phase.
