# 2026 FIFA World Cup Prediction Model

## Team Project

Machine learning based prediction system for 2026 FIFA World Cup match outcomes.

The repository keeps the current Korea Republic MVP reproducible while preparing a first expansion path toward all-participant match prediction, calibrated probabilities, tournament simulation, and champion probabilities.

## Scope Summary

Current MVP:

- Korea Republic match-level Win/Draw/Loss probabilities
- Korea Republic perspective labels
- Streamlit MVP demo

Expansion direction:

- Global match-level Win/Draw/Loss probabilities
- Korea Republic as a filtered application case from the global model
- Probability calibration for simulation input
- Group-stage and knockout simulation
- Champion probabilities
- Optional Django dashboard/API depending on schedule feasibility

This repository still prioritizes a working match-level outcome pipeline first. Tournament simulation and champion probabilities are expansion deliverables, not replacements for the reproducible MVP path.

## MVP Scope

The current MVP focuses on predicting Korea Republic group-stage match outcome probabilities:

- Korea Republic Win Probability
- Korea Republic Draw Probability
- Korea Republic Loss Probability

All MVP labels and predictions use **Korea Republic's perspective**. For example, `Win` means Korea Republic wins the match, regardless of whether Korea Republic is listed as the home or away team.

MVP does not directly classify champion teams or run a tournament simulator. Later phases expand in this order:

match probabilities → probability calibration → group simulation → knockout simulation → champion probability.

### Target column contract

The project intentionally uses result labels from different perspectives at different pipeline stages. Keep this contract explicit to avoid target leakage or accidentally training on the wrong label:

- `matches.csv.target_result` = home-team perspective result label.
- `matches.csv.target_result_korea_perspective` = Korea Republic perspective result label when the match includes Korea Republic.
- `features.csv.target_result` = model target for the active pipeline scope.
- `features.csv.target_result_korea_perspective` = retained audit copy for Korea Republic perspective when available, excluded from every model input feature set.
- `features.csv.source_target_column` and `features.csv.source_target_scope` = audit metadata showing which target definition was copied into `features.csv.target_result`.

`src/models/train_baseline.py` treats `features.csv.target_result` as the only modeling target and excludes every target/result/score-like column from the feature matrix before preprocessing and training.

## Expansion Strategy

The first expansion converts the Korea-only pipeline into a global pipeline without breaking the MVP smoke-test path.

Key changes:

- `src/data/build_dataset.py` supports `filter_korea=True` by default for the MVP and `filter_korea=False` for global data expansion.
- `src/features/make_features.py` supports `--target-scope korea` for the MVP and `--target-scope home` for global expansion feature generation.
- MVP and global processed outputs are separated by default to reduce accidental overwrites.
- `src/models/train_baseline.py` supports `--features-path`, `--run-name`, `--model-path`, and `--metrics-path` so MVP and global baseline artifacts can be separated.
- `data/mappings/team_name_mapping.csv` provides an initial country alias mapping draft.
- `src/data/validate_team_mapping.py` validates raw team names against the mapping table.
- `data/tournament/participants.json`, `schedule.json`, and `bracket.json` provide skeleton interfaces for future simulation work.
- `src/simulation/` is reserved for tournament simulation code.
- `docs/expansion_strategy.md` records the expansion roadmap and team decision points.

## Phase 1 Data Files

These files are committed because they are source data skeletons and interface definitions, not generated reports.

| File | Purpose | Status |
| --- | --- | --- |
| `data/mappings/team_name_mapping.csv` | Country canonical-name, FIFA code, and alias mapping | Initial draft; validate against raw data |
| `data/tournament/participants.json` | Participant input schema for simulation | `SKELETON_NOT_OFFICIAL` |
| `data/tournament/schedule.json` | Match schedule input schema | `SKELETON_NOT_OFFICIAL` |
| `data/tournament/bracket.json` | Group and knockout bracket schema | `SKELETON_NOT_OFFICIAL` |

The tournament JSON files are not official FIFA data. Values marked `TBD` must be replaced only after official source verification.

## Generated File Paths

