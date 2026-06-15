# Classroom Model Learning Guide

## Purpose

This guide connects the uploaded Google Colab classroom exercises to the Team 1 World Cup match-prediction model evaluation plan.

It is intended for learning and team coordination. It does not claim final model performance, final champion probabilities, or completed tournament simulation results.

Related project document:

- `docs/model_evaluation_plan.md`

## Source classroom files reviewed

| Uploaded file | Classroom topic summary | Project connection |
| --- | --- | --- |
| `0612(1).ipynb` | SVM classification, decision function, hyperplane intuition, `StandardScaler`, Logistic Regression calibration-style comparison, PCA/KNN-related practice, classification metrics. | Helps explain margin-based classification, scaling, probability quality, and evaluation outputs. |
| `260612_SVM_송광일.ipynb` | SVM-focused copy/practice notebook with similar content to `0612(1).ipynb`: SVC kernels, linear SVM, scaling, decision scores, Logistic Regression comparison. | Useful as the user's SVM learning basis for team model comparison. |
| `20260615_text_mining_pynb.ipynb` | Text mining, `CountVectorizer`, TF-IDF, document-term matrix, Naive Bayes for text classification, Gensim TF-IDF examples. | Useful for understanding vectorization and Naive Bayes, even though the current football model uses tabular features rather than text as primary input. |
| `20260615_개인과제_송광일(1).ipynb` | Web request/parsing, Korean noun extraction with `Okt`, word-counting, word cloud visualization. | Useful for explaining preprocessing, feature extraction, and presentation visualization concepts. Not primary model input for current 52-feature contract. |
| `붙여넣은 텍스트 (1)(17).txt` | KMeans distance-based outlier detection where distance greater than 2 is flagged and visualized. | Useful as a learning reference for outlier detection, but not yet part of the official team lead 52-feature pipeline. |

## Project modeling context

The current Team 1 project should evaluate classroom-learned models under the same team lead preprocessing contract.

Common contract:

- Input features: 52-feature schema from `data/schema/team_lead_features.json`.
- Label encoding: `A=0`, `D=1`, `H=2`.
- Train/test split: `2022-01-01`.
- Generated local inputs such as `X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`, and `w_train.csv` should not be committed by default.
- Final model selection should be based on recorded metrics, not assumption.

## Classroom concept to project mapping

| Classroom concept | What it means in class | Project application point | Caution |
| --- | --- | --- | --- |
| Logistic Regression | Linear baseline classifier that can output class probabilities. | Use as the first baseline for `A/D/H` multiclass prediction. | May underfit nonlinear football patterns. Do not treat as final without comparison. |
| SVM / SVC | Margin-based classifier using hyperplanes and kernels. | Use as a classroom comparison model. It can test whether margin-based decision boundaries help. | Scaling is important. Probability output may require `probability=True` or calibration, which can slow training. |
| StandardScaler | Rescales features to comparable ranges. | Important for SVM and KNN; optional/less critical for tree models. | Fit scaler only on train data. Do not leak test statistics into training. |
| Pipeline | Chains preprocessing and model steps safely. | Useful for SVM/KNN/Logistic Regression experiments to avoid train/test leakage. | The pipeline must be fitted only on training data. |
| KNN | Distance-based classifier. | Useful as a classroom baseline and intuition model. | Sensitive to scaling and high-dimensional feature spaces. May not be the strongest final candidate. |
| PCA | Reduces dimensions for visualization or compact representation. | Useful for visualizing model separation or checking feature patterns. | Do not use PCA in final model unless evaluation proves it helps. Fit only on train data. |
| Confusion Matrix | Shows which classes are confused. | Required for checking whether the model confuses home win, draw, and away win. | Accuracy alone can hide poor draw prediction. |
| F1 Score / Macro F1 | Measures balance across classes. | Use Macro F1 to avoid ignoring the draw class. | Report with Accuracy, Log Loss, and Brier Score. |
| Log Loss | Penalizes poor probability estimates. | Important because simulation needs reliable match probabilities. | Requires predicted probabilities for all classes. |
| Brier Score | Measures probability error. | Helps judge whether probabilities are stable enough for simulation. | For multiclass use, define and document calculation consistently. |
| KMeans outlier detection | Finds points far from cluster centers. | Learning reference for anomaly/outlier thinking in preprocessing. | Do not remove football matches automatically unless there is a documented rule. |
| CountVectorizer / TF-IDF | Converts text into numeric vectors. | Helps understand feature extraction and Naive Bayes. | Not part of current primary 52-feature match model unless a text feature scope is explicitly added. |
| Naive Bayes | Simple probabilistic classifier often used in text classification. | Include as a lightweight classroom comparison model if data format permits. | Its assumptions may be weak for engineered football tabular features. |
| Word cloud / Korean noun extraction | Text preprocessing and visualization. | Useful for presentation or reference-material exploration. | Not a substitute for model evaluation evidence. |

