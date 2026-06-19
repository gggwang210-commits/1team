# Next Work Priorities - 2026-06-16

## Purpose

This document reduces the next project work into five expert-priority items. The percentage weights reflect expected impact on presentation quality, reproducibility, technical credibility, and risk reduction.

## Priority allocation

| Rank | Work item | Weight | Primary owner type | Output |
| ---: | --- | ---: | --- | --- |
| 1 | Reproduce the model-comparison result in GitHub | 30% | ML/code owner | Reproducible command path and report output |
| 2 | Build the presentation evidence package | 25% | PM/presentation owner | Model story, metric table, slide-safe wording |
| 3 | Generate Korea Republic scenario analysis | 20% | Analysis owner | Korea match probability and qualification scenario table |
| 4 | Add probability-calibration and draw-risk checks | 15% | ML/evaluation owner | Calibration report and draw-handling note |
| 5 | Keep simulation and FIFA-rule verification bounded | 10% | Governance/rules owner | Simulation boundary checklist and rule-risk note |

Total: 100%.

## 1. Reproduce the model-comparison result in GitHub - 30%

### Why this is first

The Drive report is currently the strongest evidence, but the repository must be able to reproduce or at least trace the model-comparison result. Without this, the team can present a strong story but cannot defend the workflow technically.

### Required work

- Add or document a reproducible command path for the current model-comparison run.
- Record input data snapshot, feature schema, random seed, split rule, and output path.
- Generate a model-comparison report table from code rather than only from manually edited notes.
- Keep generated CSV/model artifacts out of version control unless the team explicitly approves.

### Minimum acceptable output

- `reports/model_comparison_YYYY-MM-DD.csv` generated locally.
- `reports/model_comparison_YYYY-MM-DD.md` generated or copied from a reproducible run.
- A README/runbook command showing how to re-run the comparison.

### Done condition

A reviewer can answer: "Which command generated the Soft Voting 0.800 Log Loss result?"

## 2. Build the presentation evidence package - 25%

### Why this is second

The project is in an education-team setting. The next visible performance metric is not only code completeness; it is whether the team can explain the project clearly, defensibly, and persuasively.

### Required work

- Define one clean model story:
  - Soft Voting for Win/Draw/Loss probability.
  - Poisson for expected scoreline.
  - Korea scenario as the main audience-facing example.
- Convert metric results into slide-safe wording.
- Separate fact, inference, assumption, and recommendation.
- Prepare expected Q&A around model choice, draw difficulty, overclaiming, and simulation limits.

### Minimum acceptable output

- One model-selection slide.
- One metric-comparison slide.
- One Korea scenario slide.
- One limitations/next-work slide.

### Done condition

A team member can explain in under one minute why Soft Voting was selected and why Poisson remains useful.

## 3. Generate Korea Republic scenario analysis - 20%

### Why this is third

Korea Republic analysis is the most intuitive presentation hook. It translates abstract model metrics into a concrete question the audience understands: "What does Korea need to advance?"

### Required work

- Produce Korea group-stage match probability table.
- Convert probabilities into expected points and likely scenarios.
- Create 16강 qualification condition examples:
  - required points
  - goal-difference sensitivity
  - opponent-specific win/draw/loss implications
- Avoid claiming final advancement probability unless group rules and simulation are verified.

### Minimum acceptable output

- `korea_scenario_table.csv` or equivalent generated table.
- A slide-ready summary table.
- Three short interpretation bullets.

### Done condition

The presentation can answer: "한국이 16강에 가려면 어떤 조건이 필요한가?" without pretending the full tournament simulation is complete.

## 4. Add probability-calibration and draw-risk checks - 15%

### Why this is fourth

The current model result is strong enough for a team project, but football draws are structurally hard. Also, tournament simulation depends on probability quality, not only class accuracy.

### Required work

- Compare uncalibrated and calibrated probability outputs.
- Report Log Loss and Brier Score before/after calibration.
- Add a draw-specific error note:
  - draw recall
  - draw precision
  - confusion matrix pattern
- Decide whether draw improvement is worth more time or should remain a limitation.

### Minimum acceptable output

- Calibration metric table.
- Confusion matrix or draw-focused metric summary.
- One limitation paragraph for README/slides.

### Done condition

The team can explain that probability quality was checked and that draw prediction remains a known hard case.

## 5. Keep simulation and FIFA-rule verification bounded - 10%

### Why this is fifth

Full 104-match tournament simulation is attractive but can consume too much time and create overclaiming risk. It should remain bounded unless the model-probability table and rules are both stable.

### Required work

- Keep tournament simulation claims marked as pending until rules and bracket logic are verified.
- Confirm group ranking, third-place rules, and knockout mapping before final simulation claims.
- Define a draw-resolution policy for knockout matches.
- Treat champion probability as an optional final-stage output, not the next required deliverable.

### Minimum acceptable output

- A simulation boundary checklist.
- A short rule-risk note in docs or slides.
- Clear wording that champion probability is not final unless simulation evidence exists.

### Done condition

The team avoids saying "we predicted the champion" unless the simulation is actually implemented and reproducible.

## Recommended execution order

1. Freeze the current model metric snapshot.
2. Add a reproducible model-comparison report path.
3. Create the model-selection and metric slides.
4. Generate Korea scenario table.
5. Add calibration and draw-risk checks.
6. Only then expand simulation.

## Expert judgment

The highest expected value is not full simulation first. The best next move is to secure the evidence chain:

```text
Drive result -> GitHub reproducible path -> presentation table -> Korea scenario -> calibrated probability check -> bounded simulation
```

This sequence maximizes technical credibility while protecting the team from overclaiming.
