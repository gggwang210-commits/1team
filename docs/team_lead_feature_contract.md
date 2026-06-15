# Team Lead 52-Feature Model Input Contract

## Purpose

This document fixes the team lead preprocessing baseline as the model-input schema for future GitHub preprocessing, training, and simulation work.

The machine-readable contract is stored in:

- `data/schema/team_lead_features.json`

This contract is derived from the `features.json` artifact in the shared team preprocessing output reviewed on 2026-06-15.

## Scope

This document defines the schema contract only. It does not commit generated training or prediction CSVs and does not claim that the GitHub preprocessing code already reproduces the team lead pipeline.

## Canonical model-input files

The team lead preprocessing baseline uses these generated files:

| File | Role | Commit policy |
| --- | --- | --- |
| `features.json` | Source 52-feature list | Converted into schema contract. |
| `X_train.csv` | Training feature matrix | Generated artifact; do not commit by default. |
| `X_test.csv` | Test feature matrix | Generated artifact; do not commit by default. |
| `y_train.csv` | Training labels | Generated artifact; do not commit by default. |
| `y_test.csv` | Test labels | Generated artifact; do not commit by default. |
| `w_train.csv` | Training sample weights | Generated artifact; do not commit by default. |
| `wc2026_matches.csv` | 2026 group-stage prediction input | Generated artifact; do not commit by default unless team explicitly approves. |

## Feature count

The model-input contract contains exactly **52 features**.

Any model-training matrix must contain exactly these 52 features, in this order unless a later versioned schema explicitly changes the order.

## Feature list

### Elo strength

- `delta_elo`
- `home_elo`
- `away_elo`

### Short-term form

- `home_form`
- `away_form`
- `home_form_missing`
- `away_form_missing`
- `gap_form`

### Match context

- `neutral`
- `is_wc`

### Rolling four-year team performance

- `home_goals_scored_last_4y`
- `home_goals_received_last_4y`
- `home_wins_last_4y`
- `home_draws_last_4y`
- `home_losses_last_4y`
- `home_matches_last_4y`
- `home_goal_diff_last_4y`
- `away_goals_scored_last_4y`
- `away_goals_received_last_4y`
- `away_wins_last_4y`
- `away_draws_last_4y`
- `away_losses_last_4y`
- `away_matches_last_4y`
- `away_goal_diff_last_4y`
- `home_win_rate_4y`
- `home_goals_per_match_4y`
- `away_win_rate_4y`
- `away_goals_per_match_4y`
- `gap_win_rate_4y`
- `gap_goals_per_match_4y`

### World Cup history

- `home_wc_participations`
- `away_wc_participations`
- `home_wc_titles`
- `away_wc_titles`
- `gap_wc_participations`
- `gap_wc_titles`

### Host flags

- `home_is_host`
- `away_is_host`

### Home-away gap features

- `gap_goal_diff`
- `gap_wins`

### Continent one-hot features

- `home_continent_AFC`
- `home_continent_CAF`
- `home_continent_CONCACAF`
- `home_continent_CONMEBOL`
- `home_continent_OFC`
- `home_continent_UEFA`
- `away_continent_AFC`
- `away_continent_CAF`
- `away_continent_CONCACAF`
- `away_continent_CONMEBOL`
- `away_continent_OFC`
- `away_continent_UEFA`

## Label contract

The label column is:

- `y`

The label is encoded from the home-team perspective:

| Result | Meaning | Encoded value |
| --- | --- | ---: |
| `A` | Away win | 0 |
| `D` | Draw | 1 |
| `H` | Home win | 2 |

Allowed label values are only:

```text
0, 1, 2
```

## Train/test split contract

The team lead baseline uses a date-based split:

```text
train: date < 2022-01-01
test:  date >= 2022-01-01
```

This split is for model evaluation. The 2026 World Cup group-stage prediction input is handled separately through `wc2026_matches.csv`.

## Leakage exclusion contract

The 52-feature model input must not include score, result, target, or match-identity metadata columns.

Excluded score columns:

- `home_score`
- `away_score`

Excluded result/target columns:

- `result`
- `target_result`
- `target_result_korea_perspective`
- `y`

Excluded metadata columns from model feature matrices:

- `date`
- `home_team`
- `away_team`
- `tournament`
- `city`
- `country`
- `year`
- `match_id`
- `group`
- `round`

Important boundary: `wc2026_matches.csv` may keep `group`, `round`, `home_team`, and `away_team` as prediction-input metadata, but the model prediction matrix extracted from it must use only the 52 contract features.

## Generated artifact boundary

The following files are generated artifacts and should not be committed by default:

- `results_preprocessed.csv`
- `X_train.csv`
- `X_test.csv`
- `y_train.csv`
- `y_test.csv`
- `w_train.csv`
- `wc2026_matches.csv`

The repository should commit schema, validation tests, and reproducible scripts first. Generated CSVs may be attached to reports or stored outside version control unless the team explicitly approves committing them.

## Required validation tests

Follow-up tests should verify:

1. `data/schema/team_lead_features.json` has `feature_count = 52`.
2. The schema contains exactly 52 unique feature names.
3. `X_train.csv` and `X_test.csv`, when generated locally, contain exactly the schema feature names.
4. Label files contain only `0`, `1`, and `2`.
5. `w_train.csv` has one non-negative numeric weight per training row.
6. Score/result/metadata leakage columns are absent from model matrices.
7. The train/test split follows `2022-01-01`.
8. `wc2026_matches.csv`, when generated locally, contains metadata plus the 52 schema features.

## Presentation-safe wording

> The team lead preprocessing baseline is now fixed as a 52-feature model-input contract. The GitHub repository documents the schema and will validate future preprocessing outputs against it before making model-performance or tournament-simulation claims.

## Unsafe wording

Avoid these claims until follow-up code and tests are complete:

- The GitHub code fully reproduces the team lead preprocessing pipeline.
- The generated CSVs are committed source-of-truth files.
- The model performance is final.
- The 2026 tournament simulation is complete.
- Champion probabilities are final.
