"""Metric helpers for Win/Draw/Loss model evaluation."""

from __future__ import annotations

from typing import Any

from sklearn.metrics import accuracy_score, f1_score, log_loss


def multiclass_brier_score(y_true: Any, y_prob: Any) -> float:
    """Return multiclass Brier score for one-hot-compatible probabilities.

    The caller should provide y_true labels and y_prob class probabilities
    in the same class order used by the model.
    """
    import numpy as np
    from sklearn.preprocessing import label_binarize

    classes = np.arange(y_prob.shape[1])
    y_true_bin = label_binarize(y_true, classes=classes)
    return float(np.mean(np.sum((y_prob - y_true_bin) ** 2, axis=1)))


def compute_classification_metrics(y_true: Any, y_pred: Any, y_prob: Any) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "log_loss": float(log_loss(y_true, y_prob)),
        "brier_score": multiclass_brier_score(y_true, y_prob),
    }
