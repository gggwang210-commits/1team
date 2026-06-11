# Raw Data Sources

## Purpose

This file documents the origin, license, download date, intended use, and verification status of every raw dataset used before preprocessing.

The project must distinguish between:

- **demo data**: built-in fallback rows used only to prove that the pipeline can run end to end.
- **real raw data**: externally sourced CSV files placed in `data/raw/` and documented in `source_manifest.csv`.

Demo-data validation is not the same as real-data validation. Final presentation, modeling claims, calibration claims, and simulation claims should be based on verified real raw data, not only on the built-in demo dataset.

## Required Source Metadata

Every raw CSV file used by the project should have a row in:

```text
data/raw/source_manifest.csv
```

Required metadata fields:

| Field | Meaning |
| --- | --- |
| `raw_file_name` | CSV filename under `data/raw/` |
| `dataset_name` | Human-readable dataset name |
| `source_url` | Original source URL or repository URL |
| `source_owner` | Organization, author, or provider |
| `download_date` | Date the file was downloaded or exported |
| `license` | License or terms of use |
| `expected_columns` | Semicolon-separated columns expected in the raw file |
| `used_for` | Project use case, such as global match results or ranking features |
| `verification_status` | One of `verified`, `pending`, or `rejected` |

## Verification Status Policy

| Status | Meaning | Use |
| --- | --- | --- |
| `verified` | Source URL, owner, download date, license, file existence, and expected columns have been checked | Allowed for final evidence after preprocessing validation passes |
| `pending` | File may be used for development, but one or more metadata fields still need confirmation | Allowed for development only; report as pending |
| `rejected` | Source should not be used because metadata, license, or structure is unsuitable | Must not be used for modeling or simulation |

## Required Rule Before Final Submission

Before final presentation or report submission:

```text
No verified source, no final modeling claim.
No verified source, no final calibration claim.
No verified source, no final simulation claim.
```

## Current Source Placeholders

The rows below are placeholders. Replace `TBD` values after the team confirms the real raw files.

### international_results.csv

| Field | Value |
| --- | --- |
| Dataset name | International football match results |
| Source owner | TBD |
| Source URL | TBD |
| Download date | TBD |
| License | TBD |
| Raw file path | `data/raw/international_results.csv` |
| Expected columns | `date`, `home_team`, `away_team`, `home_score`, `away_score` |
| Used for | Global match-result preprocessing |
| Verification status | `pending` |
| Known limitations | TBD until source is confirmed |

### fifa_rankings.csv

| Field | Value |
| --- | --- |
| Dataset name | FIFA ranking history |
| Source owner | TBD |
| Source URL | TBD |
| Download date | TBD |
| License | TBD |
| Raw file path | `data/raw/fifa_rankings.csv` |
| Expected columns | `rank_date`, `country_full`, `rank`, `total_points` |
| Used for | Ranking feature engineering |
| Verification status | `pending` |
| Known limitations | Ranking merge logic may be added or revised later |

## How to Validate Sources

Run:

```bash
python src/data/validate_sources.py
```

Generated reports:

```text
reports/source_validation.csv
reports/source_validation.md
```

These reports are generated validation artifacts and should not be committed by default.
