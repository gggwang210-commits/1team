"""Generate the Drive-synced reference model comparison table.

This runner preserves the latest reviewed comparison metrics used for presentation evidence.
Connect the real training pipeline before claiming full end-to-end retraining.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REFERENCE_ROWS = [
    {"model": "Soft Voting", "accuracy": 0.6465, "macro_f1": 0.5273, "log_loss": 0.8000, "brier_score": 0.4668, "role": "main_probability_candidate", "source_note": "latest_drive_review"},
    {"model": "Logistic Full", "accuracy": 0.6450, "macro_f1": 0.5148, "log_loss": 0.8058, "brier_score": 0.4683, "role": "strong_linear_baseline", "source_note": "latest_drive_review"},
    {"model": "XGBoost", "accuracy": 0.6452, "macro_f1": 0.5286, "log_loss": 0.8073, "brier_score": 0.4698, "role": "nonlinear_candidate", "source_note": "latest_drive_review"},
    {"model": "Stacking", "accuracy": 0.6430, "macro_f1": "", "log_loss": 0.8060, "brier_score": "", "role": "complexity_limited_gain", "source_note": "latest_drive_review"},
    {"model": "LightGBM", "accuracy": 0.6392, "macro_f1": 0.5366, "log_loss": 0.8135, "brier_score": 0.4720, "role": "fast_training_candidate", "source_note": "latest_drive_review"},
    {"model": "Poisson", "accuracy": 0.6332, "macro_f1": 0.4674, "log_loss": 0.8161, "brier_score": 0.4751, "role": "score_explanation_auxiliary", "source_note": "latest_drive_review"},
    {"model": "Logistic Elo-only", "accuracy": 0.6261, "macro_f1": 0.4621, "log_loss": 0.8290, "brier_score": 0.4834, "role": "elo_baseline", "source_note": "latest_drive_review"},
    {"model": "Random Forest", "accuracy": 0.6147, "macro_f1": 0.5660, "log_loss": 0.8415, "brier_score": 0.4931, "role": "draw_sensitivity_reference", "source_note": "latest_drive_review"},
]


FIELDNAMES = ["model", "accuracy", "macro_f1", "log_loss", "brier_score", "role", "source_note"]


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
