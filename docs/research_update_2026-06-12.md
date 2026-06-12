# Research Update — 2026-06-12

## 목적

1team 월드컵 예측 프로젝트의 미해결 데이터 항목(공식 참가국·조 편성·일정, 대회 규칙, raw 데이터 소스 메타데이터)을 웹 리서치로 확인하고, skeleton 파일들을 검증된 값으로 업데이트한 기록이다. 대회가 2026-06-11 개막했으므로 그동안 TBD였던 토너먼트 구조 데이터가 모두 확정 가능해졌다.

인식론 레이블: 아래 내용 중 [FACT]는 복수 매체 교차 확인, [PENDING]은 공식 FIFA 문서 재검증 필요, [UNKNOWN]은 이번 리서치에서 확정하지 못한 항목.

## 확인된 사실 요약

[FACT] 최종 조 추첨은 2025-12-05 워싱턴 DC 케네디센터에서 진행됐고, 2026-03 플레이오프 종료로 48개국이 모두 확정됐다. 대회는 2026-06-11 ~ 07-19, 총 104경기, 12개 조(A~L) × 4팀, 조 1·2위와 3위 상위 8팀이 32강에 진출한다. 결승은 뉴저지 메트라이프 스타디움.

[FACT] 대한민국은 Group A: Mexico(개최국), South Africa, Korea Republic, Czechia. 한국 조별 일정:

| 경기 | 일자(현지) | 상대 | 장소 |
| --- | --- | --- | --- |
| 1차전 | 6/11 20:00 | Czechia | Estadio Akron, 과달라하라 |
| 2차전 | 6/18 20:00 | Mexico | Estadio Akron, 과달라하라 |
| 3차전 | 6/24 19:00 | South Africa | Estadio BBVA, 몬테레이 |

[FACT] 개막전 결과: Mexico 2-0 South Africa. [UNKNOWN] 한국 vs 체코 결과는 조회 시점에 확정 보도를 확보하지 못함 — 팀이 공식 결과로 raw 데이터에 반영할 것.

[FACT] 플레이오프 승자: Path A 보스니아 헤르체고비나, Path B 스웨덴, Path C 튀르키예, Path D 체코(덴마크전 승부차기), 대륙간 Path 1 DR콩고, Path 2 이라크.

[FACT] 녹아웃 무승부 처리: 연장 30분(15분×2) 후 승부차기.

[PENDING] 조별 순위 tiebreaker 세부 순서는 보도 간 서술이 갈린다(일반 FIFA 관례인 전체 골득실 우선 vs 일부 매체의 상대전적 우선 서술). bracket.json에는 후보 순서를 두되 `PENDING_OFFICIAL_VERIFICATION`으로 표시했다. 시뮬레이션 구현 전 FIFA 공식 대회 규정 문서로 확정해야 한다. 3위 8팀 선정 기준도 동일하게 검증 필요.

## 업데이트된 파일

| 파일 | 변경 내용 | 상태 플래그 |
| --- | --- | --- |
| `data/tournament/participants.json` | 48개국 전체 + 조 편성 + 진출 경로 확정 기입 | `WEB_VERIFIED_PENDING_TEAM_REVIEW` |
| `data/tournament/schedule.json` | Group A 6경기 확정 일정 + 대회 핵심 구조(104경기, 32강 시작일, 결승) | `WEB_VERIFIED_PENDING_TEAM_REVIEW` |
| `data/tournament/bracket.json` | 12조/32강 진출 규칙·녹아웃 무승부 정책 확정, tiebreaker는 후보+PENDING 표시 | `FORMAT_VERIFIED_RULES_PENDING_OFFICIAL_DOC` |
| `data/mappings/team_name_mapping.csv` | 31행 → 51행. 2026 본선 48개국 100% 커버. Türkiye/Turkey, Czechia/Czech Republic, Cabo Verde, Curaçao, DR Congo/Zaire 등 고위험 표기 혼용 alias 추가 | 초안 → 본선 커버 완료 |
| `data/raw/source_manifest.csv` | Elo·FIFA 랭킹 소스 후보 URL/소유자/라이선스 후보 기입, 참가국 JSON 출처 행 추가 | 전 행 `pending` 유지 |

설계 원칙 준수: 기존 스키마(컬럼·키 구조)는 변경하지 않았으므로 `run_tournament.py`의 스키마 검증과 MVP smoke test 경로는 깨지지 않는다. `verification_status`는 의도적으로 `pending` 유지 — 실제 raw CSV 다운로드와 `validate_sources.py` PASS 전에는 `verified`로 올리지 않는다는 프로젝트 규칙을 따랐다.

## Raw 데이터 소스 리서치 결과

**international_results.csv (martj42)** — [FACT] 기존 manifest의 출처·CC0-1.0 라이선스 방향은 유효한 후보. `expected_columns`에 실제 results.csv가 포함하는 `tournament;city;country;neutral` 컬럼을 추가했다(특히 `neutral`은 이미 `build_dataset.py`의 COLUMN_ALIASES와 feature의 `is_neutral`에 직결). 다운로드는 PC/Codespaces에서 수행 후 `download_date` 기록 → `validate_sources.py` 실행.

**Elo 레이팅 (eloratings.net)** — [PENDING] 사이트 이용약관·데이터 추출 방식 미확정. SOURCES.md의 기존 판단(elo_diff가 rank_diff보다 예측 피처로 유망)은 유지하되, 약관 확인 전 `TERMS_UNCONFIRMED` 표시. 약관이 불명확하면 self-computed Elo(martj42 raw로 직접 계산)로 전환하는 것이 라이선스 리스크가 가장 낮다. [RECOMMENDATION]

**FIFA 랭킹** — [PENDING] Kaggle cashncarry/fifaworldranking 미러를 후보로 기입. 다운로드 시점에 라이선스·컬럼·최종 갱신일 확인 필요.

## 다음 행동 (우선순위순)

1. **PC/Codespaces에서 raw 데이터 확보**: martj42 results.csv → `data/raw/international_results.csv` 저장, manifest `download_date` 기입 → `python src/data/validate_sources.py` → PASS 시 `bash scripts/validate_preprocessing_pipeline.sh`.
2. **한국 vs 체코 결과 확인·기록**: 공식 결과 확정 후 raw 결과 데이터 갱신 정책 결정(대회 진행 중 데이터 버전 관리 — manifest에 snapshot 날짜 기록).
3. **FIFA 공식 규정으로 tiebreaker 확정**: bracket.json의 `ranking_tiebreakers_status`를 해소한 뒤 group-stage 시뮬레이션 구현 착수.

## 한계

이 문서의 사실 확인은 2026-06-12 기준 보도·Wikipedia 교차 확인이며, FIFA 공식 1차 자료 검증을 대체하지 않는다. 시뮬레이션 결과를 외부에 제시하기 전 participants/schedule/bracket의 `*_PENDING_*` 플래그를 모두 해소해야 한다.
