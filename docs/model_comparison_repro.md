# Model Comparison Reproducibility

## Purpose

This document defines the reproducibility path for the model comparison table used in the presentation.

## Stable Command

```bash
python src/run_model_comparison.py --config configs/model_comparison.yaml
```

## Reference Output

```text
outputs/model_comparison_metrics.csv
```

## Current Status

The current runner regenerates the locked reference metrics table. It does not yet perform full end-to-end retraining from raw data.

Before claiming full retraining reproducibility, connect and verify:

1. data loading
2. preprocessing
3. feature generation
4. train and validation split
5. model parameters
6. metric calculation
7. output schema

## Fixed Reference Values

- Training data: 41,299 matches
- Validation data: 4,498 matches
- Main probability model candidate: Soft Voting
- Auxiliary expected score explanation model: Poisson

## Presentation Rule

Use `outputs/model_comparison_metrics.csv` as the source of truth for model comparison slides.
