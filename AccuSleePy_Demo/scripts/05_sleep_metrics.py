"""Phase 5: Descriptive Sleep Metrics

Computes per-recording sleep architecture metrics from AccuSleePy predicted
labels (Phase 3 outputs). All metrics are derived solely from predicted labels
and confidence scores — expert labels are not used.

Metrics computed per recording
-------------------------------
Stage proportions:
    % Wake, % NREM, % REM

Bout analysis (per stage):
    mean bout duration (s), maximum bout duration (s), total bout count

Stage transition probability matrix:
    For each current state, the fraction of epoch-to-epoch transitions that
    lead to each next state (3x3, rows sum to 1.0).

Low-confidence epoch summary:
    Count and percentage of epochs with confidence_score <= threshold.

Usage
-----
python scripts/05_sleep_metrics.py \\
    --predicted_labels_dir AccuSleePy_Demo/outputs/predicted_labels \\
    --output_path AccuSleePy_Demo/outputs/sleep_metrics.csv \\
    [--confidence_threshold 0.8]
"""

import argparse
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Make utils importable from any working directory
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from utils.data_loading import load_predicted_labels  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EPOCH_DURATION_S = 2.5          # seconds per epoch
STAGES = {1: "REM", 2: "Wake", 3: "NREM"}
STAGE_ORDER = [2, 3, 1]         # Wake, NREM, REM (display order)
STAGE_NAMES = {2: "wake", 3: "nrem", 1: "rem"}


# ---------------------------------------------------------------------------
# Per-recording metric functions
# ---------------------------------------------------------------------------

def compute_stage_proportions(labels: np.ndarray) -> dict[str, float]:
    """Compute the percentage of epochs in each sleep stage.

    :param labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: dict with keys ``pct_wake``, ``pct_nrem``, ``pct_rem``;
        values are percentages in [0, 100]
    """
    n = len(labels)
    if n == 0:
        return {"pct_wake": 0.0, "pct_nrem": 0.0, "pct_rem": 0.0}
    return {
        "pct_wake": float(np.sum(labels == 2) / n * 100),
        "pct_nrem": float(np.sum(labels == 3) / n * 100),
        "pct_rem":  float(np.sum(labels == 1) / n * 100),
    }


def compute_bouts(labels: np.ndarray) -> dict[str, dict[str, float]]:
    """Compute bout-level statistics for each sleep stage.

    A *bout* is a contiguous run of epochs assigned to the same stage.
    Durations are reported in seconds (epochs × 2.5 s/epoch).

    :param labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: nested dict; outer key is stage name (``"wake"``, ``"nrem"``,
        ``"rem"``); inner dict has keys:
        - ``mean_bout_s`` (float) – mean bout duration in seconds; NaN if stage absent
        - ``max_bout_s``  (float) – maximum bout duration in seconds; NaN if stage absent
        - ``bout_count``  (int)   – number of bouts
    """
    result = {}
    for stage_val, stage_key in STAGE_NAMES.items():
        # Find runs of this stage using run-length encoding
        is_stage = (labels == stage_val).astype(np.int8)
        # np.diff finds edges; prepend/append 0 to capture leading/trailing runs
        padded = np.concatenate(([0], is_stage, [0]))
        diff = np.diff(padded)
        starts = np.where(diff == 1)[0]
        ends   = np.where(diff == -1)[0]
        lengths_s = (ends - starts) * EPOCH_DURATION_S  # in seconds

        if len(lengths_s) == 0:
            result[stage_key] = {
                "mean_bout_s": float("nan"),
                "max_bout_s":  float("nan"),
                "bout_count":  0,
            }
        else:
            result[stage_key] = {
                "mean_bout_s": float(np.mean(lengths_s)),
                "max_bout_s":  float(np.max(lengths_s)),
                "bout_count":  int(len(lengths_s)),
            }
    return result


