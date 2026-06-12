# FIFA Regulations Verification Plan

## Purpose

This document defines the remaining verification work for FIFA World Cup 2026 tournament rules used by the project simulation logic.

This file is intentionally a verification plan, not a final verified regulation record. The project should not mark FIFA competition rules as fully verified until the official FIFA competition regulations or an equivalent official FIFA source is reviewed and linked.

## Current project status

The project currently models the 2026 tournament as:

- 48 participants
- 12 groups of 4 teams
- Top 2 teams from each group advancing to the knockout stage
- 8 best third-placed teams also advancing
- 32-team knockout stage

These assumptions are structurally represented in the tournament data files and were covered by PR #43.

## Items requiring official verification

### 1. Group-stage ranking tiebreakers

Confirm the exact order of tiebreakers used to rank teams within each group.

Verification target:

- Points
- Goal difference
- Goals scored
- Head-to-head criteria, if applicable
- Fair play / disciplinary points, if applicable
- Drawing of lots or other final procedure, if applicable

Project impact:

- Group standings calculation
- Korea Republic group-stage simulation
- Reproducibility of edge cases where teams finish level on points

### 2. Best third-placed team ranking

Confirm the exact order of criteria used to rank the twelve third-placed teams and select the best eight.

Verification target:

- Points
- Goal difference
- Goals scored
- Fair play / disciplinary points, if applicable
- Drawing of lots or other final procedure, if applicable

Project impact:

- Round of 32 qualification probability
- Korea Republic advancement probability when finishing third
- Global tournament simulation correctness

### 3. Round of 32 bracket mapping

Confirm the official Round of 32 match allocation table.

Verification target:

- Fixed slots for group winners and runners-up
- Candidate opponent groups for each third-placed qualifier slot
- Full combination table for third-placed qualifiers, if published by FIFA

Project impact:

- Knockout bracket construction
- Opponent assignment after group simulation
- End-to-end tournament probability estimates

### 4. Knockout match resolution rules

Confirm the official match resolution procedure for knockout matches.

Verification target:

- Extra time duration
- Penalty shootout procedure
- Whether any special 2026-specific rule changes affect simulation logic

Project impact:

- Knockout simulation
- Win probability modeling after draws in regulation time

## Recommended verification workflow

1. Locate the official FIFA World Cup 2026 competition regulations document or official FIFA match schedule/regulations page.
2. Save the source URL and access date in the research notes.
3. Extract only the relevant regulation sections into a concise summary.
4. Update project data/configuration only after the exact rule order is confirmed.
5. Add tests for edge cases:
   - Two-team tie in a group
   - Three-team tie in a group
   - Third-place ranking tie
   - Third-place qualifier bracket assignment
   - Knockout draw after 90 minutes

## Suggested implementation tasks after verification

- Add a dedicated group ranking utility.
- Add a third-place ranking utility.
- Add tests for ranking edge cases.
- Add a bracket assignment test using the official Round of 32 mapping.
- Update `ranking_tiebreakers_status` only after official verification is complete.

## Current risk status

- `ranking_tiebreakers_status` should remain `PENDING_OFFICIAL_VERIFICATION`.
- Source manifest candidate rows should remain `pending` unless the team decides an evidence policy for raw data and official regulation sources.
- Do not claim full FIFA regulation compliance until the official regulation source is linked and reviewed.

## Notes

A web search performed during this task found public summaries that describe the 2026 format as 12 groups of four, with the top two teams plus eight best third-placed teams advancing to a Round of 32. However, public summaries are not enough to mark the project rules as officially verified.

The project should prefer an official FIFA source for final rule implementation and documentation.
