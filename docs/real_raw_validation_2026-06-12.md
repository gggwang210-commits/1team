# Real Raw Validation Evidence - 2026-06-12

## Purpose

This document records the real raw data validation evidence used to support the 2026 World Cup tournament data update and preprocessing pipeline checks.

The goal is to keep the validation result reproducible and reviewable without committing generated raw, processed, or report artifacts by default.

## Related pull requests

- PR #43: Update 2026 World Cup tournament data with validation notes
- PR #44: Fix duplicate feature rows in preprocessing output
- PR #45: Fix test import path for GitHub Actions

## Raw dataset

- Source dataset: `martj42/international_results`
- Raw file used locally: `data/raw/international_results.csv`
- Original downloaded file name used locally: `data/raw/international_results_original.csv`
- Raw rows: 49,477
- Raw columns: 9
- Expected columns:
  - `date`
  - `home_team`
  - `away_team`
  - `home_score`
  - `away_score`
  - `tournament`
  - `city`
  - `country`
  - `neutral`

## Canonicalization

The raw source used `South Korea` as a team/country name. For project consistency, the local validation run canonicalized this value to `Korea Republic` in the following fields:

- `home_team`
- `away_team`
- `country`

Observed Korea-related row counts after canonicalization:

- Korea home rows: 552
- Korea away rows: 458

## Source validation result

Command used:

```bash
python src/data/validate_sources.py
```

Result summary:

- PASS: 6
- FAIL: 0

Passed checks:

- `manifest_exists`
- `manifest_required_columns`
- `raw_file_exists`
- `raw_file_readable`
- `raw_file_non_empty`
- `expected_columns_present`

## Preprocessing commands executed

```bash
python src/data/build_dataset.py
python src/features/make_features.py --target-scope korea
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
python src/data/validate_team_mapping.py
python src/data/validate_preprocessing.py --scope both
```

## Processed dataset outputs

- Korea MVP processed matches: 1,007 rows
- Global processed matches: 49,405 rows
- Initial global feature output: 49,405 rows

## Initial preprocessing validation issue

The first preprocessing validation run found one duplicate row in the global feature output.

Initial validation summary:

- PASS: 29
- FAIL: 1

Failure detail:

- Artifact: `features_global.csv`
- Check: `no_duplicate_rows`
- Duplicate rows: 1 duplicate group, 2 rows including the original

Duplicate row observed:

| Field | Value |
|---|---|
| date | `2026-06-06` |
| home_team | `Gibraltar` |
| away_team | `Cayman Islands` |
| rank_diff | `0.0` |
| is_neutral | `0` |
| is_korea_home | `0` |
| target_result | `Win` |
| source_target_column | `target_result` |
| source_target_scope | `home` |
| target_result_korea_perspective | empty |

## Fix applied

PR #44 made duplicate feature-row handling reproducible by applying `drop_duplicates()` before feature output is written.

The relevant behavior is:

- Count rows before duplicate removal.
- Drop fully duplicated feature rows.
- Reset the index.
- Print the number of dropped duplicate rows when duplicates are found.

## Final preprocessing validation result

After duplicate feature-row handling, preprocessing validation passed.

Final validation summary:

- PASS: 30
- FAIL: 0

Score leakage checks:

- `data/processed/features.csv_score_leakage_columns=[]`
- `data/processed/features_global.csv_score_leakage_columns=[]`

## CI status

PR #45 fixed the GitHub Actions test import path issue by inserting the repository root into `sys.path` in `tests/test_make_features.py`.

After that fix, the latest Python package workflow completed successfully.

## Evidence storage policy

Generated raw, processed, and report artifacts were not committed by default.

This document intentionally records a compact evidence summary while leaving the larger generated outputs outside version control unless the team decides otherwise.

## Remaining verification tasks

The following items still require separate review before being marked as fully verified:

1. Official FIFA competition regulations for group-stage tiebreakers.
2. Official FIFA ranking rules for best third-placed teams.
3. Official FIFA Round of 32 bracket mapping, including third-place qualifier combinations.
4. Team decision on whether source manifest candidate rows should remain `pending` or move to `verified` after evidence policy is agreed.
