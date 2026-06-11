# Phase 3-1 Tournament Simulation Contract

## Purpose

This document defines the input/output contract for the future `src/simulation/run_tournament.py` implementation.

The goal of Phase 3-1 is design only. It does not implement tournament simulation code yet.
The simulation should use calibrated match probabilities produced by Phase 2 before generating group-stage, knockout, round-advancement, and champion-probability outputs.

## Command Prompt for Implementation

```text
GitHub 저장소 gggwang210-commits/1team의 Phase 3-1 작업을 진행한다.

현재 상태:
- MVP/global processed data outputs are separated.
- MVP/global feature outputs are separated.
- MVP/global baseline model artifacts are separated.
- src/models/calibrate.py creates calibrated model artifacts and calibration reports.
- Tournament skeleton files already exist:
  - data/tournament/participants.json
  - data/tournament/schedule.json
  - data/tournament/bracket.json

이번 작업 목표:
- src/simulation/run_tournament.py 구현 전에 simulation input/output contract를 문서화한다.
- calibrated model probabilities를 tournament simulation에 연결하는 방식을 정의한다.
- participants.json, schedule.json, bracket.json의 역할을 명확히 한다.
- simulation_summary.csv와 champion_probabilities.csv의 출력 스키마를 정의한다.
- 아직 실제 simulation 코드는 만들지 않는다.

생성 파일:
- docs/simulation_contract.md

수정 파일:
- docs/expansion_strategy.md
- README.md, 필요 시 최소 수정

핵심 원칙:
1. 공식 2026 FIFA 참가국, 조 편성, 경기 일정은 아직 단정하지 않는다.
2. skeleton JSON의 TBD 값은 공식 출처 검증 전까지 유지한다.
3. simulation은 calibrated probabilities를 사용한다.
4. MVP 경로를 깨지 않는다.
5. generated simulation output은 GitHub에 커밋하지 않는다.
6. 이번 단계는 설계 문서화이며 run_tournament.py 구현은 다음 단계로 미룬다.

입력 artifact:
- data/tournament/participants.json
- data/tournament/schedule.json
- data/tournament/bracket.json
- data/processed/features_global.csv
- models/global_baseline_calibrated_model.pkl
- reports/global_baseline_calibration_report/calibration_metrics.csv

향후 run_tournament.py 기본 입력 후보:
python src/simulation/run_tournament.py \
  --participants-path data/tournament/participants.json \
  --schedule-path data/tournament/schedule.json \
  --bracket-path data/tournament/bracket.json \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_calibrated_model.pkl \
  --run-name global_simulation \
  --n-simulations 10000 \
  --random-seed 42

향후 출력 artifact 후보:
- reports/simulation_summary.csv
- reports/champion_probabilities.csv
- reports/round_advancement_probabilities.csv
- reports/group_standings_simulation.csv
- reports/simulation_run_metadata.md

simulation_summary.csv 후보 컬럼:
- run_name
- n_simulations
- random_seed
- participants_path
- schedule_path
- bracket_path
- model_path
- generated_at
- notes

champion_probabilities.csv 후보 컬럼:
- team
- champion_probability
- champion_count
- n_simulations

round_advancement_probabilities.csv 후보 컬럼:
- team
- group
- round_of_32_probability
- round_of_16_probability
- quarter_final_probability
- semi_final_probability
- final_probability
- champion_probability

주의사항:
- draw 처리, 승점 동률 처리, knockout 승부차기 가정은 명시적으로 별도 정책으로 둔다.
- 실제 FIFA tie-breaker 규칙은 공식 문서 확인 전까지 단정하지 않는다.
- 초기 구현에서는 simplified tie-breaker를 사용할 수 있으나 README/docs에 명확히 표시한다.
- model probability가 class order를 어떻게 반환하는지 확인해야 한다.
- calibrated probability 품질이 낮으면 simulation 결과를 최종 주장으로 사용하지 않는다.

검증 기준:
- docs/simulation_contract.md가 존재한다.
- docs/expansion_strategy.md의 Phase 3 Next Actions가 simulation contract 기반으로 갱신된다.
- generated simulation output은 아직 생성하지 않는다.
- run_tournament.py는 이번 단계에서 만들지 않는다.

권장 커밋 메시지:
docs: add tournament simulation contract
```

## Inputs