def compute_transition_matrix(labels: np.ndarray) -> dict[str, float]:
    """Compute the stage transition probability matrix.

    For each epoch t, the transition is from labels[t] to labels[t+1].
    The matrix is normalized per row so each row sums to 1.0 (or 0.0 if a
    state never occurs).

    :param labels: 1-D integer array of predicted labels {1, 2, 3}
    :return: flat dict with keys of the form ``trans_<from>_to_<to>`` where
        ``<from>`` and ``<to>`` are lower-case stage names (``wake``, ``nrem``,
        ``rem``).  Values are row-normalized probabilities.
    """
    # Build raw count matrix: rows = from, cols = to; index 0=Wake, 1=NREM, 2=REM
    label_to_idx = {2: 0, 3: 1, 1: 2}  # Wake=0, NREM=1, REM=2
    idx_to_name  = {0: "wake", 1: "nrem", 2: "rem"}
    n_states = 3
    counts = np.zeros((n_states, n_states), dtype=np.int64)

    if len(labels) >= 2:
        from_states = labels[:-1]
        to_states   = labels[1:]
        for fs, ts in zip(from_states, to_states):
            if fs in label_to_idx and ts in label_to_idx:
                counts[label_to_idx[fs], label_to_idx[ts]] += 1

    # Row-normalize
    row_sums = counts.sum(axis=1, keepdims=True)
    # Avoid division by zero for states that never occur
    probs = np.where(row_sums > 0, counts / row_sums, 0.0)

    flat = {}
    for from_idx in range(n_states):
        from_name = idx_to_name[from_idx]
        for to_idx in range(n_states):
            to_name = idx_to_name[to_idx]
            flat[f"trans_{from_name}_to_{to_name}"] = float(probs[from_idx, to_idx])
    return flat


def compute_low_confidence_summary(
    confidence_scores: np.ndarray, threshold: float
) -> dict[str, float]:
    """Summarize the number and fraction of low-confidence epochs.

    :param confidence_scores: 1-D float array of per-epoch confidence scores
    :param threshold: epochs with score <= threshold are considered low-confidence
    :return: dict with keys ``low_conf_count`` (int) and ``low_conf_pct`` (float)
    """
    n = len(confidence_scores)
    count = int(np.sum(confidence_scores <= threshold))
    pct   = float(count / n * 100) if n > 0 else 0.0
    return {"low_conf_count": count, "low_conf_pct": pct}


# ---------------------------------------------------------------------------
# Filename parsing
# ---------------------------------------------------------------------------

def parse_recording_id(filename: str) -> tuple[str, str, str]:
    """Extract recording_id, mouse_id, and day_id from a predicted-label filename.

    Expects filename stem of the form ``MouseXX_DayY`` (e.g. ``Mouse01_Day1``).

    :param filename: basename of the predicted-label CSV file (with or without extension)
    :return: tuple of (recording_id, mouse_id, day_id)
    :raises ValueError: if the filename does not match the expected pattern
    """
    stem = Path(filename).stem  # drop .csv
    parts = stem.split("_")
    if len(parts) != 2 or not parts[0].startswith("Mouse") or not parts[1].startswith("Day"):
        raise ValueError(
            f"Unexpected predicted-label filename format: '{filename}'. "
            "Expected '<MouseXX>_<DayY>.csv'."
        )
    mouse_id, day_id = parts
    return stem, mouse_id, day_id


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def build_metrics_row(
    recording_id: str,
    mouse_id: str,
    day_id: str,
    labels: np.ndarray,
    confidence_scores: np.ndarray,
    confidence_threshold: float,
) -> dict:
    """Compute all sleep metrics for one recording and return as a flat dict.

    :param recording_id: e.g. ``"Mouse01_Day1"``
    :param mouse_id: e.g. ``"Mouse01"``
    :param day_id: e.g. ``"Day1"``
    :param labels: 1-D integer array of predicted labels {1, 2, 3}
    :param confidence_scores: 1-D float array of per-epoch confidence scores
    :param confidence_threshold: epochs with confidence <= this value are low-confidence
    :return: flat dict suitable for a single row in sleep_metrics.csv
    """
    row = {
        "recording_id": recording_id,
        "mouse_id":     mouse_id,
        "day_id":       day_id,
    }

    # Stage proportions
    row.update(compute_stage_proportions(labels))

    # Bout analysis — flatten nested dict
    bouts = compute_bouts(labels)
    for stage_key, stats in bouts.items():
        for metric_name, value in stats.items():
            row[f"{stage_key}_{metric_name}"] = value

    # Transition matrix
    row.update(compute_transition_matrix(labels))

    # Low-confidence summary
    row.update(compute_low_confidence_summary(confidence_scores, confidence_threshold))

    return row


