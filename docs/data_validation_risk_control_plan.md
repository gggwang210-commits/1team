# Data Validation and Risk Control Plan

## 1. Purpose

This document defines the project plan for controlling data-source, raw-structure, feature-leakage, ranking/rating, and generated-artifact risks before model training.

The project rule is simple: data validation comes before model performance. A model score is not meaningful if the raw source is unclear, the feature table contains leakage, or generated artifacts are mixed with source code.

This plan does not run preprocessing, model training, calibration, or tournament simulation. It defines the validation controls that must be satisfied before those steps can be trusted.

## 2. Current Risk Summary

| Risk | Impact | Current control | Remaining gap | Next mitigation |
| --- | --- | --- | --- | --- |
| `source_url` is not confirmed | The team cannot prove where the raw data came from | `data/raw/SOURCES.md` and `source_manifest.csv` require source URL metadata | Placeholder values may still exist | Research candidate sources and update manifest with real URLs |
| `source_owner` is not confirmed | Dataset accountability and provenance remain weak | Manifest has a `source_owner` field | Owner may be unknown or ambiguous | Confirm maintainer, organization, or author before `verified` |
| License or terms are not confirmed | The team may use data in a way that is not allowed | Manifest has a `license` field and SOURCES.md requires license review | Terms may be missing, vague, or incompatible | Mark as `pending` or `rejected` until confirmed |
| Raw file does not exist | Source validation fails and preprocessing cannot be trusted | `validate_sources.py` checks raw file existence | Real CSV files are not yet placed in `data/raw/` | Add raw files only after source review |
| `expected_columns` do not match raw CSV | Preprocessing may silently fail or standardize the wrong fields | `validate_sources.py` checks expected columns | Manifest may not reflect actual raw headers | Update manifest or add explicit alias mapping |
| Rating source is not confirmed | Team strength features may be weak or unsupported | SOURCES.md compares FIFA ranking, World Football Elo, and self-computed Elo | No final rating source is selected | Research sources and keep status `pending` until verified |
| Time leakage is possible | Model may use future information and report inflated results | Preprocessing validation checks score leakage columns | Rating/ranking dates and rolling features still need time-aware checks | Enforce `rating_date <= match_date` and chronological feature generation |
| Demo fallback may be misunderstood | Demo-only results may be presented as real-data evidence | SOURCES.md distinguishes demo data and real raw data | Model output may still be interpreted incorrectly | Label demo-only runs as smoke tests only |
| Generated artifacts may be committed | Repository review quality and reproducibility can degrade | README and generated artifact policy list local outputs | New artifacts may be accidentally committed | Keep reports/models/data processed outputs out of source commits unless explicitly requested |
| FIFA ranking may be used as the only strength signal | Ordinal rank may be less predictive than rating differences | SOURCES.md documents ranking/rating candidates | No ablation experiment has been run | Compare FIFA ranking, external Elo, and self-computed Elo features |

## 3. Source Verification Checklist

Before changing any raw source to `verified`, confirm every item below.

- [ ] `source_url` is confirmed.
- [ ] `source_owner` is confirmed.
- [ ] License or terms of use are confirmed.
- [ ] `download_date` is recorded.
- [ ] `raw_file_name` is finalized.
- [ ] `expected_columns` are checked against the actual raw CSV headers.
- [ ] Row count is checked.
- [ ] Date range is checked.
- [ ] `python src/data/validate_sources.py` passes.
- [ ] `reports/source_validation.md` is reviewed.

A source should remain `pending` if any item is incomplete. A source should be marked `rejected` if its origin, license, structure, or project fit is unsuitable.

## 4. Raw CSV Structure Validation

`data/raw/source_manifest.csv` must describe the actual raw CSV structure. The `expected_columns` field should match real raw headers, not guessed or already-standardized names unless the raw file actually uses those names.

If raw CSV columns differ from the project standard, use one of two responses:

### A. Update `source_manifest.csv` to real raw column names

Use this option when the raw file is valid and the manifest placeholder is wrong. The manifest should describe the raw input truth.

### B. Add a standardization rule in `build_dataset.py`

Use this option when the raw file uses a known synonym such as `home_goals` instead of `home_score`. The alias mapping should convert raw columns into the project's standard processed schema.

Do not confuse original raw columns with standardized processed columns. The manifest protects raw-source transparency; preprocessing code handles standardization.

## 5. Ranking / Rating Feature Risk Control

The project should compare ranking/rating candidates before treating any one strength signal as final.

