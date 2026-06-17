# Final Presentation Runbook: 2026 FIFA World Cup Prediction Model

## Purpose

This runbook defines what the team can safely present, what must be verified before the final presentation, and what should be described as follow-up work.

The project has moved from a Korea-only MVP framing to a global match-level prediction framing. Korea Republic remains useful as a filtered demonstration and legacy smoke-test path, but it should not be described as the primary modeling scope.

## Safe presentation claim

Use this wording:

> Our project builds a machine-learning pipeline that estimates Win/Draw/Loss probabilities for international football matches using historical match data and pre-match features. The current main scope is global match-level probability prediction. Korea Republic is presented as an interpretable application case, while group-stage simulation, knockout simulation, and champion probability are treated as extension work that requires additional rule validation.

## Do not claim

Do not say the following unless the related verification evidence is added:

- The project fully predicts the 2026 FIFA World Cup winner.
- Champion probability is a completed final output.
- `src/run_model_comparison.py` performs full end-to-end retraining.
- The current model guarantees real 2026 World Cup outcomes.
- Drive-reviewed reference metrics are the same thing as a freshly reproduced local training result.

## Evidence hierarchy

Use this order when deciding what can be shown in slides:

1. Reproduced local outputs generated from the repository commands.
2. GitHub-tracked reports and generated CSV files.
3. Drive-reviewed reference results, clearly labeled as reviewed reference metrics.
4. Future-work design notes.

If an item only exists as a design note, present it as planned extension work, not as completed implementation.

## Required verification commands

Run from the project root.

### Korea smoke-test path

```bash
python src/data/build_dataset.py
python src/features/make_features.py
python src/models/train_baseline.py
python src/models/predict.py
python src/models/evaluate.py
streamlit run app/streamlit_app.py
```

Expected local artifacts:

```text
data/processed/matches.csv
data/processed/features.csv
models/baseline_model.pkl
reports/data_quality_summary.md
reports/baseline_metrics.csv
reports/prediction_table.csv
reports/model_evaluation.md
```

### Global match-level path

```bash
python src/data/build_dataset.py --global-scope
python src/features/make_features.py --target-scope home
```

Expected local artifacts:

```text
data/processed/matches_global.csv
data/processed/features_global.csv
```

If global training uses separate output paths, record the exact command and generated files in the final presentation notes.

### Reference model-comparison output

```bash
python src/run_model_comparison.py --config configs/model_comparison.yaml
```

Expected local artifacts:

```text
outputs/model_comparison_metrics.csv
outputs/model_comparison_metrics.json
```

Important: this command currently preserves Drive-reviewed reference metrics. It is not a full model retraining pipeline.

## Slide structure recommendation

### Slide 1. Project title

Title: 2026 FIFA World Cup Match Outcome Probability Prediction

Positioning: global match-level Win/Draw/Loss probability prediction with Korea Republic as an application example.

### Slide 2. Problem definition

Explain that predicting football match outcomes is difficult because international football has class imbalance, draw outcomes, changing team strength, and tournament-specific context.

### Slide 3. Data and target definition

Show:

- Historical international match records
- Pre-match features such as rank/Elo difference and neutral venue flag
- Target: Win/Draw/Loss from the selected perspective
- Korea path: Korea Republic perspective labels
- Global path: home-team perspective labels

### Slide 4. Pipeline architecture

Show this flow:

```text
raw match data
-> standardized match table
-> feature generation
-> baseline/model comparison
-> probability output
-> prediction table
-> Streamlit demo
```

### Slide 5. Leakage control

Explain that score/result/target/date columns are excluded from model inputs and that final scores are only used to create labels.

### Slide 6. Model results

Show reproduced local metrics if available. If using the Drive-reviewed table, label it as reference metrics.

Suggested wording:

> The current reference table identifies Soft Voting as the main probability-model candidate, but the final presentation should separate reference metrics from locally reproduced training outputs.

### Slide 7. Demo output

Show:

- `reports/prediction_table.csv`
- `reports/model_evaluation.md`
- Streamlit screen capture

### Slide 8. Expansion plan

Separate completed MVP from future work:

Completed or near-completed:

- Match-level W/D/L probability pipeline
- Korea application view
- Baseline evaluation report
- Streamlit display layer

Future work:

- Probability calibration improvement
- Group-stage simulation
- Round-of-32 allocation using official rule mapping
- Knockout simulation
- Champion probability

### Slide 9. Limitations

Mention:

- Data quality and source coverage
- Draw prediction difficulty
- FIFA rule verification requirements
- Tournament simulation dependency on Annexe C and knockout probability policy
- Educational project, not betting or official prediction guidance

## Final Q&A-safe answers

### Q. Is this predicting the real 2026 World Cup winner?

No. The current verified scope is match-level Win/Draw/Loss probability prediction. Champion probability is an extension that requires complete tournament rule implementation and further validation.

### Q. Why use probability instead of one fixed prediction?

Football outcomes are uncertain. Probability outputs allow the model to express uncertainty across Win, Draw, and Loss instead of forcing a single deterministic answer.

### Q. Why is draw prediction difficult?

Draws are usually less frequent and more context-dependent than wins or losses. This makes draw classification sensitive to data balance, feature quality, and calibration.

### Q. What is Korea Republic's role now?

Korea Republic is an application case and smoke-test path. The main direction is global match-level prediction.

### Q. Are the current model-comparison metrics fully reproduced from code?

Only claim that if the team has rerun the full training workflow and saved the outputs. Otherwise, describe them as Drive-reviewed reference metrics preserved in the repository.

## Completion checklist

Before final slides are frozen:

- [ ] Issue #61 execution checklist completed or unresolved items documented.
- [ ] Issue #62 scope separation reflected in slides.
- [ ] `docs/PRESENTATION_STORYLINE.md` either updated for FIFA or excluded from final slide references.
- [ ] Streamlit screen capture prepared.
- [ ] Local generated report files checked.
- [ ] Any missing data files or demo fallback behavior disclosed.
- [ ] Champion probability described only as future work unless fully verified.
