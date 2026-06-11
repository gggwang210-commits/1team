# Preprocessing Validation Runbook

## Purpose

This runbook is for the team member who will run preprocessing validation in a PC, local terminal, or GitHub Codespaces environment.

Do not proceed to model training, probability calibration, or tournament simulation until preprocessing validation passes.

```text
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

## Full Preprocessing Validation Command Sequence

Run the full preprocessing sequence before model training, calibration, or simulation:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea

python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home

python src/data/validate_team_mapping.py
python src/data/validate_preprocessing.py --scope both
```

## MVP-only Quick Validation

Use this when you only need to check the Korea MVP path:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/data/validate_preprocessing.py --scope korea
```

## Global-only Quick Validation

Use this when you only need to check the global expansion path:

```bash
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/data/validate_preprocessing.py --scope global
```

## Expected Success Output

The final command should print:

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

### 1. Required file not found

Likely cause:

- `build_dataset.py` or `make_features.py` was not run.
- The command was run from the wrong directory.

Fix:

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
```

Then rerun:

```bash
python src/data/validate_preprocessing.py --scope both
```

### 2. Required columns are missing

Likely cause:

- Raw CSV column names do not match expected football dataset columns.
- Column alias logic in `build_dataset.py` does not yet cover the raw data format.

Fix direction:

- Inspect raw CSV headers.
- Add safe aliases in `src/data/build_dataset.py` or `src/data/validate_team_mapping.py`.
- Do not manually patch generated processed CSV files as the main solution.

### 3. Missing values in required columns

Likely cause:

- Raw rows contain missing dates, team names, scores, or target labels.
- Global/Korea filtering produced incomplete target rows.

Fix direction:

- Decide whether rows should be dropped or imputed.
- For match results and targets, dropping incomplete rows is usually safer than imputing outcomes.
- Rebuild processed files after changing code or raw data.

### 4. Duplicate rows

Likely cause:

- Raw CSV contains duplicate match records.
- Multiple raw sources overlap.

Fix direction:

- Confirm duplicate definition.
- Prefer deterministic duplicate removal in preprocessing code.
- Rebuild processed outputs and rerun validation.

### 5. Invalid target values

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

### 6. Korea MVP scope failure

MVP rule:

- Every MVP row must include `Korea Republic` as either `home_team` or `away_team`.

Likely cause:

- `matches.csv` was generated from global data without Korea filtering.
- Team naming differs from `Korea Republic`.

Fix direction:

- Verify `KOREA_TEAM_NAME` in `build_dataset.py`.
- Confirm raw data uses a supported alias or canonical team name.
- If needed, update team mapping/normalization logic before rebuilding.

### 7. Score leakage failure

Rule:

- `features.csv` and `features_global.csv` must not contain final-score columns such as `home_score` or `away_score`.

Reason:

- Scores are only allowed to create labels.
- Scores must not become model input features.

Fix direction:

- Check `src/features/make_features.py` and ensure score columns are dropped from the feature table.

### 8. source_target_scope mismatch

Expected values:

- Korea MVP: `source_target_scope = korea`
- Global expansion: `source_target_scope = home`

Likely cause:

- `make_features.py` was run with the wrong `--target-scope`.

Fix:

```bash
python src/features/make_features.py --target-scope korea
python src/features/make_features.py --target-scope home
python src/data/validate_preprocessing.py --scope both
```

## After PASS

Only after preprocessing validation passes should you continue.

MVP:

```bash
python src/models/train_baseline.py
python src/models/calibrate.py
python src/models/predict.py
python src/models/evaluate.py
```

Global expansion:

```bash
python src/models/train_baseline.py \
  --features-path data/processed/features_global.csv \
  --run-name global_baseline

python src/models/calibrate.py \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_model.pkl \
  --run-name global_baseline
```

Simulation scaffold:

```bash
python src/simulation/run_tournament.py
```

## Generated Artifact Policy

The following files are generated validation artifacts and should not be committed by default:

```text
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
The preprocessing validation gate has been added to the project workflow.
The next model-training step should proceed only after validate_preprocessing.py passes.
```

If validation was run only with the built-in demo dataset, say:

```text
The pipeline was validated on the built-in demo dataset. Real-data validation is still required after adding confirmed raw match CSV files.
```

If validation passes on real raw data, say:

```text
The preprocessing gate passed on the current raw dataset, including checks for required columns, missing values, duplicate rows, target labels, MVP scope, source target scope, and final-score leakage.
```