| Candidate | Required checks |
| --- | --- |
| FIFA ranking history | Source reliability, license or terms, date granularity, whether ranking values are known before match date, `rank_diff` feature design, missing value policy, interpretability, comparison against Elo-style features |
| World Football Elo Ratings | Source reliability, license or terms, date granularity, whether rating values are known before match date, `elo_diff` feature design, missing value policy, interpretability, comparison against FIFA ranking and baseline features |
| Self-computed Elo rating | Raw match-result source reliability, chronological computation method, initial rating, K-factor, home advantage, goal-difference multiplier, leakage-safe calculation, missing-team policy, comparison against external ratings |

Feature form guidance:

- FIFA ranking may support `home_rank`, `away_rank`, and `rank_diff`.
- Rating sources may support `home_rating`, `away_rating`, and `rating_diff`.
- Elo sources may support `home_elo`, `away_elo`, and `elo_diff`.

The project should not select a final ranking/rating feature only because it is familiar or official. It should compare predictive usefulness using validation metrics.

## 6. Time Leakage Prevention

No ranking, rating, rolling, or form feature may use information that was unavailable before the match being predicted.

Required principles:

- Any rating/ranking feature must use values available on or before the match date.
- If the feature has a release date, use the latest value released before the match date.
- If self-computed Elo is used, the feature for each match must be calculated using only matches that happened before that match.
- Tournament simulation must not use post-tournament results, future rankings, or future ratings.

Validation checks to enforce or review:

- `rating_date <= match_date`
- Rolling features use only matches before `match_date`
- Final score columns are never included in the model feature matrix
- `target_result` and `target_result_korea_perspective` are never included in the feature matrix

## 7. Demo Fallback Risk Control

The built-in demo dataset is a development convenience and smoke-test tool. It is not evidence for a real model claim.

Rules:

- Demo dataset results are for pipeline smoke tests only.
- Demo dataset results must not be described as real-data model performance.
- If source validation fails, preprocessing should not continue in the formal pipeline.
- `build_dataset.py` demo fallback is not a substitute for verified raw sources.

Safe wording:

```text
This run validates the pipeline mechanics only. It does not support a real-data model claim.
```

## 8. Generated Artifact Policy

The following are generated artifacts and should not be committed by default:

- `reports/source_validation.csv`
- `reports/source_validation.md`
- `reports/preprocessing_validation.csv`
- `reports/preprocessing_validation.md`
- `reports/data_quality_summary.md`
- `reports/team_mapping_validation.md`
- `reports/unmapped_teams.csv`
- `reports/*calibration*`
- `models/*.pkl`
- `data/processed/*.csv`

Generated outputs may be attached separately for review or presentation if the team explicitly decides to preserve a run snapshot. They should not be mixed with source-code changes by default.

## 9. Validation Gates

| Gate | PASS condition | FAIL rule |
| --- | --- | --- |
| 1. Source validation | `validate_sources.py` passes and `source_validation.md` is reviewed | Stop before preprocessing |
| 2. Preprocessing validation | `validate_preprocessing.py` passes for the intended scope | Stop before modeling |
| 3. Feature leakage check | No score, target, post-match, or future rating columns enter the feature matrix | Do not make a model claim |
| 4. Baseline training | Training script completes with saved metrics and model artifact locally | Do not continue to calibration until baseline output is inspected |
| 5. Calibration validation | Log Loss, Brier Score, and calibration report are reviewed | Do not make a probability-quality claim |
| 6. Simulation readiness check | Calibrated probabilities, tournament inputs, and source assumptions are validated | Do not make a tournament or champion-probability claim |

## 10. Failure Handling Rule

Use the following rule set consistently:

```text
No source validation PASS, no preprocessing.
No preprocessing PASS, no modeling.
No leakage check PASS, no model claim.
No calibration validation PASS, no probability claim.
No simulation readiness PASS, no tournament claim.
```

Failures should be treated as useful signals. A failed validation gate identifies what must be fixed before the project can make stronger claims.

## 11. Expert Review Checklist

Use these questions before presenting results or moving to the next stage.

- Who created this dataset?
- Are the usage terms clear?
- Is this raw CSV reproducible from the documented source?
- Are column definitions clear?
- Was the rating value available before the match date?
- Has target leakage been removed?
- Is there a plan to compare FIFA ranking and Elo rating features?
- Will the evaluation include Log Loss, Brier Score, and Calibration Curve in addition to Accuracy?
- Are demo results clearly separated from real-data results?
- Are generated artifacts kept separate from source code?

## 12. Next Action Plan

1. Research international match-result data candidates.
2. Research team strength rating candidates.
3. Confirm `source_url`, `source_owner`, and license or terms.
4. Update `source_manifest.csv` with real source values.
5. Place raw CSV files under `data/raw/`.
6. Run `python src/data/validate_sources.py`.
7. Run `bash scripts/validate_preprocessing_pipeline.sh`.
8. Design FIFA ranking vs Elo rating ablation study.
9. Add `rating_diff` or `elo_diff` features after source validation is stable.
10. Prepare simulation only after calibration has been reviewed.
