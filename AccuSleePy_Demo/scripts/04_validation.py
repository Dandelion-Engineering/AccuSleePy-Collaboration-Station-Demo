"""Validation of AccuSleePy predictions against expert labels.

Compares Phase 3 predicted labels against the expert manual labels for each
recording, excluding the exact calibration epochs saved during scoring.

Outputs
-------
``outputs/validation_summary.csv`` with one row per recording including:
    - Cohen's kappa
    - overall accuracy
    - per-class precision / recall / F1
    - compared and excluded epoch counts
    - per-recording confusion-matrix counts

The script also prints aggregate mean +/- SD kappa and accuracy across all
recordings, plus aggregate per-class precision / recall / F1 from the summed
held-out confusion matrix.

Usage
-----
    python scripts/04_validation.py \\
        --data_dir C:\\Datasets\\AccuSleePy_Data \\
        --predicted_labels_dir AccuSleePy_Demo/outputs/predicted_labels \\
        --output_path AccuSleePy_Demo/outputs/validation_summary.csv
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow imports from within AccuSleePy_Demo/scripts/
_script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_script_dir))

from utils.data_loading import (
    find_all_recordings,
    load_calibration_indices,
    load_expert_labels,
    load_predicted_labels,
)
from utils.metrics import (
    BRAIN_STATES,
    compute_all_metrics,
    confusion_matrix,
    per_class_metrics,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGE_ORDER = [("Wake", 2), ("NREM", 3), ("REM", 1)]
EXPECTED_LABELS = set(BRAIN_STATES.keys())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    :return: parsed namespace with ``data_dir``, ``predicted_labels_dir``, and
        ``output_path`` attributes
    """
    parser = argparse.ArgumentParser(
        description=(
            "Validate AccuSleePy predictions against expert labels while "
            "excluding the calibration epochs used during scoring."
        )
    )
    parser.add_argument(
        "--data_dir",
        required=True,
        help="Root directory of the AccuSleePy dataset (must contain '4-hour_recordings/').",
    )
    parser.add_argument(
        "--predicted_labels_dir",
        default=os.path.join("AccuSleePy_Demo", "outputs", "predicted_labels"),
        help=(
            "Directory containing Phase 3 predicted-label CSVs and companion "
            "calibration-index CSVs. Default: "
            "AccuSleePy_Demo/outputs/predicted_labels"
        ),
    )
    parser.add_argument(
        "--output_path",
        default=os.path.join("AccuSleePy_Demo", "outputs", "validation_summary.csv"),
        help=(
            "CSV path where per-recording validation metrics will be written. "
            "Parent directories are created automatically. Default: "
            "AccuSleePy_Demo/outputs/validation_summary.csv"
        ),
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def build_holdout_mask(n_epochs: int, calibration_indices: np.ndarray) -> np.ndarray:
    """Return a boolean mask that excludes calibration epochs.

    :param n_epochs: total number of epochs in the recording
    :param calibration_indices: 1-D int array of calibration epoch indices
    :return: boolean mask of length ``n_epochs`` where held-out epochs are True
    :raises ValueError: if calibration indices are duplicated or out of range
    """
    if calibration_indices.ndim != 1:
        raise ValueError("Calibration indices must be a 1-D array.")

    unique_indices = np.unique(calibration_indices)
    if len(unique_indices) != len(calibration_indices):
        raise ValueError("Calibration indices contain duplicates.")
    if len(unique_indices) == 0:
        raise ValueError("Calibration indices file is empty.")
    if unique_indices.min() < 0 or unique_indices.max() >= n_epochs:
        raise ValueError(
            f"Calibration indices out of range for {n_epochs} epochs: "
            f"min={unique_indices.min()}, max={unique_indices.max()}"
        )

    holdout_mask = np.ones(n_epochs, dtype=bool)
    holdout_mask[unique_indices] = False
    return holdout_mask


def flatten_confusion_counts(cm: np.ndarray) -> dict[str, int]:
    """Flatten confusion-matrix counts into CSV-friendly columns.

    ``utils.metrics.confusion_matrix`` returns rows/columns in REM, Wake, NREM
    order. This helper emits explicitly named columns so later scripts can sum
    them without relying on implicit index order.

    :param cm: 3x3 confusion matrix with rows=true labels, cols=predicted labels
    :return: flat dict such as ``cm_true_wake_pred_rem: 7``
    """
    label_to_idx = {1: 0, 2: 1, 3: 2}
    flat = {}
    for true_name, true_value in STAGE_ORDER:
        for pred_name, pred_value in STAGE_ORDER:
            flat[
                f"cm_true_{true_name.lower()}_pred_{pred_name.lower()}"
            ] = int(cm[label_to_idx[true_value], label_to_idx[pred_value]])
    return flat


def format_stage_metrics(metrics_by_stage: dict[str, dict[str, float]]) -> dict[str, float]:
    """Convert per-class metrics into flat CSV columns using project stage order.

    :param metrics_by_stage: output from ``utils.metrics.per_class_metrics``
    :return: flat dict with keys like ``wake_precision`` and ``rem_f1``
    """
    flat = {}
    for stage_name, _ in STAGE_ORDER:
        stage_metrics = metrics_by_stage[stage_name]
        prefix = stage_name.lower()
        flat[f"{prefix}_precision"] = stage_metrics["precision"]
        flat[f"{prefix}_recall"] = stage_metrics["recall"]
        flat[f"{prefix}_f1"] = stage_metrics["f1"]
    return flat


def validate_recording(rec: dict, predicted_labels_dir: Path) -> tuple[dict, np.ndarray]:
    """Validate one recording and return its metric row plus confusion matrix.

    :param rec: recording descriptor from ``find_all_recordings``
    :param predicted_labels_dir: Phase 3 output directory
    :return: tuple of (flat CSV row dict, 3x3 held-out confusion matrix)
    """
    recording_id = rec["recording_id"]
    predicted_path = predicted_labels_dir / f"{recording_id}.csv"
    calibration_path = predicted_labels_dir / f"{recording_id}_calibration_indices.csv"

    if not predicted_path.is_file():
        raise FileNotFoundError(f"Predicted label file not found: {predicted_path}")
    if not calibration_path.is_file():
        raise FileNotFoundError(f"Calibration index file not found: {calibration_path}")

    expert_labels = load_expert_labels(rec["label_path"])
    predicted_labels, confidence_scores = load_predicted_labels(str(predicted_path))
    calibration_indices = load_calibration_indices(str(calibration_path))

    if len(predicted_labels) != len(expert_labels):
        raise ValueError(
            f"Predicted/expert length mismatch for {recording_id}: "
            f"{len(predicted_labels)} vs {len(expert_labels)}"
        )
    if len(confidence_scores) != len(predicted_labels):
        raise ValueError(
            f"Confidence-score length mismatch for {recording_id}: "
            f"{len(confidence_scores)} vs {len(predicted_labels)}"
        )

    unexpected_pred = set(np.unique(predicted_labels)) - EXPECTED_LABELS
    unexpected_true = set(np.unique(expert_labels)) - EXPECTED_LABELS
    if unexpected_pred:
        raise ValueError(f"Unexpected predicted labels for {recording_id}: {unexpected_pred}")
    if unexpected_true:
        raise ValueError(f"Unexpected expert labels for {recording_id}: {unexpected_true}")

    holdout_mask = build_holdout_mask(len(expert_labels), calibration_indices)
    expert_holdout = expert_labels[holdout_mask]
    predicted_holdout = predicted_labels[holdout_mask]

    if len(expert_holdout) != len(predicted_holdout):
        raise ValueError(
            f"Held-out length mismatch for {recording_id}: "
            f"{len(expert_holdout)} vs {len(predicted_holdout)}"
        )
    if len(expert_holdout) == 0:
        raise ValueError(f"No held-out epochs remain after exclusion for {recording_id}.")

    metrics = compute_all_metrics(expert_holdout, predicted_holdout)
    metrics_by_stage = per_class_metrics(expert_holdout, predicted_holdout)
    cm = confusion_matrix(expert_holdout, predicted_holdout)

    row = {
        "recording_id": recording_id,
        "mouse_id": rec["mouse_id"],
        "day_id": rec["day_id"],
        "total_epochs": len(expert_labels),
        "excluded_calibration_epochs": int((~holdout_mask).sum()),
        "compared_epochs": int(holdout_mask.sum()),
        "kappa": metrics["kappa"],
        "accuracy": metrics["accuracy"],
    }
    row.update(format_stage_metrics(metrics_by_stage))
    row.update(flatten_confusion_counts(cm))
    return row, cm


def summarize_metric(series: pd.Series) -> tuple[float, float]:
    """Return mean and sample SD for a metric column.

    :param series: pandas Series of numeric values
    :return: tuple of (mean, sample_sd); sd is 0.0 if fewer than two rows
    """
    mean = float(series.mean())
    sd = float(series.std(ddof=1)) if len(series) > 1 else 0.0
    return mean, sd


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run held-out validation for all recordings and save metrics."""
    args = parse_args()

    predicted_labels_dir = Path(args.predicted_labels_dir)
    output_path = Path(args.output_path)

    if not os.path.isdir(args.data_dir):
        print(f"ERROR: data_dir not found: {args.data_dir}", file=sys.stderr)
        sys.exit(1)
    if not predicted_labels_dir.is_dir():
        print(f"ERROR: predicted_labels_dir not found: {predicted_labels_dir}", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("AccuSleePy Validation - Phase 4 Component B")
    print("=" * 70)
    print(f"Data directory         : {args.data_dir}")
    print(f"Predicted labels dir   : {predicted_labels_dir}")
    print(f"Validation output path : {output_path}")
    print()

    recordings = find_all_recordings(args.data_dir)
    total = len(recordings)
    print(f"Recordings found: {total}")
    print("Validation policy: exclude the exact Phase 3 calibration epochs from comparison.")
    print()

    rows = []
    aggregate_cm = np.zeros((3, 3), dtype=np.int64)
    failures = []

    for i, rec in enumerate(recordings, start=1):
        recording_id = rec["recording_id"]
        print(f"[{i:02d}/{total}] Validating {recording_id}...", end=" ", flush=True)
        try:
            row, cm = validate_recording(rec, predicted_labels_dir)
            rows.append(row)
            aggregate_cm += cm
            print(
                f"done. kappa={row['kappa']:.4f}, accuracy={row['accuracy']:.4f}, "
                f"held-out={row['compared_epochs']}"
            )
        except Exception as exc:
            print(f"FAILED: {exc}")
            failures.append((recording_id, str(exc)))

    print()
    if failures:
        print("=" * 70)
        print(f"Validation failed for {len(failures)} recording(s):", file=sys.stderr)
        for recording_id, message in failures:
            print(f"  {recording_id}: {message}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame(rows).sort_values(["mouse_id", "day_id"]).reset_index(drop=True)
    df.to_csv(output_path, index=False)

    mean_kappa, sd_kappa = summarize_metric(df["kappa"])
    mean_accuracy, sd_accuracy = summarize_metric(df["accuracy"])
    aggregate_stage_metrics = per_class_metrics(
        np.repeat([1, 2, 3], aggregate_cm.sum(axis=1)),
        np.concatenate(
            [
                np.repeat([1, 2, 3], aggregate_cm[row_idx])
                for row_idx in range(aggregate_cm.shape[0])
            ]
        ),
    )

    print("=" * 70)
    print(f"Validation summary written to: {output_path}")
    print()
    print(f"Aggregate kappa   : {mean_kappa:.4f} +/- {sd_kappa:.4f}")
    print(f"Aggregate accuracy: {mean_accuracy:.4f} +/- {sd_accuracy:.4f}")
    print()
    print("Aggregate per-class metrics (summed held-out confusion matrix):")
    for stage_name, _ in STAGE_ORDER:
        stage_metrics = aggregate_stage_metrics[stage_name]
        print(
            f"  {stage_name:<4} precision={stage_metrics['precision']:.4f} "
            f"recall={stage_metrics['recall']:.4f} "
            f"f1={stage_metrics['f1']:.4f}"
        )
    print("=" * 70)


if __name__ == "__main__":
    main()
