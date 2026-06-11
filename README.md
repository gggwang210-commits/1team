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
- `data/mappings/team_name_mapping.csv` provides an initial country alias mapping draft.
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

## Stack

- Python
- Pandas
- Scikit-learn
- Streamlit
- Django, optional expansion phase

## Status

Research & MVP Phase with documented expansion path.

## MVP Data Flow

Generated report files are intentionally not committed. Running the pipeline recreates `reports/data_quality_summary.md`, `reports/baseline_metrics.csv`, `reports/prediction_table.csv`, `reports/model_evaluation.md`, and `reports/smoke_test_report.md` from the current code, data, and model artifacts. Treat those files as local evidence for the current run rather than authoritative checked-in model results.

The implemented MVP pipeline has five explicit stages:

1. `src/data/build_dataset.py` standardizes international match-result data and writes `data/processed/matches.csv`.
   - If no compatible raw CSV exists in `data/raw/`, it creates a built-in demo dataset.
   - The demo dataset has 15 labeled rows and three target classes so baseline training can run locally.
   - By default, full international raw datasets are filtered to rows where Korea Republic is either `home_team` or `away_team`.
   - For expansion, run with `--global-scope` or call `build_dataset(filter_korea=False)` to keep all compatible international rows.
   - `target_result` is the score-derived home-team perspective label.
   - `target_result_korea_perspective` is the MVP label for Korea Republic matches. It matches `target_result` when Korea Republic is the home team, reverses home `Win`/`Loss` when Korea Republic is the away team, and keeps `Draw` unchanged.
   - `reports/data_quality_summary.md` is generated with row count, missing counts, and target distribution for a quick sanity check.
2. `src/features/make_features.py` converts processed match rows into model-ready pre-match features and writes `data/processed/features.csv`.
   - Default execution uses `--target-scope korea`, which preserves the Korea MVP target behavior.
   - Global expansion feature generation uses `--target-scope home`, which copies the home-team perspective `matches.csv.target_result` into `features.csv.target_result`.
   - Final scores are used only to create result labels.
   - Score/result leakage columns are not included as model features.
3. `src/models/train_baseline.py` validates the feature table before model fitting.
   - Supported target column: `target_result`.
   - Minimum requirements: at least two target classes, at least one non-empty usable feature column, at least two rows per class, and enough rows for the configured train/test split.
   - Baseline metrics are recorded for two explicit feature sets: `ranking_context_only` excludes `home_team` and `away_team`, while `with_team_identifiers` keeps those team-name identifiers for comparison.
   - Implemented metrics include Accuracy, Macro F1, Log Loss, and one-vs-rest multiclass Brier Score.

## Project Structure

```text
.
├── app/
│   └── streamlit_app.py              # Streamlit MVP application entry point
├── data/
│   ├── interim/                      # Intermediate cleaned data files
│   │   └── .gitkeep
│   ├── mappings/                     # Team name / FIFA code mapping files
│   │   ├── .gitkeep
│   │   └── team_name_mapping.csv
│   ├── processed/                    # Model-ready datasets
│   │   └── .gitkeep
│   ├── raw/                          # Original downloaded datasets
│   │   └── .gitkeep
│   └── tournament/                   # Participants, schedule, and bracket inputs
│       ├── .gitkeep
│       ├── bracket.json
│       ├── participants.json
│       └── schedule.json
├── docs/
│   └── expansion_strategy.md         # Global expansion roadmap
├── models/                           # Saved baseline model artifacts
│   └── .gitkeep
├── notebooks/
│   ├── 01_data_quality_check.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_baseline_modeling.ipynb
├── reports/                          # Runtime-generated reports; only .gitkeep is tracked
│   └── .gitkeep
├── scripts/
│   └── smoke_test.sh                 # Main-branch smoke test wrapper
├── src/
│   ├── data/
│   │   ├── build_dataset.py          # Dataset assembly and scope filtering
│   │   ├── clean_data.py
│   │   └── load_data.py
│   ├── features/
│   │   └── make_features.py          # Feature engineering with target scope support
│   ├── models/
│   │   ├── evaluate.py
│   │   ├── predict.py
│   │   └── train_baseline.py
│   ├── simulation/                   # Tournament simulation expansion code
│   │   └── .gitkeep
│   └── utils/
│       └── config.py
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

   Expected MVP data sources:

   - International Football Results
   - FIFA Rankings
   - FIFA World Cup Data

   If no compatible raw CSV is present, the MVP uses a small built-in demo dataset for local pipeline testing.

4. Build the processed match dataset.

   ```bash
   python src/data/build_dataset.py
   ```

   Expansion-only global dataset mode:

   ```bash
   python src/data/build_dataset.py --global-scope
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

6. Train baseline models.

   ```bash
   python src/models/train_baseline.py
   ```

7. Generate the required prediction table.

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

## Expansion Feature Check

The first global expansion check stops at feature generation. It confirms that the global data path can create `matches.csv` and that the home-team target can be copied safely into `features.csv.target_result`.

```bash
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
```

Before running the MVP smoke test again, rebuild the default Korea MVP dataset and features:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
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

## CI and Local Smoke Test

### Generated artifact policy

Running `verify_mvp_pipeline.sh`, `./scripts/smoke_test.sh`, or the manual MVP pipeline commands can refresh local generated artifacts. These files are reproducible outputs from the current code, data, and model run, so they are generally not committed:

- `data/processed/matches.csv`
- `data/processed/features.csv`
- `models/baseline_model.pkl`
- `reports/baseline_metrics.csv`
- `reports/prediction_table.csv`
- `reports/model_evaluation.md`
- `reports/smoke_test_report.md`

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
