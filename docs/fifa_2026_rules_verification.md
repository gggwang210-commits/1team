# FIFA 2026 Rules Verification

## Verification date

2026-06-15

## Primary source

- FIFA, `Regulations for the FIFA World Cup 26`, May 2026.
- Primary-source note: Article 12.6 covers the Round of 32 mapping and Annexe C reference. Article 13 covers group ranking and best third-placed teams ranking.

## Verification summary table

| Item | Status | Official basis | Project implication |
| --- | --- | --- | --- |
| Group-stage tiebreaker rules | Verified | Article 13 | Full group ranking must be aligned before final simulation claims. |
| Best third-placed teams ranking rule | Verified | Article 13 | Third-place ranking order is verified; ranking snapshot handling still needs reproducibility metadata. |
| Round of 32 bracket mapping | Verified | Article 12.6 | `data/tournament/bracket.json` should be aligned to official M73-M88 mapping in a follow-up PR. |
| Third-place qualifier combinations | Partially Verified | Article 12.6 and Annexe C | Annexe C is official, but all 495 combinations still need machine-readable conversion and tests. |

## FACT: Group-stage tiebreaker rules

FIFA Article 13 defines a multi-step ranking process for teams equal on points in the same group.

Verified criteria categories:

1. Head-to-head results among tied teams.
2. If needed, re-application among the remaining tied teams.
3. Overall group-stage goal difference and goals scored.
4. Team conduct score.
5. FIFA/Coca-Cola Men's World Ranking fallback, including earlier ranking editions if still tied.

Project implication: `src/simulation/ranking.py` must not be described as fully FIFA-compliant until this full sequence is implemented and tested.

## FACT: Best third-placed teams ranking rule

FIFA Article 13 defines the order for ranking the twelve third-placed teams and selecting the eight best-ranked third-placed teams.

Verified criteria categories:

1. Points from all group matches.
2. Goal difference from all group matches.
3. Goals scored in all group matches.
4. Team conduct score.
5. FIFA/Coca-Cola Men's World Ranking fallback, including earlier ranking editions if still tied.

Project implication: `src/simulation/third_place.py` is aligned with the main verified order, but reproducible FIFA ranking snapshot metadata is still needed before final simulation claims.

## FACT: Round of 32 bracket mapping

FIFA Article 12.6 defines the Round of 32 match structure as M73-M88.

Project implication: `data/tournament/bracket.json` should be updated in a follow-up PR to store the official M73-M88 slots and the relevant best-third-place candidate pools. This PR intentionally documents the rule first and does not change bracket data.

## PARTIALLY VERIFIED: Third-place qualifier combinations

FIFA Article 12.6 states that Annexe C includes 495 possible combinations for the eight best-ranked third-placed teams and their Round of 32 match-ups.

Important project boundary:

> Annexe C defines the official third-place qualifier combinations, but the project must not claim complete official tournament simulation support until the combinations are converted into a machine-readable file and covered by tests.

## INFERENCE: Current repository implementation status

- `data/tournament/bracket.json` still marks bracket rules as pending official verification and does not yet contain the official M73-M88 mapping.
- `src/simulation/ranking.py` is explicitly provisional and does not claim full FIFA regulation compliance.
- `src/simulation/third_place.py` follows the verified Article 13 order for best third-placed teams, with deterministic software fallback when ranking data is unavailable or still tied.
- Existing tests cover provisional group ranking and third-place ranking behavior, but not full Article 13 group tiebreakers or Annexe C combinations.

## UNKNOWN / TODO

- The project has not yet stored an official FIFA ranking snapshot for ranking fallback reproducibility.
- The project has not yet converted Annexe C 495 combinations into CSV or JSON.
- The project has not yet added complete tests for all Annexe C combinations.
- The project has not yet defined a final knockout draw-resolution policy for converting W/D/L probabilities into knockout winner probabilities.
- The project has not yet generated final reproducible tournament simulation outputs.

## Implementation boundary

The project may say:

- Official FIFA rules have been reviewed and documented.
- Group-stage tiebreaker rules, best third-placed team ranking rules, and Round of 32 structure have been verified from the official FIFA regulations.
- Annexe C is identified as the official basis for third-place qualifier combinations.

The project must not say:

- The tournament simulation is fully FIFA-compliant.
- The Round of 32 automation is complete.
- Annexe C has been fully implemented.
- Champion probabilities are final or official-rule-complete.

## Project TODO

1. Align `data/tournament/bracket.json` with Article 12.6 M73-M88 mapping.
2. Add tests for the official Round of 32 bracket mapping.
3. Implement full Article 13 group ranking, including head-to-head handling and FIFA ranking fallback.
4. Add Article 13 group ranking tests.
5. Convert Annexe C 495 third-place qualifier combinations into a machine-readable CSV or JSON file.
6. Add tests covering all Annexe C combinations.
7. Store FIFA ranking snapshot metadata before using ranking fallback in reproducible simulations.
8. Define knockout draw-resolution policy before generating champion probabilities.

## Safe presentation wording

> We reviewed the official FIFA Regulations for the FIFA World Cup 26 before tournament simulation. Group-stage tiebreakers, best third-placed team ranking rules, and the Round of 32 structure are now documented against the official regulations. Annexe C defines the official third-place qualifier combinations, but we will not claim complete tournament simulation support until those 495 combinations are converted into machine-readable data and covered by tests.

## Unsafe presentation wording

Avoid these claims until follow-up implementation and tests are complete:

- The tournament simulation fully implements all FIFA 2026 rules.
- The Round of 32 automation is complete.
- The Annexe C third-place combinations are fully implemented.
- Champion probabilities are final.
- Our simulation output is official-rule-complete.

## References

- FIFA, `Regulations for the FIFA World Cup 26`, May 2026.
- Article 12.6: Round of 32 mapping and Annexe C reference.
- Article 13: Equal points, group ranking, and best third-placed teams ranking.
- Annexe C: Combinations for eight best third-placed teams.
