# Drive Model Results Alignment - 2026-06-16

## Purpose

This document records the latest Google Drive project-material review and aligns the GitHub repository direction with the current Team 1 project status.

The 2026-06-16 Drive materials show that the project has moved beyond a generic global-first skeleton and should now be treated as a model-comparison-driven World Cup prediction project.

## Reviewed Drive materials

Reviewed current Drive items:

- `00. 프로젝트 관련정리`
- `2026WC예측_팀회의자료_v2`
- `2026월드컵_기획안_발표.pptx`
- `03. 회의록`

## Latest team direction

The current project direction is:

1. Train a 3-class football match-result classifier for away win / draw / home win.
2. Apply the model output to 2026 World Cup fixtures.
3. Use Soft Voting as the main probability model because it currently has the best validation Log Loss and Brier Score among the compared models.
4. Combine the Soft Voting result with Poisson score prediction so the final presentation can explain both:
   - Win / Draw / Loss probability
   - Expected scoreline
5. Use Korea Republic as a high-value presentation scenario, especially for group-stage and Round-of-16 qualification conditions.

## Current model comparison evidence

The Drive report records the following model-comparison results from `1team_wc2026_report_v2.ipynb`.

| Model | Accuracy | Macro-F1 | Log Loss | Brier | Current interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Soft Voting | 0.6465 | 0.5273 | 0.8000 | 0.4668 | Main model candidate |
| Logistic Full | 0.6450 | 0.5148 | 0.8058 | 0.4683 | Strong linear baseline |
| XGBoost | 0.6452 | 0.5286 | 0.8073 | 0.4698 | Core non-linear candidate |
| Stacking | 0.6430 | - | 0.8060 | - | Added complexity, limited benefit so far |
| LightGBM | 0.6392 | 0.5366 | 0.8135 | 0.4720 | Fast candidate, useful for scale |
| Poisson | 0.6332 | 0.4674 | 0.8161 | 0.4751 | Useful for expected scoreline |
| Logistic Elo-only | 0.6261 | 0.4621 | 0.8290 | 0.4834 | Minimal Elo baseline |
| Random Forest | 0.6147 | 0.5660 | 0.8415 | 0.4931 | Best Macro-F1; strongest draw sensitivity |

## Interpretation boundary

The correct status is not simply `skeleton` anymore.

Safe wording:

> Team 1 has a working model-comparison report over 41,299 training matches and 4,498 validation matches. Among the compared models, Soft Voting currently has the best Log Loss and Brier Score. The recommended presentation direction is Soft Voting for Win/Draw/Loss probabilities plus Poisson for expected scoreline explanation. Korea Republic scenario analysis should be treated as a focused presentation use case, not the only model scope.

Do not claim yet:

- Final 2026 World Cup prediction results are complete.
- Champion probabilities are final.
- Tournament simulation is fully verified.
- Stacking is superior to Soft Voting.
- The GitHub repository already fully reproduces every Drive notebook result.

## Key risks found in the Drive/GitHub gap

| Gap | Risk | Required action |
| --- | --- | --- |
| GitHub still emphasizes baseline/calibration scaffolding | Repository appears behind current team work | Update project spec and status documents |
| Drive report treats Soft Voting as best current model | GitHub may understate current modeling progress | Record model-comparison evidence and next implementation phase |
| Poisson is useful for scoreline even if not best classifier | Presentation may lose explainability if ignored | Keep Poisson as scoreline companion model |
| Random Forest has highest Macro-F1 but poor Log Loss | Team may over-optimize one metric | Explain metric tradeoff clearly |
| Draw recall remains difficult | Public demo may overclaim confidence | Add draw-improvement and calibration checks |
| 2026 tournament data/rules remain partly verification-dependent | Simulation claims can be overstated | Keep rule verification and generated-artifact boundaries explicit |

## GitHub realignment plan

### Phase A - Documentation sync

- Update project specification with the 2026-06-16 Drive evidence.
- Add this alignment document.
- Keep generated Drive CSV/model artifacts out of version control unless the team explicitly decides otherwise.

### Phase B - Model strategy sync

- Treat Soft Voting as the main current model candidate.
- Keep Logistic Full and XGBoost as strong benchmark candidates.
- Keep Poisson as the expected-scoreline companion model.
- Keep Random Forest result for draw-sensitivity discussion, not as the main probability model.

### Phase C - Code implementation follow-up

- Add a reproducible model-comparison script or notebook export path.
- Add a `reports/model_comparison_2026-06-16.md` generated from the agreed metrics snapshot.
- Add probability-calibration checks for Soft Voting.
- Add Korea scenario analysis functions after stable match-probability output exists.
- Add tournament simulation only after official rules and bracket mappings are implemented and tested.

## Recommended team-facing next actions

1. Approve Soft Voting + Poisson as the presentation model story.
2. Decide whether the main deliverable is 72 group-stage fixtures or full 104-match tournament simulation.
3. Assign one member to draw-recall improvement and calibration checks.
4. Assign one member to Korea scenario table generation.
5. Assign one member to README / 발표 스크립트 / GitHub evidence documentation.

## Status label

`DRIVE_MODEL_COMPARISON_REVIEWED__SOFT_VOTING_MAIN_CANDIDATE__POISSON_SCORELINE_COMPANION__SIMULATION_VERIFICATION_PENDING`