| Input | Role | Status |
| --- | --- | --- |
| `data/tournament/participants.json` | Participant/team metadata for tournament simulation | Skeleton, not official |
| `data/tournament/schedule.json` | Match list and stage metadata | Skeleton, not official |
| `data/tournament/bracket.json` | Group and knockout advancement structure | Skeleton, not official |
| `data/processed/features_global.csv` | Model-ready global feature table | Generated locally |
| `models/global_baseline_calibrated_model.pkl` | Calibrated global match probability model | Generated locally |
| `reports/global_baseline_calibration_report/calibration_metrics.csv` | Probability-quality evidence before simulation | Generated locally |

## Future CLI Shape

```bash
python src/simulation/run_tournament.py \
  --participants-path data/tournament/participants.json \
  --schedule-path data/tournament/schedule.json \
  --bracket-path data/tournament/bracket.json \
  --features-path data/processed/features_global.csv \
  --model-path models/global_baseline_calibrated_model.pkl \
  --run-name global_simulation \
  --n-simulations 10000 \
  --random-seed 42
```

Optional explicit output arguments can be added later:

```bash
python src/simulation/run_tournament.py \
  --output-dir reports/simulation_global \
  --champion-output-path reports/champion_probabilities.csv \
  --round-output-path reports/round_advancement_probabilities.csv
```

## Output Contract

### `reports/simulation_summary.csv`

| Column | Meaning |
| --- | --- |
| `run_name` | User-provided simulation run name |
| `n_simulations` | Number of Monte Carlo simulations |
| `random_seed` | Fixed random seed for reproducibility |
| `participants_path` | Participant JSON path used in the run |
| `schedule_path` | Schedule JSON path used in the run |
| `bracket_path` | Bracket JSON path used in the run |
| `model_path` | Calibrated model path used in the run |
| `generated_at` | Timestamp when the report was created |
| `notes` | Assumptions or warnings |

### `reports/champion_probabilities.csv`

| Column | Meaning |
| --- | --- |
| `team` | Canonical team name |
| `champion_probability` | Estimated probability of becoming champion |
| `champion_count` | Number of simulations won by the team |
| `n_simulations` | Total simulation count |

### `reports/round_advancement_probabilities.csv`

| Column | Meaning |
| --- | --- |
| `team` | Canonical team name |
| `group` | Group name or placeholder |
| `round_of_32_probability` | Probability of reaching Round of 32 |
| `round_of_16_probability` | Probability of reaching Round of 16 |
| `quarter_final_probability` | Probability of reaching quarter-final |
| `semi_final_probability` | Probability of reaching semi-final |
| `final_probability` | Probability of reaching final |
| `champion_probability` | Probability of winning tournament |

### `reports/group_standings_simulation.csv`

| Column | Meaning |
| --- | --- |
| `simulation_id` | Simulation iteration ID |
| `group` | Group name |
| `team` | Canonical team name |
| `points` | Simulated group-stage points |
| `wins` | Simulated wins |
| `draws` | Simulated draws |
| `losses` | Simulated losses |
| `goals_for` | Optional future field; may be unavailable in early simulation |
| `goals_against` | Optional future field; may be unavailable in early simulation |
| `rank_in_group` | Final simulated group rank |

## Assumptions to Keep Explicit

1. **Official data status**
   - Participant, schedule, and bracket files are skeletons until official source verification.
   - `TBD` values should not be treated as real FIFA data.

2. **Draw handling**
   - Group-stage draws are allowed if the calibrated model predicts W/D/L probabilities.
   - Knockout draws require a separate winner-selection policy after regulation-time draw.

3. **Tie-breaker policy**
   - Full FIFA tie-breakers should not be claimed until verified.
   - Early implementation may use simplified tie-breakers, but the report must label this clearly.

4. **Probability quality**
   - Simulation should use calibrated probabilities where possible.
   - If calibration metrics are poor, simulation output should be treated as a prototype result, not a final forecast.

5. **Reproducibility**
   - `--random-seed` should be required or have a visible default.
   - `--n-simulations` should be recorded in every output report.

## Suggested Phase 3 Implementation Order

1. Create `src/simulation/run_tournament.py` CLI scaffold only.
2. Load and validate tournament JSON files.
3. Load calibrated model and feature table.
4. Generate match probability table for scheduled matches.
5. Simulate group-stage outcomes with a fixed random seed.
6. Add simplified knockout handling.
7. Write simulation summary and champion probabilities.
8. Add README/docs commands after the script runs locally.

## Verification Command for This Design Step

```bash
python - <<'PY'
from pathlib import Path
path = Path('docs/simulation_contract.md')
print(path, 'OK' if path.exists() else 'MISSING')
PY
```

## Non-Goals for This Step

- Do not create `src/simulation/run_tournament.py` yet.
- Do not generate simulation reports yet.
- Do not claim official 2026 FIFA participants, groups, or schedule.
- Do not change the MVP smoke test gate.
