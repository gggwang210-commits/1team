# Current Project Status - 2026-06-14

## Purpose

This document aligns the project status with the latest GitHub validation evidence and separates safe presentation claims from items that still require official verification.

## Executive Summary

The project should be described as a global-first 2026 FIFA World Cup match prediction pipeline with Korea Republic preserved as a filtered demonstration and smoke-test path.

The repository now contains evidence that raw source validation and preprocessing validation were executed successfully for the current real-data workflow. However, tournament-level claims such as final advancement probabilities, Round of 32 bracket mapping, and champion probabilities still require official FIFA rule verification and reproducible simulation evidence.

New alignment note: as of the 2026-06-15 shared team materials review, the GitHub project should be realigned to the team lead preprocessing baseline before further modeling or final simulation claims.

## Current Verified Evidence

Evidence currently recorded in `docs/real_raw_validation_2026-06-12.md`:

- Source dataset: `martj42/international_results`.
- Local raw file used: `data/raw/international_results.csv`.
- Raw rows: 49,477.
- Raw columns: 9.
- Source validation result: PASS 6 / FAIL 0.
- Korea MVP processed matches: 1,007 rows.
- Global processed matches: 49,405 rows.
- Initial global feature output: 49,405 rows.
- One duplicate feature-row issue was found and then fixed.
- Final preprocessing validation result: PASS 30 / FAIL 0.
- Score leakage checks found no `home_score` or `away_score` leakage columns in the feature tables.
- Latest Python package workflow completed successfully after the import-path fix.

## Current Project Stage

| Area | Status | Interpretation |
| --- | --- | --- |
| Project direction | Global-first | Primary scope is global match-level prediction. |
| Korea Republic path | Preserved | Use as filtered demonstration and legacy smoke-test path. |
| Team lead preprocessing alignment | New baseline selected | See `docs/team_lead_preprocessing_alignment_2026-06-15.md`; code reproduction and schema tests are follow-up work. |
| Raw source validation | Passed evidence recorded | Evidence exists, but generated raw files are not committed. |
| Preprocessing validation | Realignment required | Previous validation evidence exists, but the repository must now align to the team lead 52-feature preprocessing contract. |
| FIFA rules verification | Documented for review | See `docs/fifa_2026_rules_verification.md`; implementation and tests still need follow-up PRs. |
| Tournament participants/schedule/bracket | Article 12.6 mapping aligned; Annexe C pending | Must not be presented as complete tournament simulation support until Annexe C is encoded and tested. |
| Baseline metrics | Requires current reproducible run evidence | Do not overclaim final performance from older MVP reports. |
| Calibration | Pipeline-ready | Use after baseline evidence is stable. |
| Simulation/champion probabilities | Not final | Requires official rules implementation, Annexe C data conversion, team-lead-aligned model inputs, and reproducible simulation output. |

## Team Lead Preprocessing Alignment Note

The team lead preprocessing alignment note is tracked in:

- `docs/team_lead_preprocessing_alignment_2026-06-15.md`

Status summary:

- The shared team materials define a richer 52-feature model-input contract.
- The reference outputs include `results_preprocessed.csv`, `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`, `w_train.csv`, `features.json`, and `wc2026_matches.csv`.
- These are generated artifacts and should not be committed by default.
- GitHub should next add schema-contract documentation and tests before refactoring the full preprocessing pipeline.

## FIFA Rules Verification Note

The FIFA 2026 rules verification note is tracked in:

- `docs/fifa_2026_rules_verification.md`

Status summary:

- Group-stage tiebreaker rules: Verified from official FIFA regulations, implementation follow-up required.
- Best third-placed teams ranking rule: Verified from official FIFA regulations, ranking snapshot metadata follow-up required.
- Round of 32 bracket mapping: Verified from official FIFA regulations, `bracket.json` alignment follow-up required.
- Third-place qualifier combinations: Partially verified because Annexe C is official, but 495 combinations still need machine-readable conversion and tests.

## Safe Presentation Wording

Use this wording in README, reports, slides, and team discussion:

> The project has a global-first ML pipeline for international football match Win/Draw/Loss prediction. We are realigning the GitHub implementation to the team lead preprocessing baseline, which defines a 52-feature model-input contract using Elo, EWMA form, rolling four-year team performance, tournament weights, World Cup history, host flags, and continent features. FIFA 2026 tournament rules have been reviewed and partially implemented, but final simulation outputs and champion-probability claims still require team-lead-aligned model evidence, Annexe C data conversion, and reproducible simulation results.

Avoid these claims unless new evidence is added:

- The full 2026 World Cup prediction system is complete.
- The GitHub code fully reproduces the team lead preprocessing pipeline.
- Champion probabilities are final.
- Tournament bracket mapping is fully implemented and tested.
- Annexe C third-place combinations are fully implemented.
- All source manifest rows are verified.
- Global model performance is production-ready.

## Recommended Next Actions

1. Add a schema contract document for the team lead 52-feature preprocessing baseline.
2. Add tests that validate the 52-feature contract and label encoding.
3. Refactor GitHub preprocessing modules to reproduce the team lead pipeline without committing generated CSVs by default.
4. Decide whether validated source manifest rows should remain `pending` or move to `verified`.
5. Store FIFA ranking snapshot metadata for ranking fallback reproducibility.
6. Convert Annexe C 495 third-place qualifier combinations into machine-readable CSV/JSON.
7. Add tests covering all Annexe C combinations.
8. Re-run team-lead-aligned baseline training from the agreed data snapshot.
9. Record metrics with run date, data snapshot, command history, and feature schema version.
10. Run calibration and record Log Loss / Brier Score before and after calibration.
11. Define knockout draw-resolution policy before tournament simulation.
12. Generate simulation outputs only after the above checks pass.

## Team Review Checklist

Before final presentation, confirm:

- [ ] `docs/real_raw_validation_2026-06-12.md` is referenced as evidence.
- [ ] `docs/fifa_2026_rules_verification.md` is referenced as rules-verification evidence.
- [ ] `docs/team_lead_preprocessing_alignment_2026-06-15.md` is referenced as the preprocessing alignment baseline.
- [ ] Generated artifacts are not treated as committed source of truth.
- [ ] Korea Republic results are described as a filtered use case, not the full project scope.
- [ ] FIFA rules are marked as documented/verified only at the source-review level until implementation tests pass.
- [ ] Any model metric shown in slides has a run date and input data snapshot.
- [ ] Simulation output is clearly separated from model output.

## Status Decision

Current status label:

`VALIDATION_EVIDENCE_RECORDED__TEAM_LEAD_PREPROCESSING_ALIGNMENT_REQUIRED__SIMULATION_IMPLEMENTATION_PENDING`

This label is intentionally conservative. It reflects that prior data and preprocessing gates have evidence, official FIFA rules have been documented, and the project is now being realigned to the team lead preprocessing baseline before final modeling and simulation claims.
