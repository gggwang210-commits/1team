# Team Lead Preprocessing Alignment - 2026-06-15

## Purpose

This note records the decision to align the GitHub project direction with the team lead preprocessing baseline from the shared Google Drive export reviewed on 2026-06-15.

The project should now treat the team lead preprocessing pipeline as the primary data foundation for modeling and simulation work.

## Alignment decision

The GitHub project should move from the earlier lightweight global baseline pipeline toward the team lead preprocessing baseline.

Primary baseline owner/context:

- Team context: Mirae Convergence Education Center, Team 1 machine-learning project.
- Team lead preprocessing owner: Heo Byeong-cheol.
- Reviewed materials: shared project ZIP export containing preprocessing specification, notebooks, preprocessed CSV outputs, 2026 match input data, EDA notebook, task tracker, meeting notes, and reference materials.

## Verified baseline artifacts from shared materials

The reviewed shared folder contains the following preprocessing outputs:

| Artifact | Rows | Columns | Role |
| --- | ---: | ---: | --- |
| `results_preprocessed.csv` | 45,797 | 65 | Full preprocessed match table with metadata, labels, and engineered features. |
| `X_train.csv` | 41,299 | 52 | Training feature matrix. |
| `X_test.csv` | 4,498 | 52 | Test feature matrix. |
| `y_train.csv` | 41,299 | 1 | Training label, encoded as A=0, D=1, H=2. |
| `y_test.csv` | 4,498 | 1 | Test label, encoded as A=0, D=1, H=2. |
| `w_train.csv` | 41,299 | 1 | Training sample weights by tournament importance. |
| `features.json` | 52 | - | Canonical 52-feature list for model input. |
| `wc2026_matches.csv` | 72 | 56 | 2026 group-stage prediction input table: 12 groups x 6 matches. |

Important boundary: these files are generated artifacts and should not be committed by default unless the team explicitly approves an exception. The repository should first reproduce their generation logic and document their expected schema.

## Team lead preprocessing pipeline

The preprocessing specification defines this pipeline:

1. Team-name normalization.
2. Base match table construction.
3. Elo scraping and merge-as-of join.
4. Short-term form calculation with EWMA.
5. Tournament-importance sample weight generation.
6. Derived feature generation.
7. Final feature table generation and date-based train/test split.

## Source-data stance

The team lead baseline uses:

- `results.csv` as the primary international match-result dataset.
- `former_names.csv` for team-name history and normalization.
- `eloratings.net` scraped history as the primary Elo source.
- `fifa_ranking.csv` as available ranking reference data, with a future need to define snapshot metadata.
- `shootouts.csv` and `goalscorers.csv` as deferred auxiliary data.
- `FIFA World Cup Dataset/train.csv` and `test.csv` as limited reference inputs, not the main training pipeline.
- player-stat datasets as deferred/non-primary because the year-by-year national-team mapping is not stable enough for the current pipeline.

## Feature contract

The model input contract is now recorded in:

- `docs/team_lead_feature_contract.md`
- `data/schema/team_lead_features.json`

The contract is based on the 52-feature list in the shared preprocessing artifact `features.json`.

Feature families:

- Elo strength features: `home_elo`, `away_elo`, `delta_elo`.
- Short-term form features: `home_form`, `away_form`, missing flags, and gap features.
- Tournament context: `neutral`, `is_wc`, and tournament sample weights.
- Rolling four-year team strength: goals, conceded goals, wins, draws, losses, match counts, goal difference.
- Rate-adjusted features: win rate and goals per match.
- World Cup history features: participations and titles.
- Host flags.
- Gap features comparing home and away teams.
- Continent one-hot features.

Labels:

- `H` / home win is encoded as `2`.
- `D` / draw is encoded as `1`.
- `A` / away win is encoded as `0`.

Split policy:

- Train: matches before `2022-01-01`.
- Test: matches from `2022-01-01` onward.
- Purpose: model evaluation. 2026 World Cup prediction is handled through a separate `wc2026_matches.csv` simulation input table.