| Scope | Match file | Feature file | Model file | Metrics file |
| --- | --- | --- | --- | --- |
| Korea MVP | `data/processed/matches.csv` | `data/processed/features.csv` | `models/baseline_model.pkl` | `reports/baseline_metrics.csv` |
| Global baseline | `data/processed/matches_global.csv` | `data/processed/features_global.csv` | `models/global_baseline_model.pkl` | `reports/global_baseline_metrics.csv` |

Global baseline training is not calibration or simulation yet. It only confirms that `features_global.csv` can be trained with the same baseline modeling workflow without overwriting MVP artifacts.

## Stack

- Python
- Pandas
- Scikit-learn
- Streamlit
- Django, optional expansion phase

## Status

Research & MVP Phase with documented expansion path.

## MVP Data Flow

Generated report files are intentionally not committed. Running the pipeline recreates reports and model artifacts from the current code, data, and model run. Treat those files as local evidence for the current run rather than authoritative checked-in model results.

The implemented MVP pipeline has five explicit stages:

1. `src/data/build_dataset.py` standardizes international match-result data and writes `data/processed/matches.csv`.
   - For expansion, run with `--global-scope` to write `data/processed/matches_global.csv` by default.
   - Custom output is available with `--output-path`.
2. `src/features/make_features.py` converts processed match rows into model-ready pre-match features.
   - MVP output: `data/processed/features.csv`.
   - Global output: `data/processed/features_global.csv`.
   - Custom input and output paths are available with `--input-path` and `--output-path`.
3. `src/models/train_baseline.py` validates the feature table before model fitting.
   - MVP default input: `data/processed/features.csv`.
   - Global input can be selected with `--features-path data/processed/features_global.csv`.
   - `--run-name global_baseline` writes `models/global_baseline_model.pkl` and `reports/global_baseline_metrics.csv`.
   - Implemented metrics include Accuracy, Macro F1, Log Loss, and one-vs-rest multiclass Brier Score.
4. `src/models/predict.py` generates the required MVP prediction table.
5. `src/models/evaluate.py` evaluates the MVP baseline outputs.

## Project Structure

```text
.
├── app/
│   └── streamlit_app.py
├── data/
│   ├── mappings/
│   │   └── team_name_mapping.csv
│   ├── processed/
│   │   └── .gitkeep
│   ├── raw/
│   │   └── .gitkeep
│   └── tournament/
│       ├── bracket.json
│       ├── participants.json
│       └── schedule.json
├── docs/
│   └── expansion_strategy.md
├── models/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── scripts/
│   └── smoke_test.sh
├── src/
│   ├── data/
│   │   ├── build_dataset.py
│   │   ├── clean_data.py
│   │   ├── load_data.py
│   │   └── validate_team_mapping.py
│   ├── features/
│   │   └── make_features.py
│   ├── models/
│   │   ├── evaluate.py
│   │   ├── predict.py
│   │   └── train_baseline.py
│   └── simulation/
│       └── .gitkeep
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

4. Build the processed match dataset.

   MVP dataset:

   ```bash
   python src/data/build_dataset.py
   ```

   Global expansion dataset:

   ```bash
   python src/data/build_dataset.py --global-scope
   ```

   Custom output path:

   ```bash
   python src/data/build_dataset.py --global-scope --output-path data/processed/custom_matches.csv
   ```

5. Create model-ready features.

   MVP default, Korea Republic perspective:

   ```bash
   python src/features/make_features.py
   ```

   Explicit MVP command:

   ```bash
   python src/features/make_features.py --target-scope korea
   ```

   Global expansion feature mode, home-team perspective:

   ```bash
   python src/features/make_features.py --target-scope home
   ```

   Custom input/output paths:

   ```bash
   python src/features/make_features.py --target-scope home --input-path data/processed/custom_matches.csv --output-path data/processed/custom_features.csv
   ```

6. Train baseline models.

   MVP baseline:

   ```bash
   python src/models/train_baseline.py
   ```

   Global baseline:

   ```bash
   python src/models/train_baseline.py \
     --features-path data/processed/features_global.csv \
     --run-name global_baseline
   ```

   Custom model and metrics paths:

   ```bash
   python src/models/train_baseline.py \
     --features-path data/processed/features_global.csv \
     --model-path models/custom_global_model.pkl \
     --metrics-path reports/custom_global_metrics.csv
   ```

7. Generate the required MVP prediction table.

   ```bash
   python src/models/predict.py
   ```

8. Evaluate baseline models.

   ```bash
   python src/models/evaluate.py
   ```

9. Launch the Streamlit demo.

   ```bash
   streamlit run app/streamlit_app.py
   ```

## Expansion Baseline Check

```bash
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/models/train_baseline.py \
  --features-path data/processed/features_global.csv \
  --run-name global_baseline
