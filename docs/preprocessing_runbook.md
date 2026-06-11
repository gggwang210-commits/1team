# Source and Preprocessing Validation Runbook

## Purpose

This runbook is for the team member who will run source validation and preprocessing validation in a PC, local terminal, or GitHub Codespaces environment.

Source validation must run before preprocessing validation. Preprocessing validation must pass before model training, probability calibration, or tournament simulation.

```text
No source validation PASS, no preprocessing.
No preprocessing PASS, no modeling.
No preprocessing PASS, no calibration.
No preprocessing PASS, no simulation.
```

## Current Mobile Constraint

If you are working from a mobile ChatGPT environment, you may be able to update GitHub files and request code changes, but you usually cannot run the repository's Python commands locally.

In that case, use this document as the execution checklist for the next PC/Codespaces session.

## Pre-run Setup

### 1. Move to the repository root

```bash
cd 1team
```

### 2. Create and activate a Python virtual environment

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Check raw data status

```bash
ls data/raw
```

If `data/raw/` does not contain compatible raw CSV files, `src/data/build_dataset.py` may fall back to the built-in demo dataset. Demo-data validation can confirm that the pipeline runs, but it should not be presented as real-data validation.

## Required PC/Codespaces Execution Order

Run these commands in this order:

```bash
python src/data/validate_sources.py
bash scripts/validate_preprocessing_pipeline.sh
python src/models/train_baseline.py --features-path data/processed/features_global.csv --run-name global_baseline
python src/models/calibrate.py --features-path data/processed/features_global.csv --model-path models/global_baseline_model.pkl --run-name global_baseline
```

Stop immediately if `python src/data/validate_sources.py` fails. Do not run preprocessing until the raw file existence and expected-column checks pass.

## Source Validation Gate

Source validation checks the raw data layer before any preprocessing output is created.

Run:

```bash
python src/data/validate_sources.py
```

Minimum checks:

- `data/raw/source_manifest.csv` exists.
- The manifest has required columns.
- Each `raw_file_name` listed in the manifest exists in `data/raw/`.
- Each raw CSV is readable.
- Each raw CSV has at least one row.
- Each raw CSV contains its declared `expected_columns`.

If this command fails, fix the raw files or `source_manifest.csv` first.

```text
No source validation PASS, no preprocessing.
```

## Full Preprocessing Validation Command Sequence

Run the full preprocessing sequence before model training, calibration, or simulation:

```bash
python src/data/validate_sources.py
bash scripts/validate_preprocessing_pipeline.sh
```

The pipeline script expands to:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea

python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home