def run(predicted_labels_dir: str, output_path: str, confidence_threshold: float) -> None:
    """Run the Phase 5 sleep metrics pipeline.

    Iterates over all predicted-label CSV files in *predicted_labels_dir*,
    computes per-recording metrics, and saves the full table to *output_path*.

    :param predicted_labels_dir: path to directory containing predicted-label
        CSV files from Phase 3 (e.g. ``AccuSleePy_Demo/outputs/predicted_labels``)
    :param output_path: path for the output CSV (e.g.
        ``AccuSleePy_Demo/outputs/sleep_metrics.csv``)
    :param confidence_threshold: confidence score at or below which an epoch is
        counted as low-confidence (default: 0.8)
    :raises FileNotFoundError: if predicted_labels_dir does not exist
    """
    pred_dir = Path(predicted_labels_dir).resolve()
    if not pred_dir.is_dir():
        print(f"ERROR: predicted_labels_dir not found: {pred_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect only the predicted-label files (exclude calibration index files)
    label_files = sorted(
        f for f in pred_dir.glob("*.csv")
        if not f.name.endswith("_calibration_indices.csv")
    )
    if not label_files:
        print(f"ERROR: No predicted-label CSV files found in: {pred_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(label_files)} predicted-label files in: {pred_dir}")
    print(f"Confidence threshold: <= {confidence_threshold}")
    print(f"Output path: {output_path}")
    print()

    rows = []
    errors = []

    for i, label_path in enumerate(label_files, start=1):
        try:
            recording_id, mouse_id, day_id = parse_recording_id(label_path.name)
        except ValueError as e:
            errors.append(str(e))
            continue

        try:
            labels, confidence_scores = load_predicted_labels(str(label_path))
        except Exception as e:
            errors.append(f"{label_path.name}: failed to load — {e}")
            continue

        # Validate label values
        unexpected = set(np.unique(labels)) - {1, 2, 3}
        if unexpected:
            errors.append(
                f"{recording_id}: unexpected label values in predicted labels: {unexpected}"
            )
            continue

        row = build_metrics_row(
            recording_id, mouse_id, day_id,
            labels, confidence_scores, confidence_threshold
        )
        rows.append(row)

        print(
            f"  [{i:3d}/{len(label_files)}] {recording_id:20s}  "
            f"Wake={row['pct_wake']:5.1f}%  NREM={row['pct_nrem']:5.1f}%  "
            f"REM={row['pct_rem']:5.1f}%  "
            f"low_conf={row['low_conf_count']}"
        )

    if errors:
        print(f"\n{len(errors)} error(s) encountered:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        sys.exit(1)

    # Build DataFrame and save
    df = pd.DataFrame(rows)
    # Sort by mouse_id, day_id for consistent ordering
    df = df.sort_values(["mouse_id", "day_id"]).reset_index(drop=True)

    out_path = Path(output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(out_path), index=False, float_format="%.6f")

    # Print aggregate summary
    print()
    print("=" * 60)
    print("GROUP-LEVEL SUMMARY (all recordings)")
    print("=" * 60)
    print(f"  Recordings processed  : {len(df)}")
    print(f"  Mean % Wake           : {df['pct_wake'].mean():.2f} ± {df['pct_wake'].std():.2f}")
    print(f"  Mean % NREM           : {df['pct_nrem'].mean():.2f} ± {df['pct_nrem'].std():.2f}")
    print(f"  Mean % REM            : {df['pct_rem'].mean():.2f} ± {df['pct_rem'].std():.2f}")
    print()
    for stage_key in ["wake", "nrem", "rem"]:
        mean_col = f"{stage_key}_mean_bout_s"
        print(
            f"  Mean {stage_key.upper():4s} bout duration : "
            f"{df[mean_col].mean():.1f} ± {df[mean_col].std():.1f} s"
        )
    print()
    print(f"  Total low-conf epochs : {df['low_conf_count'].sum()}")
    print(f"  Mean low-conf %       : {df['low_conf_pct'].mean():.3f}%")
    print()
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse CLI arguments and run the sleep metrics pipeline."""
    parser = argparse.ArgumentParser(
        description=(
            "Phase 5 — Compute descriptive sleep metrics from AccuSleePy "
            "predicted labels. Outputs per-recording stage proportions, bout "
            "statistics, transition probabilities, and low-confidence epoch "
            "counts to a CSV file."
        )
    )
    parser.add_argument(
        "--predicted_labels_dir",
        required=True,
        help="Path to the directory containing predicted-label CSV files from Phase 3 "
             "(e.g. AccuSleePy_Demo/outputs/predicted_labels)",
    )
    parser.add_argument(
        "--output_path",
        default=os.path.join("AccuSleePy_Demo", "outputs", "sleep_metrics.csv"),
        help="Output path for the sleep_metrics CSV "
             "(default: AccuSleePy_Demo/outputs/sleep_metrics.csv)",
    )
    parser.add_argument(
        "--confidence_threshold",
        type=float,
        default=0.8,
        help="Confidence score at or below which an epoch is counted as "
             "low-confidence (default: 0.8)",
    )
    args = parser.parse_args()

    run(
        predicted_labels_dir=args.predicted_labels_dir,
        output_path=args.output_path,
        confidence_threshold=args.confidence_threshold,
    )


if __name__ == "__main__":
    main()
