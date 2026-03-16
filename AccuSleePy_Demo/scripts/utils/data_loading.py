"""Shared data loading utilities for the AccuSleePy Demo pipeline.

All functions are pure I/O helpers: they locate, read, and return data
without any processing or side effects.  Every subsequent script in the
pipeline imports from this module so that loading logic is defined once.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
from accusleepy.fileio import load_recording as _accusleepy_load_recording
from accusleepy.fileio import load_labels as _accusleepy_load_labels


# ---------------------------------------------------------------------------
# Dataset structure helpers
# ---------------------------------------------------------------------------

def find_all_recordings(data_dir: str) -> list[dict]:
    """Return a sorted list of all recording descriptors found under data_dir.

    The expected directory layout is::

        <data_dir>/
        └── 4-hour_recordings/
            └── MouseXX/
                └── DayX/
                    ├── recording.parquet
                    └── labels.csv

    Each descriptor is a dict with keys:
        - ``mouse_id``  (str)  – e.g. ``"Mouse01"``
        - ``day_id``    (str)  – e.g. ``"Day1"``
        - ``recording_id`` (str) – e.g. ``"Mouse01_Day1"``
        - ``recording_path`` (str) – absolute path to ``recording.parquet``
        - ``label_path``     (str) – absolute path to ``labels.csv``

    :param data_dir: root directory of the AccuSleePy dataset
    :return: list of recording descriptor dicts, sorted by mouse then day
    :raises FileNotFoundError: if the expected subdirectory structure is absent
    """
    recordings_root = os.path.join(data_dir, "4-hour_recordings")
    if not os.path.isdir(recordings_root):
        raise FileNotFoundError(
            f"Expected '4-hour_recordings' subdirectory not found in: {data_dir}"
        )

    records = []
    for mouse_dir in sorted(Path(recordings_root).iterdir()):
        if not mouse_dir.is_dir():
            continue
        mouse_id = mouse_dir.name
        for day_dir in sorted(mouse_dir.iterdir()):
            if not day_dir.is_dir():
                continue
            day_id = day_dir.name
            rec_path = day_dir / "recording.parquet"
            lbl_path = day_dir / "labels.csv"
            if rec_path.exists() and lbl_path.exists():
                records.append(
                    {
                        "mouse_id": mouse_id,
                        "day_id": day_id,
                        "recording_id": f"{mouse_id}_{day_id}",
                        "recording_path": str(rec_path),
                        "label_path": str(lbl_path),
                    }
                )
    return records


# ---------------------------------------------------------------------------
# Signal loading
# ---------------------------------------------------------------------------

def load_eeg_emg(recording_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Load EEG and EMG time-series arrays from a recording file.

    Delegates to ``accusleepy.fileio.load_recording`` so all downstream
    scripts use the same loading path as AccuSleePy internally.

    :param recording_path: path to a ``.parquet`` (or ``.csv``) recording file
    :return: tuple of (eeg, emg) as 1-D float64 numpy arrays
    """
    return _accusleepy_load_recording(recording_path)


# ---------------------------------------------------------------------------
# Label loading
# ---------------------------------------------------------------------------

def load_expert_labels(label_path: str) -> np.ndarray:
    """Load expert manual sleep-stage labels from a CSV file.

    Returns only the label array (confidence scores are not present in
    expert-label files).

    :param label_path: path to a ``labels.csv`` file with a ``brain_state``
        column; values are integers 1 (REM), 2 (Wake), or 3 (NREM)
    :return: 1-D int64 numpy array of epoch labels
    """
    labels, _ = _accusleepy_load_labels(label_path)
    return labels


def load_predicted_labels(label_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Load AccuSleePy predicted labels and confidence scores from a CSV file.

    :param label_path: path to a predicted-label CSV produced by
        ``02_accusleepy_scoring.py``; must contain ``brain_state`` and
        ``confidence_score`` columns
    :return: tuple of (labels, confidence_scores) as 1-D numpy arrays
    :raises ValueError: if the file does not contain a ``confidence_score``
        column
    """
    labels, conf = _accusleepy_load_labels(label_path)
    if conf is None:
        raise ValueError(
            f"No confidence_score column found in predicted label file: {label_path}"
        )
    return labels, conf


def load_calibration_indices(indices_path: str) -> np.ndarray:
    """Load the calibration epoch indices saved during Phase 3 scoring.

    :param indices_path: path to a ``_calibration_indices.csv`` file with a
        single ``epoch_index`` column
    :return: 1-D int64 numpy array of calibration epoch indices
    """
    df = pd.read_csv(indices_path)
    return df["epoch_index"].values.astype(np.int64)
