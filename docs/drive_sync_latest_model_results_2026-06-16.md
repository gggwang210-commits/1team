# Drive Sync: Latest Model Results

## Source

- Source document: `2026WC예측_팀회의자료_v2`
- Source date: 2026-06-16
- Source notebook noted in Drive: `1team_wc2026_report_v2.ipynb`
- Data scale: 41,299 training matches and 4,498 validation matches

## Why this sync was needed

The Drive review document contains the latest model comparison table. The GitHub reference table previously tracked only a smaller subset of models. This sync updates GitHub so presentation evidence follows the latest reviewed Drive material.

## Updated GitHub reference files

- `outputs/model_comparison_metrics.csv`
- `src/run_model_comparison.py`

## Current model decision

Soft Voting is treated as the current main probability model candidate because it has the best Log Loss and Brier Score in the reviewed comparison.

Poisson is not treated as the best model. It is used as an auxiliary expected score explanation model.

## Model interpretation from latest review

- Soft Voting: main probability candidate
- Logistic Full: strong linear baseline
- XGBoost: nonlinear candidate
- Stacking: limited gain relative to complexity
- LightGBM: fast training candidate
- Poisson: expected score explanation
- Logistic Elo-only: Elo baseline
- Random Forest: draw sensitivity reference

## Important limitations

The latest Drive document includes scenario and simulation discussion, but GitHub should not present full tournament simulation or winner probability as final until FIFA rule logic, third-place qualification, and bracket mapping are verified.

## Next GitHub actions

1. Connect the reference runner to the real training pipeline.
2. Add figure generation from `outputs/model_comparison_metrics.csv`.
3. Add Korea group-stage scenario outputs after official schedule and group data are verified.
4. Add probability calibration and draw-risk report.
5. Keep simulation and winner probability as later-stage outputs until rule verification is complete.
