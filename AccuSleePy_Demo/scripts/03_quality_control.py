"""Quality control checks for AccuSleePy predicted sleep-stage labels.

Runs three QC checks on the AccuSleePy predicted labels for all 50 recordings
and writes two sets of outputs:

1. Per-recording low-confidence epoch CSVs in ``low_confidence_epochs/``:
   - One file per recording listing all epochs with confidence_score <= 0.8.
   - Columns: epoch_index, predicted_label, confidence_score.
   - Written even if no low-confidence epochs exist (header row only).

2. ``QC_report.md``:
   - Flags for stage proportion violations and long-run violations.
   - Low-confidence epoch counts per recording.

QC Checks
---------
Stage proportion plausibility (for a 4-hour daytime C57BL/6 mouse recording):
    - Wake > 80%  → flag (possible electrode/signal quality issue)
    - REM  > 25%  → flag (unusually high for a light-phase recording)
    - NREM < 10%  → flag

Long unbroken run:
    - Any single-stage unbroken stretch > 60 minutes → flag
    - At 2.5 s/epoch: 60 min = 3,600 s / 2.5 s = 1,440 epochs

Low-confidence epoch listing:
    - confidence_score <= 0.8 → listed in per-recording CSV

Decision rule (per Project Details.md):
    Flagged recordings are NOT excluded. Document and let the researcher decide.

Usage
-----
    python scripts/03_quality_control.py \\
        --predicted_labels_dir AccuSleePy_Demo/outputs/predicted_labels \\
        --output_dir AccuSleePy_Demo \\
        [--confidence_threshold 0.8] \\
        [--wake_high_threshold 0.80] \\
        [--rem_high_threshold 0.25] \\
        [--nrem_low_threshold 0.10] \\
        [--long_run_minutes 60]

All threshold arguments have default values matching Project Details.md.
Only ``--predicted_labels_dir`` and ``--output_dir`` are required.
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

from utils.data_loading import load_predicted_labels


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EPOCH_DURATION_S = 2.5          # seconds per epoch
LABEL_NAMES = {1: "REM", 2: "Wake", 3: "NREM"}
CONFIDENCE_THRESHOLD = 0.8      # default: flag epochs at or below this value


# ---------------------------------------------------------------------------
# QC helper functions
# ---------------------------------------------------------------------------

def compute_stage_proportions(labels: np.ndarray) -> dict[str, float]:
    """Return the proportion (fraction) of each sleep stage.

    :param labels: 1-D integer array with values {1, 2, 3}
    :return: dict with keys 'REM', 'Wake', 'NREM' and float values in [0, 1]
    """
    n = len(labels)
    return {
        "REM":  float(np.sum(labels == 1) / n),
        "Wake": float(np.sum(labels == 2) / n),
        "NREM": float(np.sum(labels == 3) / n),
    }


def check_stage_proportions(
    props: dict[str, float],
    wake_high: float,
    rem_high: float,
    nrem_low: float,
) -> list[str]:
    """Return a list of flag strings for stage-proportion violations.

    :param props: dict from compute_stage_proportions
    :param wake_high: flag if Wake > this threshold
    :param rem_high:  flag if REM  > this threshold
    :param nrem_low:  flag if NREM < this threshold
    :return: list of human-readable flag strings (empty if no violations)
    """
    flags = []
    if props["Wake"] > wake_high:
        flags.append(
            f"Wake proportion {props['Wake']:.1%} exceeds {wake_high:.0%} threshold "
            f"(possible electrode/signal quality issue)"
        )
    if props["REM"] > rem_high:
        flags.append(
            f"REM proportion {props['REM']:.1%} exceeds {rem_high:.0%} threshold "
            f"(unusually high for a light-phase recording)"
        )
    if props["NREM"] < nrem_low:
        flags.append(
            f"NREM proportion {props['NREM']:.1%} below {nrem_low:.0%} threshold"
        )
    return flags


def find_long_runs(labels: np.ndarray, max_run_epochs: int) -> list[str]:
    """Return flag strings for any unbroken single-stage run exceeding max_run_epochs.

    :param labels: 1-D integer array with values {1, 2, 3}
    :param max_run_epochs: run length threshold in epochs; runs *longer* than
        this are flagged
    :return: list of human-readable flag strings (empty if no violations)
    """
    flags = []
    if len(labels) == 0:
        return flags

    current_label = labels[0]
    current_run = 1
    for label in labels[1:]:
        if label == current_label:
            current_run += 1
        else:
            if current_run > max_run_epochs:
                duration_min = current_run * EPOCH_DURATION_S / 60
                flags.append(
                    f"Unbroken {LABEL_NAMES[current_label]} run of {current_run} epochs "
                    f"({duration_min:.1f} min) exceeds {max_run_epochs * EPOCH_DURATION_S / 60:.0f}-min threshold"
                )
            current_label = label
            current_run = 1
    # Check the final run
    if current_run > max_run_epochs:
        duration_min = current_run * EPOCH_DURATION_S / 60
        flags.append(
            f"Unbroken {LABEL_NAMES[current_label]} run of {current_run} epochs "
            f"({duration_min:.1f} min) exceeds {max_run_epochs * EPOCH_DURATION_S / 60:.0f}-min threshold"
        )
    return flags


def get_low_confidence_epochs(
    labels: np.ndarray,
    conf_scores: np.ndarray,
    threshold: float,
) -> pd.DataFrame:
    """Return a DataFrame of epochs with confidence_score at or below the threshold.

    :param labels: 1-D integer array of predicted labels
    :param conf_scores: 1-D float array of confidence scores, same length as labels
    :param threshold: confidence score at or below which an epoch is considered
        low-confidence
    :return: DataFrame with columns [epoch_index, predicted_label, confidence_score];
        sorted by epoch_index; empty (header only) if no low-confidence epochs exist
    """
    mask = conf_scores <= threshold
    indices = np.where(mask)[0]
    return pd.DataFrame(
        {
            "epoch_index":      indices,
            "predicted_label":  labels[indices],
            "confidence_score": conf_scores[indices],
        }
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run QC checks on all predicted label files and write outputs."""
    parser = argparse.ArgumentParser(
        description="Quality control checks for AccuSleePy predicted labels."
    )
    parser.add_argument(
        "--predicted_labels_dir",
        required=True,
        help="Directory containing predicted label CSVs from 02_accusleepy_scoring.py "
             "(e.g. AccuSleePy_Demo/outputs/predicted_labels)",
    )
    parser.add_argument(
        "--output_dir",
        required=True,
        help="Root output directory for QC outputs "
             "(e.g. AccuSleePy_Demo); QC_report.md and low_confidence_epochs/ "
             "are written here",
    )
    parser.add_argument(
        "--confidence_threshold",
        type=float,
        default=CONFIDENCE_THRESHOLD,
        help=f"Confidence score at or below which an epoch is flagged as low-confidence "
             f"(default: {CONFIDENCE_THRESHOLD})",
    )
    parser.add_argument(
        "--wake_high_threshold",
        type=float,
        default=0.80,
        help="Flag recording if Wake proportion exceeds this value (default: 0.80)",
    )
    parser.add_argument(
        "--rem_high_threshold",
        type=float,
        default=0.25,
        help="Flag recording if REM proportion exceeds this value (default: 0.25)",
    )
    parser.add_argument(
        "--nrem_low_threshold",
        type=float,
        default=0.10,
        help="Flag recording if NREM proportion is below this value (default: 0.10)",
    )
    parser.add_argument(
        "--long_run_minutes",
        type=float,
        default=60.0,
        help="Flag any unbroken single-stage run longer than this many minutes "
             "(default: 60)",
    )
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Validate inputs
    # -----------------------------------------------------------------------
    pred_dir = Path(args.predicted_labels_dir)
    if not pred_dir.is_dir():
        print(f"ERROR: predicted_labels_dir not found: {pred_dir}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output_dir)
    low_conf_dir = out_dir / "low_confidence_epochs"
    low_conf_dir.mkdir(parents=True, exist_ok=True)

    qc_report_path = out_dir / "QC_report.md"

    # Convert long-run threshold from minutes to epochs
    long_run_epochs = int(args.long_run_minutes * 60 / EPOCH_DURATION_S)

    # -----------------------------------------------------------------------
    # Collect all predicted-label files (exclude calibration-index files)
    # -----------------------------------------------------------------------
    label_files = sorted(
        f for f in pred_dir.glob("*.csv")
        if not f.name.endswith("_calibration_indices.csv")
    )
    if not label_files:
        print(f"ERROR: No predicted label CSVs found in {pred_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(label_files)} predicted label file(s).")
    print(
        f"QC thresholds: Wake > {args.wake_high_threshold:.0%}, "
        f"REM > {args.rem_high_threshold:.0%}, "
        f"NREM < {args.nrem_low_threshold:.0%}, "
        f"long run > {args.long_run_minutes:.0f} min, "
        f"low confidence <= {args.confidence_threshold}"
    )
    print()

    # -----------------------------------------------------------------------
    # Per-recording QC
    # -----------------------------------------------------------------------
    all_flags: list[dict] = []          # {recording_id, flags: [str]}
    low_conf_counts: list[dict] = []    # {recording_id, n_low_conf, pct_low_conf}

    for i, label_file in enumerate(label_files, 1):
        recording_id = label_file.stem
        print(f"[{i:02d}/{len(label_files)}] {recording_id} ...", end=" ", flush=True)

        # Load predicted labels and confidence scores
        labels, conf_scores = load_predicted_labels(str(label_file))
        n_total = len(labels)

        # --- Stage proportion check ---
        props = compute_stage_proportions(labels)
        prop_flags = check_stage_proportions(
            props,
            args.wake_high_threshold,
            args.rem_high_threshold,
            args.nrem_low_threshold,
        )

        # --- Long-run check ---
        run_flags = find_long_runs(labels, long_run_epochs)

        # --- Low-confidence epoch listing ---
        low_conf_df = get_low_confidence_epochs(labels, conf_scores, args.confidence_threshold)
        n_low_conf = len(low_conf_df)
        pct_low_conf = n_low_conf / n_total if n_total > 0 else 0.0

        # Save per-recording low-confidence CSV
        low_conf_path = low_conf_dir / f"{recording_id}_low_confidence.csv"
        low_conf_df.to_csv(low_conf_path, index=False)

        # Collect results
        all_flags_for_rec = prop_flags + run_flags
        all_flags.append({"recording_id": recording_id, "flags": all_flags_for_rec})
        low_conf_counts.append(
            {
                "recording_id": recording_id,
                "n_low_confidence": n_low_conf,
                "pct_low_confidence": pct_low_conf,
                "wake_pct": props["Wake"],
                "nrem_pct": props["NREM"],
                "rem_pct":  props["REM"],
            }
        )

        flag_str = f"{len(all_flags_for_rec)} flag(s), {n_low_conf} low-conf epoch(s)"
        print(f"done. ({flag_str})")

    print()

    # -----------------------------------------------------------------------
    # Write QC_report.md
    # -----------------------------------------------------------------------
    flagged = [r for r in all_flags if r["flags"]]
    n_flagged = len(flagged)

    with open(qc_report_path, "w", encoding="utf-8") as f:
        f.write("# QC Report — AccuSleePy Demo\n\n")
        f.write(f"**Generated by:** `scripts/03_quality_control.py`\n\n")
        f.write(f"**Predicted labels directory:** `{pred_dir}`\n\n")
        f.write("**QC thresholds:**\n")
        f.write(f"- Wake proportion > {args.wake_high_threshold:.0%}: flagged\n")
        f.write(f"- REM proportion  > {args.rem_high_threshold:.0%}: flagged\n")
        f.write(f"- NREM proportion < {args.nrem_low_threshold:.0%}: flagged\n")
        f.write(
            f"- Unbroken single-stage run > {args.long_run_minutes:.0f} min "
            f"({long_run_epochs} epochs): flagged\n"
        )
        f.write(
            f"- Confidence score ≤ {args.confidence_threshold}: listed in "
            f"low_confidence_epochs/ (not flagged)\n"
        )
        f.write("\n**Decision rule:** Flagged recordings are NOT excluded from analysis. "
                "Flags are documented here for researcher review.\n\n")
        f.write("---\n\n")

        # --- Flagged recordings ---
        f.write(f"## Flagged Recordings ({n_flagged} of {len(all_flags)})\n\n")
        if n_flagged == 0:
            f.write("No recordings were flagged.\n\n")
        else:
            for rec in flagged:
                f.write(f"### {rec['recording_id']}\n\n")
                for flag in rec["flags"]:
                    f.write(f"- {flag}\n")
                f.write("\n")

        f.write("---\n\n")

        # --- Low-confidence epoch summary table ---
        f.write("## Low-Confidence Epoch Summary\n\n")
        f.write(
            f"Confidence threshold: ≤ {args.confidence_threshold}. "
            f"Per-recording CSVs in `low_confidence_epochs/`.\n\n"
        )
        f.write("| Recording | N Low-Confidence | % of Total |\n")
        f.write("|---|---|---|\n")
        for rec in low_conf_counts:
            f.write(
                f"| {rec['recording_id']} "
                f"| {rec['n_low_confidence']} "
                f"| {rec['pct_low_confidence']:.2%} |\n"
            )
        f.write("\n")

        # --- Stage proportion summary table ---
        f.write("## Stage Proportion Summary (Predicted Labels)\n\n")
        f.write("| Recording | % Wake | % NREM | % REM | Flagged |\n")
        f.write("|---|---|---|---|---|\n")
        flag_lookup = {r["recording_id"]: r["flags"] for r in all_flags}
        for rec in low_conf_counts:
            rid = rec["recording_id"]
            flagged_marker = "Yes" if flag_lookup[rid] else ""
            f.write(
                f"| {rid} "
                f"| {rec['wake_pct']:.1%} "
                f"| {rec['nrem_pct']:.1%} "
                f"| {rec['rem_pct']:.1%} "
                f"| {flagged_marker} |\n"
            )
        f.write("\n")

    print(f"QC report written to: {qc_report_path}")
    print(f"Low-confidence epoch CSVs written to: {low_conf_dir}")
    print()

    # -----------------------------------------------------------------------
    # Print summary to stdout
    # -----------------------------------------------------------------------
    total_low_conf = sum(r["n_low_confidence"] for r in low_conf_counts)
    print(f"Summary:")
    print(f"  Recordings processed    : {len(all_flags)}")
    print(f"  Recordings flagged      : {n_flagged}")
    print(f"  Total low-conf epochs   : {total_low_conf}")
    if flagged:
        print(f"\nFlagged recordings:")
        for rec in flagged:
            print(f"  {rec['recording_id']}:")
            for flag in rec["flags"]:
                print(f"    - {flag}")


if __name__ == "__main__":
    main()