```

File existence check:

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

## Data Skeleton Syntax Check

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

## Team Mapping Validation

Run this after adding real raw match CSV files to `data/raw/`:

```bash
python src/data/validate_team_mapping.py
```

This creates generated data-quality reports:

- `reports/unmapped_teams.csv`
- `reports/team_mapping_validation.md`

These reports are local validation outputs and are not committed by default.

## CI and Local Smoke Test

### Generated artifact policy

Running `verify_mvp_pipeline.sh`, `./scripts/smoke_test.sh`, the manual MVP pipeline commands, global baseline commands, or `src/data/validate_team_mapping.py` can refresh local generated artifacts. These files are reproducible outputs from the current code, data, and model run, so they are generally not committed:

- `data/processed/matches.csv`
- `data/processed/features.csv`
- `data/processed/matches_global.csv`
- `data/processed/features_global.csv`
- `models/baseline_model.pkl`
- `models/global_baseline_model.pkl`
- `reports/baseline_metrics.csv`
- `reports/global_baseline_metrics.csv`
- `reports/prediction_table.csv`
- `reports/model_evaluation.md`
- `reports/smoke_test_report.md`
- `reports/unmapped_teams.csv`
- `reports/team_mapping_validation.md`

The `.gitkeep` files are placeholders that keep otherwise-empty directories in Git. By default, pull requests should include only source code, scripts, and README/documentation changes unless a reviewer explicitly asks for generated artifacts.

### Official smoke test

Run the official smoke test from the `main` branch so CI and local baseline results are reproducible:

```bash
git fetch origin main && git checkout main
./scripts/smoke_test.sh
```

The smoke test gate is intentionally limited to the reproducible MVP pipeline commands. Post-MVP features such as calibration, simulation, and Django must not be added as mandatory smoke test requirements until the team explicitly changes the acceptance criteria.

### Development quick check

Run the MVP pipeline in order:

1. `python src/data/build_dataset.py`
2. `python src/features/make_features.py`
3. `python src/models/train_baseline.py`
4. `python src/models/predict.py`
5. `python src/models/evaluate.py`

## MVP Deliverables

- Data Quality Report
- Baseline Model
- Prediction Table
- Streamlit Demo

## Expansion Deliverables

- Team name mapping table
- 2026 tournament input tables
- Team mapping validation report
- Global baseline metrics
- Calibrated prediction table
- Simulation summary
- Champion probabilities
- Global dashboard / Django API if schedule allows

## MVP Limitations

- The built-in demo dataset is intentionally small and is only meant to prove that the local pipeline runs end to end.
- Team-name identifiers such as `home_team` and `away_team` can make demo metrics look better than they really are because a model may memorize team-specific outcomes instead of learning generalizable ranking or match-context signals.
- MVP metrics should not be treated as production-ready claims until they are validated on larger historical datasets with time-aware splits and stronger leakage checks.

## Post-MVP Improvements

- Replace the demo dataset with real historical international match results and FIFA rankings.
- Add rolling recent-form features, rest-days features, and tournament-context features.
- Add probability calibration and compare calibrated vs. uncalibrated Log Loss/Brier Score alongside Accuracy and Macro F1.
- Add tournament simulation with fixed seed reproducibility.
- Add data governance checks before using sensitive, licensed, or API-based datasets.