## EDA findings from team notebook

The team EDA notebook records these working conclusions:

- Label distribution is home-win heavy and draw is the smallest class.
- Tournament type affects class distribution, supporting sample-weight usage.
- `delta_elo` strongly supports the hypothesis that Elo difference is a major predictive signal.
- Four-year win rate appears stronger than EWMA form in the observed EDA, while EWMA form remains useful.
- Upset analysis suggests neutral venue is more useful than short-term form alone for some upset patterns.

These findings should guide model selection and presentation wording, but they should not be presented as final model performance claims until reproducible training metrics are recorded.

## Gap versus current GitHub pipeline

Current GitHub pipeline status before this alignment:

- `src/data/build_dataset.py` creates a standardized match table and supports Korea/global scope.
- `src/features/make_features.py` supports simpler baseline feature generation.
- Tournament bracket and ranking rules have been improved through PRs #50-#53.

Alignment gap:

- The GitHub preprocessing pipeline does not yet reproduce the team lead's 52-feature contract.
- It does not yet implement Elo scraping/merge-as-of as the primary strength feature source.
- It does not yet generate EWMA form, rolling four-year statistics, tournament weights, or `wc2026_matches.csv` in the same form as the team lead baseline.
- It now records the shared preprocessed schema as the canonical model-input contract, but schema validation tests and script reproduction remain follow-up work.

## Required GitHub realignment plan

### PR 1: Documentation and schema contract

- Add this alignment note.
- Add a schema contract document for the 52-feature list.
- Add generated-artifact policy notes for team lead preprocessing outputs.

### PR 2: Preprocessing module structure

Create or refactor modules toward:

- `src/data/team_name_normalization.py`
- `src/data/elo_scraping.py`
- `src/data/elo_join.py`
- `src/features/form_features.py`
- `src/features/rolling_features.py`
- `src/features/tournament_weights.py`
- `src/features/wc_history_features.py`
- `src/features/team_lead_feature_contract.py`

### PR 3: Schema validation tests

Add tests that verify:

- `data/schema/team_lead_features.json` contains exactly 52 model features.
- `X_train.csv` and `X_test.csv`, when generated locally, contain the same feature columns.
- score/result leakage columns are excluded from model input.
- labels are limited to `0`, `1`, `2`.
- train/test split follows `2022-01-01`.

### PR 4: Team lead preprocessing reproduction

Reproduce the notebook pipeline as scriptable Python modules without committing large generated CSVs by default.

### PR 5: Modeling realignment

Train baseline models using:

- `X_train.csv`
- `y_train.csv`
- `w_train.csv` as `sample_weight`
- `X_test.csv`
- `y_test.csv`

Metrics should include:

- Accuracy
- Macro F1
- Log Loss
- Multiclass Brier Score
- Confusion matrix
- Draw-class recall

### PR 6: 2026 group-stage prediction input

Treat `wc2026_matches.csv` as the group-stage prediction input contract.

Important boundary:

- The current 72-match file is group-stage input only.
- It is not a final tournament simulation output.
- Champion probabilities remain blocked until Annexe C, knockout draw-resolution policy, and reproducible simulation outputs are complete.

## Presentation-safe wording

> We are realigning the GitHub project to the team lead preprocessing baseline. The shared preprocessing work already defines a richer 52-feature model-input contract using Elo, EWMA form, four-year rolling team performance, tournament weights, World Cup history, host flags, and continent features. The GitHub repository has documented that schema contract and should now validate and reproduce the pipeline before making model-performance or tournament-simulation claims.

## Unsafe wording

Avoid these claims until follow-up implementation and tests are complete:

- The GitHub code fully reproduces the team lead preprocessing pipeline.
- The 2026 simulation is final.
- The model performance is final.
- Champion probabilities are complete.
- Player-stat features are part of the current primary model.

## Immediate next action

Create a follow-up PR that adds schema validation tests for `data/schema/team_lead_features.json` before refactoring the full preprocessing code.
