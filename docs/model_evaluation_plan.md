# Model Evaluation Plan

## Purpose

This document records the team decision to evaluate multiple classroom-learned models under the same data contract and metrics before selecting a final model.

The project should not pre-select a final model only because LightGBM or XGBoost is expected to perform well. LightGBM and XGBoost are strong main candidates for tabular football match data, but the final choice must be based on reproducible evaluation evidence.

## Current modeling status

Current status:

- The team lead 52-feature model-input contract is documented.
- Schema validation tests exist for `data/schema/team_lead_features.json`.
- Preprocessing module scaffold files exist, but full preprocessing reproduction is not complete.
- Final model performance has not been established.
- Final champion probabilities and tournament simulation outputs have not been established.

## Common data contract

All model experiments should use the same team lead preprocessing contract.

Expected generated local inputs:

| File | Role | Git policy |
| --- | --- | --- |
| `X_train.csv` | Training feature matrix using the 52-feature contract. | Generated artifact; do not commit by default. |
| `X_test.csv` | Test feature matrix using the 52-feature contract. | Generated artifact; do not commit by default. |
| `y_train.csv` | Training labels. | Generated artifact; do not commit by default. |
| `y_test.csv` | Test labels. | Generated artifact; do not commit by default. |
| `w_train.csv` | Training sample weights. | Generated artifact; do not commit by default. |

Model input must follow:

- Feature schema: `data/schema/team_lead_features.json`
- Feature count: 52
- Label encoding: `A=0`, `D=1`, `H=2`
- Train/test split: `2022-01-01`
- Leakage policy: score, result, target, and match-identity metadata columns must not be included in model input matrices.

## Models to compare

The team should compare models learned in class and practical tabular-data candidates.

| Model | Role in experiment | Why include it | Notes |
| --- | --- | --- | --- |
| Logistic Regression | Baseline model | Simple, explainable, probability output is easy to inspect. | Good first reference point. |
| Decision Tree | Classroom comparison model | Easy to explain and visualize. | May overfit; use mainly for learning and comparison. |
| RandomForest | Nonlinear comparison model | Captures nonlinear patterns and feature interactions. | Probability quality must be checked. |
| SVM | Classroom comparison model | Useful margin-based classifier. | Probability output may require calibration. |
| KNN | Classroom comparison model | Intuitive distance-based baseline. | May be sensitive to scaling and high-dimensional features. |
| Naive Bayes | Lightweight comparison model | Very fast baseline. | Strong independence assumptions may limit performance. |
| XGBoost | Main candidate | Strong for structured tabular data. | Tune carefully and evaluate probability quality. |
| LightGBM | Main candidate | Strong for structured tabular data and efficient training. | Tune carefully and evaluate probability quality. |
| Soft Voting Ensemble | Ensemble candidate | Combines predicted probabilities from multiple models. | Use only after individual model probabilities are available. |

## Recommended experiment order

1. Confirm that local generated input files match the 52-feature schema.
2. Train Logistic Regression as the baseline.
3. Train Decision Tree and RandomForest for tree-based comparison.
4. Train SVM, KNN, and Naive Bayes if time allows.
5. Train XGBoost and/or LightGBM as main candidates.
6. Compare all models with the same metrics.
7. If at least two models produce useful probabilities, test Soft Voting.
8. Consider calibration if Log Loss or Brier Score suggests poor probability quality.
9. Select a final candidate only after results are recorded.

## Evaluation metrics

Use the same metrics for every model.

| Metric | Why it matters |
| --- | --- |
| Accuracy | Overall percentage of correct predictions. Useful but not enough alone. |
| Macro F1 | Checks whether all classes are handled more evenly, including draw. |
| Log Loss | Measures probability quality. Important for simulation input. |
| Brier Score | Measures squared probability error. Important for probability reliability. |
| Confusion Matrix | Shows which classes are confused. |
| Draw Recall | Checks whether the model can identify draw outcomes instead of ignoring them. |

Important: tournament simulation depends on probability quality, not only top-class accuracy. A model with slightly lower accuracy but better Log Loss and Brier Score may be more useful for simulation.

## Result table template

| Model | Accuracy | Macro F1 | Log Loss | Brier Score | Draw Recall | Uses sample_weight? | Calibration used? | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| Logistic Regression | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Baseline. |
| Decision Tree | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Classroom comparison. |
| RandomForest | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Nonlinear comparison. |
| SVM | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Probability may need calibration. |
| KNN | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Scaling-sensitive. |
| Naive Bayes | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Lightweight baseline. |
| XGBoost | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Main candidate. |
| LightGBM | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Main candidate. |
| Soft Voting Ensemble | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Ensemble candidate. |

## Individual model report template

Each team member should report:

1. Model name.
2. Main purpose of the model in this comparison.
3. Input data files used.
4. Major hyperparameters.
5. Whether `w_train.csv` sample weights were used.
6. Metrics: Accuracy, Macro F1, Log Loss, Brier Score, Draw Recall.
7. Confusion matrix.
8. Strengths observed.
9. Weaknesses observed.
10. Whether the model is suitable as a final candidate.
11. Whether calibration or ensemble use is recommended.

## Suggested role split

This is a suggested split only. The team may adjust depending on members and time.

| Track | Model group | Output |
| --- | --- | --- |
| Baseline track | Logistic Regression, Naive Bayes | Simple baseline results. |
| Tree track | Decision Tree, RandomForest | Nonlinear baseline and feature-importance discussion. |
| Boosting track | XGBoost, LightGBM | Main candidate results. |
| Distance/margin track | SVM, KNN | Classroom model comparison. |
| Ensemble/evaluation track | Soft Voting, metric summary | Final comparison table and probability-quality discussion. |

## Decision rule for final model selection

Do not select the final model by Accuracy alone.

A final candidate should satisfy:

- It uses the 52-feature contract correctly.
- It avoids score/result/metadata leakage.
- It has competitive Accuracy and Macro F1.
- It does not completely ignore draw outcomes.
- It has acceptable Log Loss and Brier Score.
- Its probability output is stable enough for later group-stage and tournament simulation.
- Its result can be reproduced with documented data snapshot and command history.

## Ensemble policy

Soft Voting is allowed as a candidate only after individual models are evaluated.

Recommended first ensemble:

- Logistic Regression as a stable baseline probability model.
- RandomForest as a nonlinear comparison model.
- LightGBM or XGBoost as a main tabular-data candidate.

Do not use Stacking or situation-specific model routing as the first implementation unless the team has enough time to prevent data leakage and explain the validation process.

## Not yet decided

The following items are not finalized:

- Final model.
- Final hyperparameters.
- Whether LightGBM or XGBoost outperforms other models on this dataset.
- Whether Soft Voting improves probability quality.
- Whether calibration is required.
- Final model metrics.
- Final group-stage or tournament-simulation outputs.
- Champion probabilities.

## Presentation-safe wording

> The team will compare classroom-learned models and strong tabular-data candidates under the same 52-feature preprocessing contract. LightGBM and XGBoost are treated as main candidates, but the final model will be selected only after comparing Accuracy, Macro F1, Log Loss, Brier Score, Confusion Matrix, and Draw Recall.

## Unsafe wording

Avoid these claims until evaluation is complete:

- LightGBM is the final model.
- XGBoost is the final model.
- The ensemble is proven to be best.
- The model performance is final.
- Champion probabilities are final.
- The tournament simulation is complete.
