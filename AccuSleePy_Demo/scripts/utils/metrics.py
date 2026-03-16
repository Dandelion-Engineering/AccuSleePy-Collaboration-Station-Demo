"""Shared metric computation utilities for the AccuSleePy Demo pipeline.

Computes validation metrics (Cohen's kappa, per-class F1, overall accuracy,
confusion matrix) used in Phase 4 quality control and validation scripts.

All functions accept numpy arrays and return plain Python scalars or dicts
so results can be written to CSV without additional processing.

Label encoding (as confirmed in data_guide.md and Project Details.md):
    REM  = 1
    Wake = 2
    NREM = 3
"""

import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BRAIN_STATES = {1: "REM", 2: "Wake", 3: "NREM"}
LABEL_ORDER = [1, 2, 3]          # REM, Wake, NREM — used for confusion matrix rows/cols
LABEL_NAMES = ["REM", "Wake", "NREM"]


# ---------------------------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------------------------

def confusion_matrix(true_labels: np.ndarray, pred_labels: np.ndarray) -> np.ndarray:
    """Compute a 3x3 confusion matrix for the three sleep stages.

    Rows correspond to true labels; columns correspond to predicted labels.
    Order: [REM (1), Wake (2), NREM (3)].

    :param true_labels: 1-D integer array of expert labels {1, 2, 3}
    :param pred_labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: 3x3 numpy integer array; cm[i][j] = count of true class i predicted as class j
    :raises ValueError: if arrays have different lengths or contain unexpected label values
    """
    if len(true_labels) != len(pred_labels):
        raise ValueError(
            f"true_labels length ({len(true_labels)}) != pred_labels length ({len(pred_labels)})"
        )
    unexpected_true = set(np.unique(true_labels)) - {1, 2, 3}
    unexpected_pred = set(np.unique(pred_labels)) - {1, 2, 3}
    if unexpected_true:
        raise ValueError(f"Unexpected values in true_labels: {unexpected_true}")
    if unexpected_pred:
        raise ValueError(f"Unexpected values in pred_labels: {unexpected_pred}")

    cm = np.zeros((3, 3), dtype=np.int64)
    label_to_idx = {1: 0, 2: 1, 3: 2}
    for t, p in zip(true_labels, pred_labels):
        cm[label_to_idx[t], label_to_idx[p]] += 1
    return cm


# ---------------------------------------------------------------------------
# Cohen's kappa
# ---------------------------------------------------------------------------

def cohens_kappa(true_labels: np.ndarray, pred_labels: np.ndarray) -> float:
    """Compute Cohen's kappa between true and predicted sleep-stage labels.

    Kappa accounts for chance agreement. Range: (-1, 1]; 1 = perfect agreement,
    0 = no better than chance.

    :param true_labels: 1-D integer array of expert labels {1, 2, 3}
    :param pred_labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: Cohen's kappa as a float
    """
    cm = confusion_matrix(true_labels, pred_labels)
    n = cm.sum()
    if n == 0:
        return 0.0

    observed_agreement = np.diag(cm).sum() / n
    row_marginals = cm.sum(axis=1) / n   # true class proportions
    col_marginals = cm.sum(axis=0) / n   # predicted class proportions
    expected_agreement = np.dot(row_marginals, col_marginals)

    if expected_agreement == 1.0:
        return 1.0
    return (observed_agreement - expected_agreement) / (1.0 - expected_agreement)


# ---------------------------------------------------------------------------
# Overall accuracy
# ---------------------------------------------------------------------------

def overall_accuracy(true_labels: np.ndarray, pred_labels: np.ndarray) -> float:
    """Compute overall classification accuracy.

    :param true_labels: 1-D integer array of expert labels {1, 2, 3}
    :param pred_labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: accuracy as a float in [0, 1]
    """
    if len(true_labels) != len(pred_labels):
        raise ValueError(
            f"true_labels length ({len(true_labels)}) != pred_labels length ({len(pred_labels)})"
        )
    if len(true_labels) == 0:
        return 0.0
    return float(np.sum(true_labels == pred_labels) / len(true_labels))


# ---------------------------------------------------------------------------
# Per-class precision, recall, F1
# ---------------------------------------------------------------------------

def per_class_metrics(
    true_labels: np.ndarray, pred_labels: np.ndarray
) -> dict[str, dict[str, float]]:
    """Compute per-class precision, recall, and F1 for each sleep stage.

    :param true_labels: 1-D integer array of expert labels {1, 2, 3}
    :param pred_labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: dict mapping stage name (e.g. "REM") to a sub-dict with keys
        ``precision``, ``recall``, ``f1``, each as float in [0, 1].
        Returns 0.0 for undefined precision or recall (i.e., zero denominator).
    """
    cm = confusion_matrix(true_labels, pred_labels)
    label_to_idx = {1: 0, 2: 1, 3: 2}
    result = {}
    for label_val, label_name in BRAIN_STATES.items():
        idx = label_to_idx[label_val]
        tp = cm[idx, idx]
        fp = cm[:, idx].sum() - tp   # predicted as this class, but not this class
        fn = cm[idx, :].sum() - tp   # this class, but predicted as something else

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall    = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1        = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        result[label_name] = {"precision": precision, "recall": recall, "f1": f1}
    return result


# ---------------------------------------------------------------------------
# All metrics in one call
# ---------------------------------------------------------------------------

def compute_all_metrics(
    true_labels: np.ndarray, pred_labels: np.ndarray
) -> dict:
    """Compute all validation metrics in a single call.

    Returns a flat dict suitable for writing as a row in a CSV file.

    :param true_labels: 1-D integer array of expert labels {1, 2, 3}
    :param pred_labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: dict with keys:
        - ``kappa``              (float)
        - ``accuracy``           (float)
        - ``n_epochs``           (int)
        - ``REM_precision``      (float)
        - ``REM_recall``         (float)
        - ``REM_f1``             (float)
        - ``Wake_precision``     (float)
        - ``Wake_recall``        (float)
        - ``Wake_f1``            (float)
        - ``NREM_precision``     (float)
        - ``NREM_recall``        (float)
        - ``NREM_f1``            (float)
    """
    kappa = cohens_kappa(true_labels, pred_labels)
    acc   = overall_accuracy(true_labels, pred_labels)
    pcm   = per_class_metrics(true_labels, pred_labels)

    flat = {
        "kappa":    kappa,
        "accuracy": acc,
        "n_epochs": len(true_labels),
    }
    for stage in ["REM", "Wake", "NREM"]:
        for metric in ["precision", "recall", "f1"]:
            flat[f"{stage}_{metric}"] = pcm[stage][metric]
    return flat
