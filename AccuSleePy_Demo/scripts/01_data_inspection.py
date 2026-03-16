"""Dataset inspection script for AccuSleePy Demo (Phase 2).

Loads every recording in the dataset, verifies signal dimensions, epoch
structure, sampling rate, and label encoding, then prints a human-readable
summary covering all items required by the Phase 2 specification.

The summary is printed to stdout AND saved to ``outputs/data_info.txt``
inside the output directory so it can be referenced without re-running
the script.

Usage
-----
::

    python scripts/01_data_inspection.py --data_dir C:\\Datasets\\AccuSleePy_Data

    # Specify a custom output directory (default: AccuSleePy_Demo/outputs):
    python scripts/01_data_inspection.py --data_dir C:\\Datasets\\AccuSleePy_Data \\
        --output_dir AccuSleePy_Demo/outputs
"""

import argparse
import io
import os
import sys

import numpy as np

# Allow importing from scripts/utils when running from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.utils.data_loading import find_all_recordings, load_eeg_emg, load_expert_labels


# ---------------------------------------------------------------------------
# Constants matching the dataset specification
# ---------------------------------------------------------------------------
EXPECTED_SAMPLING_RATE_HZ = 512
EXPECTED_EPOCH_LENGTH_S = 2.5
EXPECTED_SAMPLES_PER_EPOCH = int(EXPECTED_SAMPLING_RATE_HZ * EXPECTED_EPOCH_LENGTH_S)  # 1280
EXPECTED_RECORDING_DURATION_H = 4
EXPECTED_TOTAL_SAMPLES = int(
    EXPECTED_RECORDING_DURATION_H * 3600 * EXPECTED_SAMPLING_RATE_HZ
)  # 7,372,800
EXPECTED_EPOCH_COUNT = int(
    EXPECTED_RECORDING_DURATION_H * 3600 / EXPECTED_EPOCH_LENGTH_S
)  # 5,760
LABEL_ENCODING = {1: "REM", 2: "Wake", 3: "NREM"}
# Minimum calibration epochs required per stage (Phase 3 constraint)
MIN_CALIBRATION_EPOCHS = 120


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    :return: parsed namespace with ``data_dir`` and ``output_dir`` attributes
    """
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the AccuSleePy dataset and print a structured summary. "
            "Output is also saved to <output_dir>/data_info.txt."
        )
    )
    parser.add_argument(
        "--data_dir",
        required=True,
        help="Root directory of the AccuSleePy dataset (must contain '4-hour_recordings/').",
    )
    parser.add_argument(
        "--output_dir",
        default=os.path.join("AccuSleePy_Demo", "outputs"),
        help=(
            "Directory where data_info.txt will be written. "
            "Created automatically if it does not exist. "
            "Default: AccuSleePy_Demo/outputs"
        ),
    )
    return parser.parse_args()


def format_size(path: str) -> str:
    """Return a human-readable file size string for a given path.

    :param path: file path
    :return: size string, e.g. ``"14.2 MB"``
    """
    size_bytes = os.path.getsize(path)
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main() -> None:
    """Run dataset inspection, print summary to stdout, and save to data_info.txt."""
    args = parse_args()

    # Tee all output to both stdout and a string buffer so we can save it
    buffer = io.StringIO()

    class _Tee:
        """Write to both a real stream and a buffer simultaneously."""

        def __init__(self, real_stream, buf):
            self._real = real_stream
            self._buf = buf

        def write(self, text):
            self._real.write(text)
            self._buf.write(text)

        def flush(self):
            self._real.flush()
            self._buf.flush()

    sys.stdout = _Tee(sys.__stdout__, buffer)

    try:
        _run_inspection(args)
    finally:
        sys.stdout = sys.__stdout__

    # Save captured output to data_info.txt
    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, "data_info.txt")
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(buffer.getvalue())
    print(f"\nOutput saved to: {output_path}")


def _run_inspection(args: argparse.Namespace) -> None:
    """Execute all dataset inspection steps and print results.

    :param args: parsed CLI arguments (``data_dir``, ``output_dir``)
    """
    print("=" * 70)
    print("AccuSleePy Dataset Inspection")
    print("=" * 70)
    print(f"Data directory : {args.data_dir}")
    print()

    # ------------------------------------------------------------------
    # 1. Discover all recordings
    # ------------------------------------------------------------------
    recordings = find_all_recordings(args.data_dir)
    total_recordings = len(recordings)
    print(f"Total recordings found: {total_recordings}")
    print()

    # ------------------------------------------------------------------
    # 2. File inventory — per-recording listing
    # ------------------------------------------------------------------
    print("-" * 70)
    print("FILE INVENTORY")
    print("-" * 70)
    print(f"{'Recording ID':<22}  {'recording.parquet':>18}  {'labels.csv':>12}")
    print(f"{'-'*22}  {'-'*18}  {'-'*12}")
    for rec in recordings:
        rec_size = format_size(rec["recording_path"])
        lbl_size = format_size(rec["label_path"])
        print(f"{rec['recording_id']:<22}  {rec_size:>18}  {lbl_size:>12}")
    print()

    # ------------------------------------------------------------------
    # 3. Representative recording — shapes, dtypes, sampling rate check
    # ------------------------------------------------------------------
    rep = recordings[0]
    print("-" * 70)
    print(f"REPRESENTATIVE RECORDING: {rep['recording_id']}")
    print("-" * 70)

    eeg, emg = load_eeg_emg(rep["recording_path"])
    labels = load_expert_labels(rep["label_path"])

    print(f"  EEG array shape : {eeg.shape}   dtype: {eeg.dtype}")
    print(f"  EMG array shape : {emg.shape}   dtype: {emg.dtype}")
    print(f"  Label array shape: {labels.shape}   dtype: {labels.dtype}")
    print()

    # Sampling rate verification
    actual_samples = len(eeg)
    print(f"  Expected samples (4h @ {EXPECTED_SAMPLING_RATE_HZ} Hz): {EXPECTED_TOTAL_SAMPLES:,}")
    print(f"  Actual samples                                : {actual_samples:,}")
    sample_match = actual_samples == EXPECTED_TOTAL_SAMPLES
    print(f"  Sampling rate check : {'PASS' if sample_match else 'FAIL'}")
    print()

    # Epoch structure verification
    actual_epochs = len(labels)
    print(f"  Expected epochs (4h / {EXPECTED_EPOCH_LENGTH_S}s): {EXPECTED_EPOCH_COUNT:,}")
    print(f"  Actual epochs                          : {actual_epochs:,}")
    epoch_match = actual_epochs == EXPECTED_EPOCH_COUNT
    print(
        f"  Samples per epoch ({EXPECTED_SAMPLING_RATE_HZ} Hz × {EXPECTED_EPOCH_LENGTH_S}s): "
        f"{EXPECTED_SAMPLES_PER_EPOCH}"
    )
    print(f"  Epoch structure check: {'PASS' if epoch_match else 'FAIL'}")
    print()

    # Label encoding for representative recording
    unique_vals = sorted(np.unique(labels).tolist())
    print(f"  Unique label values: {unique_vals}")
    for val, name in sorted(LABEL_ENCODING.items()):
        count = int(np.sum(labels == val))
        pct = 100.0 * count / actual_epochs
        print(f"    {val} = {name}: {count} epochs ({pct:.1f}%)")
    print()

    # ------------------------------------------------------------------
    # 4. Full dataset scan
    # ------------------------------------------------------------------
    print("-" * 70)
    print("FULL DATASET SCAN")
    print("-" * 70)

    anomalies = []
    all_label_counts = {1: [], 2: [], 3: []}  # REM, Wake, NREM counts per recording
    all_label_arrays = []

    for i, rec in enumerate(recordings):
        try:
            eeg, emg = load_eeg_emg(rec["recording_path"])
            labels = load_expert_labels(rec["label_path"])
        except Exception as exc:
            anomalies.append(f"  LOAD FAILURE [{rec['recording_id']}]: {exc}")
            print(f"  [{i+1:02d}/{total_recordings}] {rec['recording_id']} — LOAD FAILURE")
            continue

        n_samples = len(eeg)
        n_epochs = len(labels)
        unique_vals = sorted(np.unique(labels).tolist())

        # Collect counts
        for val in [1, 2, 3]:
            all_label_counts[val].append(int(np.sum(labels == val)))
        all_label_arrays.append(labels)

        # Check for anomalies
        if n_samples != EXPECTED_TOTAL_SAMPLES:
            anomalies.append(
                f"  SAMPLE COUNT MISMATCH [{rec['recording_id']}]: "
                f"expected {EXPECTED_TOTAL_SAMPLES:,}, got {n_samples:,}"
            )
        if n_epochs != EXPECTED_EPOCH_COUNT:
            anomalies.append(
                f"  EPOCH COUNT MISMATCH [{rec['recording_id']}]: "
                f"expected {EXPECTED_EPOCH_COUNT:,}, got {n_epochs:,}"
            )
        unexpected_labels = [v for v in unique_vals if v not in LABEL_ENCODING]
        if unexpected_labels:
            anomalies.append(
                f"  UNEXPECTED LABEL VALUES [{rec['recording_id']}]: {unexpected_labels}"
            )

        status = "OK"
        if n_samples != EXPECTED_TOTAL_SAMPLES or n_epochs != EXPECTED_EPOCH_COUNT or unexpected_labels:
            status = "ANOMALY"

        print(
            f"  [{i+1:02d}/{total_recordings}] {rec['recording_id']:<22}  "
            f"samples={n_samples:>9,}  epochs={n_epochs:>6,}  "
            f"labels={unique_vals}  {status}"
        )

    print()

    # ------------------------------------------------------------------
    # 5. Label distribution across entire dataset
    # ------------------------------------------------------------------
    print("-" * 70)
    print("LABEL DISTRIBUTION (ALL RECORDINGS COMBINED)")
    print("-" * 70)

    if all_label_arrays:
        all_labels_combined = np.concatenate(all_label_arrays)
        total_epochs = len(all_labels_combined)
        print(f"  Total epochs across all recordings: {total_epochs:,}")
        print()
        for val, name in sorted(LABEL_ENCODING.items()):
            count = int(np.sum(all_labels_combined == val))
            pct = 100.0 * count / total_epochs
            print(f"    {val} = {name:<5}: {count:>8,} epochs  ({pct:6.2f}%)")
        print()

    # ------------------------------------------------------------------
    # 6. Minimum per-recording counts (calibration feasibility check)
    # ------------------------------------------------------------------
    print("-" * 70)
    print("PER-RECORDING LABEL COUNTS — MINIMUM ACROSS ALL RECORDINGS")
    print("-" * 70)
    print(f"  (Phase 3 requires at least {MIN_CALIBRATION_EPOCHS} epochs per stage per recording)")
    print()

    calibration_feasible = True
    for val, name in sorted(LABEL_ENCODING.items()):
        counts = all_label_counts[val]
        if counts:
            min_count = min(counts)
            min_rec = recordings[counts.index(min_count)]["recording_id"]
            max_count = max(counts)
            mean_count = float(np.mean(counts))
            feasible = min_count >= MIN_CALIBRATION_EPOCHS
            if not feasible:
                calibration_feasible = False
            flag = "OK" if feasible else "INSUFFICIENT"
            print(
                f"    {val} = {name:<5}: min={min_count:>5,} ({min_rec})  "
                f"max={max_count:>5,}  mean={mean_count:>7.1f}  [{flag}]"
            )

    print()
    print(
        f"  Calibration feasibility (120 epochs/stage): "
        f"{'FEASIBLE for all recordings' if calibration_feasible else 'INFEASIBLE — see above'}"
    )
    print()

    # ------------------------------------------------------------------
    # 7. Anomalies
    # ------------------------------------------------------------------
    print("-" * 70)
    print("ANOMALIES")
    print("-" * 70)
    if anomalies:
        for a in anomalies:
            print(a)
    else:
        print("  None detected.")
    print()

    # ------------------------------------------------------------------
    # 8. Summary
    # ------------------------------------------------------------------
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)
    mice = sorted({r["mouse_id"] for r in recordings})
    print(f"  Animals (mice): {len(mice)}  —  {', '.join(mice)}")
    print(f"  Total recordings: {total_recordings}")
    print(
        f"  Recordings per mouse: {total_recordings // len(mice) if mice else 'N/A'}"
    )
    print(f"  Signal shape: ({EXPECTED_TOTAL_SAMPLES:,},) samples  "
          f"[{EXPECTED_RECORDING_DURATION_H}h × 3600s × {EXPECTED_SAMPLING_RATE_HZ} Hz]")
    print(f"  Epochs per recording: {EXPECTED_EPOCH_COUNT:,}  "
          f"[{EXPECTED_RECORDING_DURATION_H}h × 3600s / {EXPECTED_EPOCH_LENGTH_S}s]")
    print(f"  Label encoding confirmed: REM=1, Wake=2, NREM=3")
    print()

    # ------------------------------------------------------------------
    # 9. Loading code example
    # ------------------------------------------------------------------
    print("-" * 70)
    print("LOADING CODE EXAMPLE (template for all subsequent scripts)")
    print("-" * 70)
    print("""
    from scripts.utils.data_loading import find_all_recordings, load_eeg_emg, load_expert_labels

    recordings = find_all_recordings(data_dir)

    for rec in recordings:
        eeg, emg = load_eeg_emg(rec["recording_path"])
        labels   = load_expert_labels(rec["label_path"])
        # eeg  : shape (7372800,), dtype float64
        # emg  : shape (7372800,), dtype float64
        # labels: shape (5760,),   dtype int64
    """)

    print("=" * 70)
    print("Inspection complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