python src/data/validate_team_mapping.py
python src/data/validate_preprocessing.py --scope both
```

## Korea-only Quick Validation

Use this when you only need to check the Korea filtered path after source validation passes:

```bash
python src/data/validate_sources.py
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/data/validate_preprocessing.py --scope korea
```

## Global-only Quick Validation

Use this when you only need to check the global-first path after source validation passes:

```bash
python src/data/validate_sources.py
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/data/validate_preprocessing.py --scope global
```

## Expected Source Validation Success Output

The source validation command should print:

```text
Source validation passed.
```

## Expected Preprocessing Success Output

The final preprocessing validation command should print:

```text
Preprocessing validation passed.
```

The following local generated reports should also exist:

```text
reports/preprocessing_validation.csv
reports/preprocessing_validation.md
```

All rows in `reports/preprocessing_validation.csv` should have:

```text
status = PASS
```

## Failure Output

If source validation fails, it exits with code `1`. Fix source files or `source_manifest.csv` before preprocessing.

If preprocessing validation fails, the command exits with code `1` and prints a failure message such as:

```text
Preprocessing validation failed with N failed check(s).
```

Open these files first:

```text
reports/preprocessing_validation.md
reports/preprocessing_validation.csv
```

Do not continue to model training, calibration, or simulation until the failed checks are fixed.

## Failure Types and How to Respond

### 1. Source validation failure

Likely cause:

- `data/raw/source_manifest.csv` is missing.
- Manifest required columns are missing.
- A raw file listed in the manifest does not exist.
- A raw CSV is empty.
- A raw CSV does not contain the declared `expected_columns`.

Fix direction:

- Add the missing raw CSV to `data/raw/`.
- Update `raw_file_name` in `data/raw/source_manifest.csv`.
- Update `expected_columns` to match the actual raw CSV headers.
- Do not proceed to preprocessing while source validation fails.

### 2. Required preprocessing file not found

Likely cause:

- `build_dataset.py` or `make_features.py` was not run.
- The command was run from the wrong directory.

Fix:

```bash
python src/data/validate_sources.py
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
```

Then rerun:

```bash
python src/data/validate_preprocessing.py --scope both
```

### 3. Required columns are missing

Likely cause:

- Raw CSV column names do not match expected football dataset columns.
- Column alias logic in `build_dataset.py` does not yet cover the raw data format.

Fix direction:

- Inspect raw CSV headers.
- Update `data/raw/source_manifest.csv` if the manifest is wrong.
- Add safe aliases in `src/data/build_dataset.py` or `src/data/validate_team_mapping.py` if the raw data uses a common alternative schema.
- Do not manually patch generated processed CSV files as the main solution.

### 4. Missing values in required columns

Likely cause:

- Raw rows contain missing dates, team names, scores, or target labels.
- Global/Korea filtering produced incomplete target rows.

Fix direction:

- Decide whether rows should be dropped or imputed.
- For match results and targets, dropping incomplete rows is usually safer than imputing outcomes.
- Rebuild processed files after changing code or raw data.

### 5. Duplicate rows

Likely cause:

- Raw CSV contains duplicate match records.
- Multiple raw sources overlap.

Fix direction:

- Confirm duplicate definition.
- Prefer deterministic duplicate removal in preprocessing code.
- Rebuild processed outputs and rerun validation.

### 6. Invalid target values

Expected values:

```text
Win
Draw
Loss
```

Likely cause:

- Target labels were not generated through the standard score-comparison logic.
- Existing raw labels use different values.

Fix direction:

- Check `_add_home_perspective_target()` and `_add_korea_perspective_target()` in `src/data/build_dataset.py`.
- Do not proceed if target labels include unexpected classes.

### 7. Korea filtered scope failure

Korea filtered rule:

- Every Korea filtered row must include `Korea Republic` as either `home_team` or `away_team`.

Likely cause:

- `matches.csv` was generated from global data without Korea filtering.
- Team naming differs from `Korea Republic`.

Fix direction:

- Verify `KOREA_TEAM_NAME` in `build_dataset.py`.
- Confirm raw data uses a supported alias or canonical team name.
- If needed, update team mapping/normalization logic before rebuilding.

### 8. Score leakage failure

Rule:

- `features.csv` and `features_global.csv` must not contain final-score columns such as `home_score` or `away_score`.

Reason:

- Scores are only allowed to create labels.
- Scores must not become model input features.

Fix direction:

- Check `src/features/make_features.py` and ensure score columns are dropped from the feature table.

### 9. source_target_scope mismatch

Expected values:

- Korea filtered path: `source_target_scope = korea`
- Global-first path: `source_target_scope = home`

Likely cause:

- `make_features.py` was run with the wrong `--target-scope`.

Fix:

```bash
python src/features/make_features.py --target-scope korea
python src/features/make_features.py --target-scope home
python src/data/validate_preprocessing.py --scope both
```

## After PASS

Only after source validation and preprocessing validation pass should you continue.

Global-first model path:

```bash
python src/models/train_baseline.py \
  --features-path data/processed/features_global.csv \
  --run-name global_baseline

python src/models/calibrate.py \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_model.pkl \
  --run-name global_baseline
```

Korea filtered path:

```bash
python src/models/train_baseline.py
python src/models/calibrate.py
python src/models/predict.py
python src/models/evaluate.py
```

Simulation scaffold:

```bash
python src/simulation/run_tournament.py
```

## Generated Artifact Policy

The following files are generated validation artifacts and should not be committed by default:

```text
reports/source_validation.csv
reports/source_validation.md
reports/preprocessing_validation.csv
reports/preprocessing_validation.md
reports/unmapped_teams.csv
reports/team_mapping_validation.md
reports/data_quality_summary.md
```

Commit them only if a reviewer explicitly asks for a specific evidence snapshot.

## Reporting Language for Team Presentation

Use clear wording when reporting validation status:

```text
The project now separates source validation and preprocessing validation.
Source validation checks raw file existence and expected columns before preprocessing.
Preprocessing validation checks processed matches/features before modeling.
```

If source validation fails, say:

```text
Source validation failed, so preprocessing and modeling were not run. The raw data source or expected column contract must be fixed first.
```

If validation was run only with the built-in demo dataset, say:

```text
The pipeline was validated on the built-in demo dataset. Real-data validation is still required after adding confirmed raw match CSV files.
```

If validation passes on real raw data, say:

```text
The source and preprocessing gates passed on the current raw dataset, including checks for raw file existence, expected columns, required columns, missing values, duplicate rows, target labels, scope, and final-score leakage.
```
