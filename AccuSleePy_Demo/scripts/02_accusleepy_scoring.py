"""AccuSleePy scoring script for AccuSleePy Demo (Phase 3).

Runs AccuSleePy on all recordings in the dataset using the pre-trained 2.5-second
epoch model.  For each recording, the script:

1. Loads EEG, EMG, and expert label arrays.
2. Selects 120 calibration epochs per sleep stage (360 total) using evenly
   distributed sampling via ``np.linspace``.
3. Calibrates the model to the recording using AccuSleePy's built-in
   distributional shift correction.
4. Scores all epochs of the recording with the calibrated model.
5. Saves the predicted labels and confidence scores to
   ``<output_dir>/<recording_id>.csv`` using AccuSleePy's native ``save_labels``.
6. Saves the calibration epoch indices to
   ``<output_dir>/<recording_id>_calibration_indices.csv`` for use in Phase 4
   validation (calibration epochs are excluded from validation).

AccuSleePy scoring is performed entirely in memory.  No intermediate files are
written to disk during the scoring process; accordingly no cleanup of temporary
files is required.

Usage
-----
::

    python scripts/02_accusleepy_scoring.py \\
        --data_dir C:\\Datasets\\AccuSleePy_Data \\
        --model_path "C:\\Datasets\\models\\ssann_2(5)s.pth" \\
        --output_dir AccuSleePy_Demo/outputs/predicted_labels
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

# Allow importing from scripts/utils when running from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.utils.data_loading import find_all_recordings, load_eeg_emg, load_expert_labels

from accusleepy.models import load_model
from accusleepy.fileio import load_config, save_labels
from accusleepy.signal_processing import create_eeg_emg_image, get_mixture_values
from accusleepy.classification import score_recording


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SAMPLING_RATE = 512          # Hz — confirmed for this dataset
CALIB_EPOCHS_PER_STAGE = 120 # distributed calibration epochs per sleep stage
STAGE_ENCODING = {1: "REM", 2: "Wake", 3: "NREM"}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    :return: parsed namespace with ``data_dir``, ``model_path``, and
        ``output_dir`` attributes
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run AccuSleePy on all recordings in the dataset. "
            "Saves one predicted-label CSV and one calibration-indices CSV "
            "per recording to the output directory."
        )
    )
    parser.add_argument(
        "--data_dir",
        required=True,
        help="Root directory of the AccuSleePy dataset (must contain '4-hour_recordings/').",
    )
    parser.add_argument(
        "--model_path",
        required=True,
        help="Path to the pre-trained AccuSleePy model file (e.g. ssann_2(5)s.pth).",
    )
    parser.add_argument(
        "--output_dir",
        default=os.path.join("AccuSleePy_Demo", "outputs", "predicted_labels"),
        help=(
            "Directory where predicted-label and calibration-index files will be written. "
            "Created automatically if it does not exist. "
            "Default: AccuSleePy_Demo/outputs/predicted_labels"
        ),
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Calibration helpers
# ---------------------------------------------------------------------------

def select_calibration_indices(labels: np.ndarray) -> np.ndarray:
    """Select distributed calibration epoch indices (120 per stage, 360 total).

    For each sleep stage (Wake=2, NREM=3, REM=1), finds all epoch indices
    where that stage occurs and samples 120 of them using evenly spaced
    positions via ``np.linspace``.  This spreads the calibration epochs across
    the full recording rather than concentrating them at a single time point,
    which is important because calibration estimates per-stage feature
    statistics — epochs drawn from different points in the recording capture
    variability across the session.

    :param labels: 1-D int64 array of expert sleep-stage labels (values 1, 2, 3)
    :return: 1-D int64 array of 360 calibration epoch indices (120 per stage)
    :raises ValueError: if any stage has fewer than 120 labeled epochs
    """
    calib_indices = []
    for stage_val, stage_name in STAGE_ENCODING.items():
        stage_idx = np.where(labels == stage_val)[0]
        n_available = len(stage_idx)
        if n_available < CALIB_EPOCHS_PER_STAGE:
            # Report all stage counts so the caller can diagnose the issue
            counts = {name: int(np.sum(labels == val)) for val, name in STAGE_ENCODING.items()}
            raise ValueError(
                f"Stage '{stage_name}' has only {n_available} labeled epochs, "
                f"but {CALIB_EPOCHS_PER_STAGE} are required. "
                f"Per-stage counts for this recording: {counts}"
            )
        sampled_positions = np.linspace(0, n_available - 1, CALIB_EPOCHS_PER_STAGE, dtype=int)
        calib_indices.append(stage_idx[sampled_positions])
    return np.concatenate(calib_indices)


# ---------------------------------------------------------------------------
# Per-recording scoring
# ---------------------------------------------------------------------------

def score_one_recording(
    rec: dict,
    model,
    cfg,
    epoch_length: float,
    epochs_per_img: int,
    output_dir: str,
) -> None:
    """Score a single recording and save outputs to disk.

    Performs calibration using 120 evenly distributed epochs per sleep stage,
    scores all epochs with the calibrated model, then saves:

    - ``<recording_id>.csv`` — predicted labels and confidence scores
      (AccuSleePy native format via ``save_labels``)
    - ``<recording_id>_calibration_indices.csv`` — the 360 calibration epoch
      indices used for this recording, to be excluded during Phase 4 validation

    :param rec: recording descriptor dict from ``find_all_recordings``
    :param model: loaded AccuSleePy SSANN model
    :param cfg: AccuSleePy configuration (``AccuSleePyConfig``)
    :param epoch_length: epoch length in seconds (e.g. 2.5)
    :param epochs_per_img: number of epochs per model input image (e.g. 9)
    :param output_dir: directory where output files will be written
    """
    recording_id = rec["recording_id"]

    # 1. Load signals and expert labels
    eeg, emg = load_eeg_emg(rec["recording_path"])
    labels = load_expert_labels(rec["label_path"])

    # 2. Select calibration indices (120 per stage, distributed)
    calib_indices = select_calibration_indices(labels)

    # 3. Build EEG+EMG spectrogram image (in memory)
    img = create_eeg_emg_image(eeg, emg, SAMPLING_RATE, epoch_length, cfg.emg_filter)

    # 4. Compute mixture values from calibration columns
    #    Labels must be in "class" format (0-indexed) for get_mixture_values
    labels_class = cfg.brain_state_set.convert_digit_to_class(labels)
    mixture_means, mixture_sds = get_mixture_values(
        img[:, calib_indices], labels_class[calib_indices], cfg.brain_state_set
    )

    # 5. Score all epochs with the calibrated model
    pred_labels, conf_scores = score_recording(
        model, eeg, emg, mixture_means, mixture_sds,
        SAMPLING_RATE, epoch_length, epochs_per_img,
        cfg.brain_state_set, cfg.emg_filter,
    )

    # 6. Save predicted labels (AccuSleePy native format: brain_state + confidence_score)
    label_output_path = os.path.join(output_dir, f"{recording_id}.csv")
    save_labels(pred_labels, label_output_path, confidence_scores=conf_scores)

    # 7. Save calibration indices companion file
    indices_output_path = os.path.join(output_dir, f"{recording_id}_calibration_indices.csv")
    pd.DataFrame({"epoch_index": calib_indices}).to_csv(indices_output_path, index=False)

    # 8. Verify predicted labels contain only expected values {1, 2, 3}
    unique_vals = set(pred_labels.tolist())
    if not unique_vals.issubset({1, 2, 3}):
        raise ValueError(
            f"Unexpected label values in {recording_id}: {unique_vals - {1, 2, 3}}"
        )

    # Note: AccuSleePy scoring is performed entirely in memory.
    # No intermediate or temporary files are written to disk during the scoring
    # process; accordingly, no cleanup of temporary files is required.


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run AccuSleePy scoring on all recordings and save outputs."""
    args = parse_args()

    print("=" * 70)
    print("AccuSleePy Scoring — Phase 3")
    print("=" * 70)
    print(f"Data directory : {args.data_dir}")
    print(f"Model path     : {args.model_path}")
    print(f"Output dir     : {args.output_dir}")
    print()

    # Validate input paths
    if not os.path.isdir(args.data_dir):
        raise FileNotFoundError(f"Data directory not found: {args.data_dir}")
    if not os.path.isfile(args.model_path):
        raise FileNotFoundError(f"Model file not found: {args.model_path}")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Discover all recordings
    recordings = find_all_recordings(args.data_dir)
    total = len(recordings)
    print(f"Recordings found: {total}")
    print()

    # Load model and configuration (once, shared across all recordings)
    print("Loading model and configuration...")
    model, epoch_length, epochs_per_img, model_type, brain_states = load_model(args.model_path)
    cfg = load_config()
    print(f"  Model type     : {model_type}")
    print(f"  Epoch length   : {epoch_length} s")
    print(f"  Epochs per img : {epochs_per_img}")
    print(f"  EMG filter     : {cfg.emg_filter}")
    print()

    print(
        f"Calibration method: {CALIB_EPOCHS_PER_STAGE} epochs/stage "
        f"× {len(STAGE_ENCODING)} stages = "
        f"{CALIB_EPOCHS_PER_STAGE * len(STAGE_ENCODING)} total calibration epochs per recording "
        f"(distributed via np.linspace)"
    )
    print()

    # Score all recordings
    failed = []
    for i, rec in enumerate(recordings, start=1):
        recording_id = rec["recording_id"]
        print(f"[{i:02d}/{total}] Scoring {recording_id}...", end=" ", flush=True)
        try:
            score_one_recording(
                rec=rec,
                model=model,
                cfg=cfg,
                epoch_length=epoch_length,
                epochs_per_img=epochs_per_img,
                output_dir=args.output_dir,
            )
            print("done")
        except Exception as exc:
            print(f"FAILED: {exc}")
            failed.append((recording_id, str(exc)))

    print()
    print("=" * 70)
    if failed:
        print(f"Scoring complete with {len(failed)} failure(s):")
        for rec_id, err in failed:
            print(f"  FAILED: {rec_id} — {err}")
        sys.exit(1)
    else:
        print(f"All {total} recordings scored successfully.")
        print(f"Outputs written to: {args.output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
