# Current Project Status - 2026-06-14

## Purpose

This document aligns the project status with the latest GitHub validation evidence and separates safe presentation claims from items that still require official verification.

## Executive Summary

The project should be described as a global-first 2026 FIFA World Cup match prediction pipeline with Korea Republic preserved as a filtered demonstration and smoke-test path.

The repository now contains evidence that raw source validation and preprocessing validation were executed successfully for the current real-data workflow. However, tournament-level claims such as final advancement probabilities, Round of 32 bracket mapping, and champion probabilities still require official FIFA rule verification and reproducible simulation evidence.

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
| Raw source validation | Passed evidence recorded | Evidence exists, but generated raw files are not committed. |
| Preprocessing validation | Passed evidence recorded | Duplicate feature-row handling has been fixed. |
| Tournament participants/schedule/bracket | Web-verified / pending team review | Must not be presented as final FIFA-verified data yet. |
| Baseline metrics | Requires current reproducible run evidence | Do not overclaim final performance from older MVP reports. |
| Calibration | Pipeline-ready | Use after baseline evidence is stable. |
| Simulation/champion probabilities | Not final | Requires official rules and reproducible simulation output. |

## Safe Presentation Wording

Use this wording in README, reports, slides, and team discussion:

> The project has a global-first ML pipeline for international football match Win/Draw/Loss prediction. Real raw data source validation and preprocessing validation evidence have been recorded. Korea Republic remains a reproducible filtered demonstration path. Tournament simulation is structurally prepared, but final FIFA rule verification and reproducible simulation outputs are still required before making official advancement or champion-probability claims.

Avoid these claims unless new evidence is added:

- The full 2026 World Cup prediction system is complete.
- Champion probabilities are final.
- Tournament bracket mapping is fully FIFA-verified.
- All source manifest rows are verified.
- Global model performance is production-ready.

## Recommended Next Actions

1. Decide whether validated source manifest rows should remain `pending` or move to `verified`.
2. Verify official FIFA group-stage tiebreakers.
3. Verify official third-place ranking rules.
4. Verify Round of 32 bracket mapping, including third-place qualifier combinations.
5. Re-run global baseline training from the agreed validated data snapshot.
6. Record global baseline metrics with run date, data snapshot, and command history.
7. Run calibration and record Log Loss / Brier Score before and after calibration.
8. Define knockout draw-resolution policy before tournament simulation.
9. Generate simulation outputs only after the above checks pass.

## Team Review Checklist

Before final presentation, confirm:

- [ ] `docs/real_raw_validation_2026-06-12.md` is referenced as evidence.
- [ ] Generated artifacts are not treated as committed source of truth.
- [ ] Korea Republic results are described as a filtered use case, not the full project scope.
- [ ] FIFA rules are marked as official-verified only after source review.
- [ ] Any model metric shown in slides has a run date and input data snapshot.
- [ ] Simulation output is clearly separated from model output.

## Status Decision

Current status label:

`VALIDATION_EVIDENCE_RECORDED__SIMULATION_RULES_PENDING`

This label is intentionally conservative. It reflects that the data and preprocessing gates have evidence, while the tournament simulation layer still needs official-rule verification and reproducible output evidence.
