"""Generate the reference model comparison table.

This runner currently preserves the verified comparison metrics used for presentation evidence.
Connect the real training pipeline before claiming full end-to-end retraining.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REFERENCE_ROWS = [
    {"model": "Soft Voting", "accuracy": 0.6465, "macro_f1": 0.5273, "log_loss": 0.8000, "brier_score": 0.4668, "role": "main_candidate"},
    {"model": "Logistic Full", "accuracy": 0.6450, "macro_f1": 0.5148, "log_loss": 0.8058, "brier_score": 0.4683, "role": "linear_baseline"},
    {"model": "XGBoost", "accuracy": 0.6452, "macro_f1": 0.5286, "log_loss": 0.8073, "brier_score": 0.4698, "role": "nonlinear_candidate"},
    {"model": "Random Forest", "accuracy": 0.6147, "macro_f1": 0.5660, "log_loss": 0.8415, "brier_score": 0.4931, "role": "draw_reference"},
    {"model": "Poisson", "accuracy": 0.6332, "macro_f1": 0.4674, "log_loss": 0.8161, "brier_score": 0.4751, "role": "score_explanation"},
]


FIELDNAMES = ["model", "accuracy", "macro_f1", "log_loss", "brier_score", "role"]


def write_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(REFERENCE_ROWS)


def write_json(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(REFERENCE_ROWS, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/model_comparison.yaml")
    parser.add_argument("--metrics-csv", default="outputs/model_comparison_metrics.csv")
    parser.add_argument("--metrics-json", default="outputs/model_comparison_metrics.json")
    args = parser.parse_args()

    # The config path is accepted to keep the final reproducibility command stable.
    # Training integration should later load and validate this config.
    _ = args.config

    write_csv(Path(args.metrics_csv))
    write_json(Path(args.metrics_json))
    print(f"Wrote {args.metrics_csv}")
    print(f"Wrote {args.metrics_json}")


if __name__ == "__main__":
    main()
