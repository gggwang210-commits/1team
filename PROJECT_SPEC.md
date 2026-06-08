# PROJECT_SPEC

## Project

2026 FIFA World Cup Prediction Model

## Final MVP Decision

The revised MVP is a tournament prediction and simulation system for the 2026 FIFA World Cup, with Korea Republic analysis as the main demo storyline.

The project will estimate match-level Win/Draw/Loss probabilities, simulate the group stage and knockout stage, and summarize tournament-level probabilities such as Korea Republic advancement probability and champion probability.

## Core Prediction Tasks

### 1. Match Win/Draw/Loss Prediction

For each match, the model outputs calibrated probabilities for:

- Win Probability
- Draw Probability
- Loss Probability

The match model is the foundation for every downstream simulation.

### 2. Group Stage Simulation

The group stage simulator will use match-level probabilities to run repeated Monte Carlo simulations.

Expected outputs:

- Group table distribution by team
- Expected points
- Probability of finishing 1st, 2nd, 3rd, or 4th
- Probability of reaching the Round of 32
- Korea Republic group-stage advancement probability

The 2026 format assumption is 48 teams, 12 groups of four, with the top two teams in each group and the eight best third-place teams advancing to the Round of 32.

### 3. Knockout Stage Simulation

The knockout simulator will estimate single-elimination outcomes from the Round of 32 through the Final.

Expected outputs:

- Probability of reaching each knockout round
- Final appearance probability
- Champion probability estimation
- Korea Republic round-by-round advancement probability

Draw is not a terminal knockout outcome. If a simulated knockout match is level after regular time, the simulator should convert the match model output into a win probability for each team using an overtime/penalty proxy or normalized non-draw probability.

### 4. Korea Republic Advancement Probability

Korea Republic is the primary dashboard focus.

Required Korea Republic outputs:

- Match-level Win/Draw/Loss probability for each group match
- Group-stage expected points
- Round of 32 qualification probability
- Round of 16, quarter-final, semi-final, final, and champion probabilities when bracket simulation is available
- Key factors affecting Korea Republic outcomes

### 5. Champion Probability Estimation

The system will estimate each team's probability of winning the tournament using repeated full-tournament simulations.

Champion probability should be reported with:

- Number of simulations
- Model version
- Dataset version/date
- Key assumptions and limitations

### 6. Upset Analysis

Upset analysis will identify matches where the lower-rated or lower-probability team has a meaningful chance to win or advance.

Possible upset definitions:

- FIFA ranking gap based upset
- Elo/rating gap based upset if ratings are available
- Model probability upset where the underdog win probability exceeds a selected threshold

Expected outputs:

- Top potential group-stage upsets
- Top potential knockout-stage upsets
- Korea Republic upset opportunities and upset risks

### 7. SHAP Feature Importance Analysis

The explainability layer will use SHAP feature importance analysis where the selected model supports it.

Expected outputs:

- Global feature importance summary
- Match-level explanation for selected Korea Republic matches
- Interpretation notes for high-impact features such as ranking difference, recent form, venue/neutral flag, confederation, goal difference trends, and tournament history

SHAP results must be presented as interpretation support, not as causal proof.

## Data Sources

Initial candidate sources:

- International Football Results dataset
- FIFA Rankings
- FIFA World Cup historical match data
- Optional: Elo ratings, squad market value, injuries, recent form, confederation/tournament metadata

Data source availability, licensing, freshness, and join keys must be checked before final modeling.

## Feature Candidates

- Team strength difference
- FIFA ranking difference
- Recent match form
- Goals for/against trend
- Home/away/neutral venue indicator
- Confederation
- World Cup participation/history indicators
- Head-to-head summary, only if leakage-safe
- Rest days or travel burden, if reliable schedule data is available

## Baseline Models

Baseline candidates:

- Multinomial Logistic Regression
- Random Forest
- Gradient Boosting / XGBoost or LightGBM, if dependency and time constraints allow

The MVP should prefer a simple, explainable, reproducible baseline before adding more complex models.

## Evaluation

### Match-Level Metrics

- Accuracy
- Macro F1
- Log Loss
- Brier Score
- Calibration curve or reliability notes

### Simulation-Level Metrics

- Backtesting on previous World Cups where feasible
- Group qualification prediction sanity check
- Champion probability distribution sanity check
- Sensitivity analysis for simulation count and key assumptions

## Revised MVP Deliverables

Required MVP deliverables:

1. Data quality report
2. Feature table v1
3. Match Win/Draw/Loss baseline model
4. Model evaluation report with calibration notes
5. Group stage simulation module
6. Knockout stage simulation module
7. Korea Republic advancement probability report
8. Champion probability estimation table
9. Upset analysis report
10. SHAP feature importance report or notebook
11. Streamlit demo showing Korea Republic-focused predictions and tournament simulation summary
12. Final presentation/report explaining assumptions, risks, results, and next steps

## Success Metrics

The MVP will be considered successful if it meets the following criteria:

- Produces valid Win/Draw/Loss probabilities for target matches
- Produces reproducible group-stage simulation results with a fixed random seed
- Produces reproducible knockout-stage and champion probability estimates
- Reports Korea Republic Round of 32 qualification probability clearly
- Shows champion probability estimates for all modeled teams
- Includes at least one upset analysis table
- Includes at least one SHAP-based feature importance output or clearly documented fallback explanation method
- Provides evaluation metrics: Accuracy, Log Loss, Brier Score, and calibration notes
- Runs end-to-end with documented commands
- Presents limitations transparently enough for a class/team project review

## Risks and Limitations

- Data freshness risk: FIFA rankings, squads, injuries, and final fixtures may change before the tournament.
- Data leakage risk: features must not use information unavailable before the predicted match.
- Small sample risk: World Cup matches are limited, so model estimates can be noisy.
- Calibration risk: high Accuracy does not guarantee reliable probabilities.
- Format complexity risk: third-place qualification and knockout bracket mapping can introduce simulation errors.
- Knockout draw handling risk: regular-time draw probabilities must be converted carefully for extra time/penalty outcomes.
- Interpretability risk: SHAP explains model behavior but does not prove causal impact.
- External factor risk: injuries, tactical changes, weather, travel, and squad rotation may not be captured.
- Overconfidence risk: champion probabilities should be communicated as estimates, not certainties.
- Scope risk: full tournament simulation can delay MVP completion if data cleaning and match model quality are not stabilized first.

## Implementation Priority

Always prioritize MVP completion in this order:

Data Quality
→ Feature Engineering
→ Match Win/Draw/Loss Modeling
→ Evaluation and Calibration
→ Group Stage Simulation
→ Knockout Stage Simulation
→ Korea Republic Probability Report
→ Champion Probability Estimation
→ Upset Analysis
→ SHAP Feature Importance
→ Streamlit Demo
→ Final Presentation
