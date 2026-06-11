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

## Raw Data Adoption Criteria

Before a raw dataset is accepted for project use, the team should review the following criteria:

| Criterion | Required question |
| --- | --- |
| Source URL | Can the original source URL, repository URL, or download page be identified? |
| Source owner | Can the data owner, maintainer, organization, or author be identified? |
| License or terms | Can the license, public-use rule, or terms of use be identified? |
| Download date | Can the team record when the file was downloaded or exported? |
| Expected columns | Can the raw CSV headers be inspected and recorded in `expected_columns`? |
| Row count | Can the raw file row count be checked and recorded in validation output or notes? |
| Date range | Can the match or ranking date range be identified? |
| Project use case fit | Does the dataset support the intended use, such as global match results or ranking features? |
| Update or version control | Can the team either update the source later or freeze the downloaded version for reproducibility? |

A dataset should not be treated as final evidence only because it is available online. It should be accepted only when its source, structure, and project use case are clear enough to support reproducible preprocessing.

## Source Status Decision Rule

Use `verification_status` consistently in `data/raw/source_manifest.csv`.

| Status | Meaning | Use |
| --- | --- | --- |
| `verified` | Source URL, source owner, download date, license or terms of use, file existence, and expected columns have been checked | Allowed for final evidence after source validation and preprocessing validation pass |
| `pending` | Some metadata or structural details are still unconfirmed, but the source may be kept for development review | Allowed for development and investigation only |
| `rejected` | Source is unsuitable because the source is unknown, license is unclear, required columns are missing, file structure is not usable, or the data does not fit the project use case | Must not be used for modeling, calibration, or simulation |

Decision rules:

```text
verified = usable for final evidence after validation passes
pending = usable for development review only
rejected = not usable for modeling or simulation
```

## Verification Status Policy

| Status | Meaning | Use |
| --- | --- | --- |
| `verified` | Source URL, owner, download date, license, file existence, and expected columns have been checked | Allowed for final evidence after preprocessing validation passes |
| `pending` | File may be used for development, but one or more metadata fields still need confirmation | Allowed for development only; report as pending |
| `rejected` | Source should not be used because metadata, license, or structure is unsuitable | Must not be used for modeling or simulation |

## Minimum Evidence Before Modeling

Before model training, the project should satisfy the minimum evidence requirements below:

1. `data/raw/source_manifest.csv` contains the actual `raw_file_name` values.
2. The raw CSV files listed in the manifest exist under `data/raw/`.
3. `python src/data/validate_sources.py` passes.
4. `reports/source_validation.md` or `reports/source_validation.csv` is reviewed.
5. Demo-dataset-only results are not described as real-data model claims.

If source validation fails, preprocessing should not run. A failure can be normal while raw CSV files or manifest entries are still being prepared.

## Required Rule Before Final Submission

Before final presentation or report submission:

```text
No verified source, no final modeling claim.
No verified source, no final calibration claim.
No verified source, no final simulation claim.
```

## Mobile Workflow

When working from a mobile environment, do not assume that repository commands can be executed locally. Use mobile time for source-governance preparation:

- Collect candidate raw data URLs.
- Confirm the source owner or maintainer.
- Check license or terms of use.
- Inspect or record expected raw CSV columns when possible.
- Prepare instructions to update `data/raw/source_manifest.csv`.
- Prepare the next PC/Codespaces execution checklist.

A mobile workflow can improve data quality even before execution by reducing uncertainty about where the raw data comes from and what it is allowed to support.

## PC/Codespaces Workflow

When a PC or GitHub Codespaces environment is available, run the workflow in this order:

```bash
# 1. Place real raw CSV files under data/raw/
# 2. Update data/raw/source_manifest.csv with actual filenames and metadata
python src/data/validate_sources.py
bash scripts/validate_preprocessing_pipeline.sh
```

If `validate_sources.py` fails, fix the raw files or manifest before running preprocessing. The failure is an intended gate behavior, not a pipeline bug.

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
