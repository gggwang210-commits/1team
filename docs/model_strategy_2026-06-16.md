# Model Strategy - 2026-06-16

## Current decision

The current recommended modeling story is:

```text
Soft Voting = main Win/Draw/Loss probability model
Poisson = expected-scoreline companion model
Korea Republic = focused scenario-analysis use case
```

This direction is based on the latest Drive model-comparison report, not on a final tournament simulation result.

## Why Soft Voting is the main candidate

Soft Voting currently has the best probability-quality metrics among the compared models:

- Accuracy: `0.6465`
- Macro-F1: `0.5273`
- Log Loss: `0.8000`
- Brier Score: `0.4668`

For a tournament prediction project, Log Loss and Brier Score are more important than raw accuracy because the system needs usable probabilities, not only hard class labels.

## Why Poisson stays in the pipeline

Poisson is not the best current classifier by Log Loss, but it adds a presentation-critical output:

- expected home/away goals
- scoreline probability matrix
- explainable expected score, such as `1-1`, `2-1`, or `1-0`

Use Poisson as a companion model, not as the main probability model unless future evidence changes.

## Metric interpretation

| Metric | Use in this project | Main caution |
| --- | --- | --- |
| Accuracy | Simple headline model comparison | Can hide poor draw handling |
| Macro-F1 | Class-balance sensitivity | Random Forest does well here but weakens probability metrics |
| Log Loss | Probability quality | Primary comparison metric for prediction probabilities |
| Brier Score | Probability calibration quality | Useful before simulation |

## Model roles

| Model | Role |
| --- | --- |
| Logistic Elo-only | Minimal benchmark showing Elo-only limitations |
| Logistic Full | Strong interpretable baseline |
| XGBoost | Strong non-linear benchmark |
| LightGBM | Fast gradient-boosting candidate |
| Random Forest | Draw-sensitivity reference, not current main model |
| Poisson | Expected-scoreline companion |
| Soft Voting | Current main candidate |
| Stacking | Experimental extension; not clearly better yet |

## Presentation-safe wording

Use:

> We compared multiple models under the same train/test split and feature set. Soft Voting currently produced the best Log Loss and Brier Score, so we use it as the main probability model. Poisson is retained to explain expected scores because it can convert expected goals into scoreline probabilities.

Avoid:

> The model predicts the World Cup winner accurately.

Avoid:

> Stacking is the best model.

Avoid:

> Accuracy alone proves our model is strong.

## Engineering follow-up

1. Add reproducible model-comparison execution path.
2. Store current metric snapshot as generated report output, not as manually edited source of truth.
3. Add calibration report for Soft Voting.
4. Add Korea scenario generation from match-probability tables.
5. Add draw-recall improvement experiments only after the main probability pipeline is reproducible.

## Governance note

All external/public claims must separate:

- implemented code
- notebook output
- generated report
- inference from metrics
- presentation recommendation

The current status is strong enough for a team presentation strategy, but not yet enough for final public prediction claims.
