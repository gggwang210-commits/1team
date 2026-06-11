# Raw Data Execution Checklist

## 1. Purpose

This checklist documents the PC/Codespaces procedure for placing a real raw CSV file under `data/raw/` and running source validation before preprocessing.

Mobile work should be limited to preparation, review, and checklist planning. Do not treat mobile review as source validation execution.

The core rule remains:

```text
No source validation PASS, no preprocessing.
```

## 2. Current Source Candidate

### international_results.csv

| Field | Value |
| --- | --- |
| Source URL | `https://github.com/martj42/international_results` |
| Source owner | `martj42` |
| License | `CC0-1.0` |
| Source file candidate | `results.csv` |
| Target raw file | `data/raw/international_results.csv` |
| Verification status | `pending` |

The `international_results.csv` source candidate has been documented in `data/raw/source_manifest.csv`, but it should not be changed to `verified` until the raw file exists locally and `src/data/validate_sources.py` passes.

### team_strength_ratings.csv

`team_strength_ratings.csv` is not part of this execution step. The rating source is still pending because World Football Elo Ratings, FIFA ranking history, and self-computed Elo have not yet been finalized.

## 3. Files to Prepare

Prepare this file in the project repository:

```text
data/raw/international_results.csv
```

Use `results.csv` from `martj42/international_results` as the source file candidate, but save it locally with the project manifest filename:

```text
international_results.csv
```

This filename must match the `raw_file_name` value in `data/raw/source_manifest.csv`.

## 4. Manual Download Step

Use a PC or GitHub Codespaces environment.

1. Open the `martj42/international_results` repository.
2. Find and inspect `results.csv`.
3. Confirm that the CSV contains the required columns:
   - `date`
   - `home_team`
   - `away_team`
   - `home_score`
   - `away_score`
4. Download `results.csv`.
5. Save it in this project as:

   ```text
   data/raw/international_results.csv
   ```

6. Record the actual download date in `YYYY-MM-DD` format.

## 5. Manifest Update Step

After the file is downloaded, update this field in `data/raw/source_manifest.csv`:

```text
download_date
```

Use the actual download date, for example:

```text
2026-06-12
```

Do not change `verification_status` to `verified` yet. Keep it as `pending` until `python src/data/validate_sources.py` passes and the generated source validation report is reviewed.

## 6. Source Validation Step

Run the source validation command from the repository root:

```bash
python src/data/validate_sources.py
```

This command should create source validation reports under `reports/`.

## 7. Expected PASS Conditions

Source validation should pass only when all required checks succeed.

Expected PASS conditions:

- `data/raw/source_manifest.csv` exists.
- `data/raw/international_results.csv` exists.
- The raw CSV is readable.
- The raw CSV has at least one row.
- The expected columns exist in the raw CSV:
  - `date`
  - `home_team`
  - `away_team`
  - `home_score`
  - `away_score`
- `reports/source_validation.csv` is generated.
- `reports/source_validation.md` is generated.

If any condition fails, do not run preprocessing.

## 8. Failure Cases and Fixes

| Failure case | Likely cause | Fix |
| --- | --- | --- |
| File not found | `international_results.csv` is missing or saved in the wrong location | Confirm the file path is exactly `data/raw/international_results.csv` |
| Expected column missing | The raw CSV columns do not match `expected_columns` in the manifest | Inspect raw headers. Update `source_manifest.csv` if the manifest is wrong, or add alias mapping later if standardization is needed |
| CSV read error | Encoding, delimiter, or file corruption problem | Re-download the file and inspect the CSV format |
| Source metadata incomplete | Manifest still contains placeholder source metadata | Confirm `source_url`, `source_owner`, `license`, and `download_date` |
| Validation report not generated | Python execution failed or `reports/` could not be written | Check the Python traceback and confirm the repository is writable |

## 9. Next Step After PASS

After source validation passes:

1. Review `reports/source_validation.md`.
2. Confirm the actual `download_date` is recorded in `data/raw/source_manifest.csv`.
3. Decide whether `verification_status` can be changed from `pending` to `verified`.
4. Run the full validation pipeline:

   ```bash
   bash scripts/validate_preprocessing_pipeline.sh
   ```

5. Review preprocessing validation reports.
6. Only after validation passes, proceed to feature engineering or modeling work.

## 10. Do Not Do Yet

Do not do the following in this step:

- Do not commit the actual raw CSV yet unless the team explicitly decides to version raw data.
- Do not commit generated reports by default.
- Do not finalize `team_strength_ratings.csv` yet.
- Do not run model training.
- Do not run calibration.
- Do not run tournament simulation.
- Do not change `verification_status` to `verified` before source validation passes.

This checklist prepares the project for real-data validation. It does not by itself prove that the source is verified.