## Recommended learning path for team members

1. Start with the model evaluation plan.
2. Confirm the shared 52-feature contract and label encoding.
3. Run Logistic Regression as the simplest baseline.
4. Run SVM and KNN only inside proper scaling pipelines.
5. Run tree models and boosting models separately.
6. Compare all models with the same metrics.
7. Discuss Soft Voting only after individual model probabilities are available.
8. Do not claim final performance until results are recorded.

## Suggested individual model report template

Each team member should submit:

1. Model name.
2. Classroom concept learned.
3. Project dataset used.
4. Preprocessing steps.
5. Whether `StandardScaler` or `Pipeline` was used.
6. Whether `w_train.csv` sample weights were used.
7. Accuracy.
8. Macro F1.
9. Log Loss.
10. Brier Score.
11. Confusion Matrix.
12. Draw Recall.
13. What the model did well.
14. What the model did poorly.
15. Whether it should remain a final candidate.

## Recommended model-specific notes

### Logistic Regression

Use this as the baseline. It is simple and useful for checking whether the engineered features already contain meaningful predictive signal.

### SVM

Use this as a classroom comparison model. Because the class notebooks emphasize the SVM hyperplane, decision function, and scaling, SVM is valuable for learning. For the project, use it carefully because probability output and multiclass handling are more complex than tree-based models.

### KNN

Use this to understand distance-based prediction. Because the project has 52 features, KNN may be sensitive to scaling and feature noise. It is a comparison model, not the first final-model candidate.

### Decision Tree and RandomForest

Use these to compare nonlinear models and inspect feature-importance style explanations. RandomForest is a reasonable bridge between classroom learning and stronger boosting models.

### XGBoost and LightGBM

Treat these as main tabular-data candidates. They are likely strong candidates, but the team must still prove performance with the shared metric table.

### Soft Voting Ensemble

Use this only after individual model probabilities are available. Soft Voting can combine Logistic Regression, RandomForest, and LightGBM/XGBoost probabilities to reduce dependence on one model.

## What this guide does not decide

This guide does not decide:

- Final model.
- Final hyperparameters.
- Whether LightGBM or XGBoost is better on the team dataset.
- Whether Soft Voting improves performance.
- Whether SVM, KNN, or Naive Bayes should remain in the final candidate set.
- Final model metrics.
- Final 2026 group-stage predictions.
- Final champion probabilities.

## Presentation-safe wording

> We connected the classroom model exercises to the Team 1 model evaluation plan. Logistic Regression, SVM, KNN, Naive Bayes, tree-based models, boosting models, and Soft Voting will be compared under the same 52-feature preprocessing contract. The final model will be selected only after evaluating Accuracy, Macro F1, Log Loss, Brier Score, Confusion Matrix, and Draw Recall.

## Unsafe wording

Avoid these claims until evaluation is complete:

- The classroom notebooks prove which model is best.
- SVM is the final model.
- LightGBM or XGBoost is already proven best.
- Soft Voting is already proven best.
- KMeans outlier logic is part of the official preprocessing pipeline.
- Text mining is part of the current primary football prediction model.
- Champion probabilities are ready.
