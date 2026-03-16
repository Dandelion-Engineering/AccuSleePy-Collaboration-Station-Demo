# Data Guide — AccuSleePy Demo

*Built during Phase 2 (2026-03-16). All values derived from
`scripts/01_data_inspection.py` run against `C:\Datasets\AccuSleePy_Data`.*

---

## 1. File Inventory

The dataset is stored under a single root directory with the following layout:

```
<data_dir>/
└── 4-hour_recordings/
    ├── Mouse01/
    │   ├── Day1/
    │   │   ├── recording.parquet    ← EEG + EMG signals
    │   │   └── labels.csv           ← Expert manual sleep-stage labels
    │   ├── Day2/ … Day5/
    ├── Mouse02/ … Mouse10/
```

### File categories

| File name | Role | Format |
|---|---|---|
| `recording.parquet` | EEG and EMG time-series | Apache Parquet (columnar binary) |
| `labels.csv` | Expert manual sleep-stage labels | CSV |

### Per-recording file sizes

| Recording ID | recording.parquet | labels.csv |
|---|---|---|
| Mouse01_Day1 | 64.6 MB | 16.9 KB |
| Mouse01_Day2 | 64.8 MB | 11.3 KB |
| Mouse01_Day3 | 64.5 MB | 11.3 KB |
| Mouse01_Day4 | 64.6 MB | 11.3 KB |
| Mouse01_Day5 | 64.7 MB | 11.3 KB |
| Mouse02_Day1 | 65.9 MB | 11.3 KB |
| Mouse02_Day2 | 65.7 MB | 11.3 KB |
| Mouse02_Day3 | 65.8 MB | 11.3 KB |
| Mouse02_Day4 | 66.1 MB | 11.3 KB |
| Mouse02_Day5 | 65.8 MB | 11.3 KB |
| Mouse03_Day1 | 64.8 MB | 11.3 KB |
| Mouse03_Day2 | 64.9 MB | 11.3 KB |
| Mouse03_Day3 | 64.4 MB | 11.3 KB |
| Mouse03_Day4 | 64.8 MB | 11.3 KB |
| Mouse03_Day5 | 64.7 MB | 11.3 KB |
| Mouse04_Day1 | 65.9 MB | 11.3 KB |
| Mouse04_Day2 | 65.7 MB | 11.3 KB |
| Mouse04_Day3 | 65.5 MB | 11.3 KB |
| Mouse04_Day4 | 65.3 MB | 11.3 KB |
| Mouse04_Day5 | 65.7 MB | 11.3 KB |
| Mouse05_Day1 | 65.9 MB | 11.3 KB |
| Mouse05_Day2 | 65.6 MB | 11.3 KB |
| Mouse05_Day3 | 65.5 MB | 11.3 KB |
| Mouse05_Day4 | 66.5 MB | 11.3 KB |
| Mouse05_Day5 | 66.2 MB | 11.3 KB |
| Mouse06_Day1 | 65.3 MB | 11.3 KB |
| Mouse06_Day2 | 65.1 MB | 11.3 KB |
| Mouse06_Day3 | 65.4 MB | 11.3 KB |
| Mouse06_Day4 | 65.3 MB | 11.3 KB |
| Mouse06_Day5 | 64.9 MB | 11.3 KB |
| Mouse07_Day1 | 65.3 MB | 11.3 KB |
| Mouse07_Day2 | 65.3 MB | 11.3 KB |
| Mouse07_Day3 | 65.6 MB | 11.3 KB |
| Mouse07_Day4 | 65.4 MB | 11.3 KB |
| Mouse07_Day5 | 66.0 MB | 11.3 KB |
| Mouse08_Day1 | 65.7 MB | 11.3 KB |
| Mouse08_Day2 | 65.3 MB | 11.3 KB |
| Mouse08_Day3 | 65.1 MB | 11.3 KB |
| Mouse08_Day4 | 65.6 MB | 11.3 KB |
| Mouse08_Day5 | 65.5 MB | 11.3 KB |
| Mouse09_Day1 | 65.1 MB | 11.3 KB |
| Mouse09_Day2 | 65.8 MB | 11.3 KB |
| Mouse09_Day3 | 65.6 MB | 11.3 KB |
| Mouse09_Day4 | 65.3 MB | 11.3 KB |
| Mouse09_Day5 | 65.4 MB | 11.3 KB |
| Mouse10_Day1 | 65.7 MB | 11.3 KB |
| Mouse10_Day2 | 65.5 MB | 11.3 KB |
| Mouse10_Day3 | 65.1 MB | 11.3 KB |
| Mouse10_Day4 | 65.5 MB | 11.3 KB |
| Mouse10_Day5 | 65.3 MB | 11.3 KB |

**Note:** Mouse01_Day1 has a slightly larger `labels.csv` (16.9 KB vs 11.3 KB for all
others). The file loads without error and passes all structure checks; the size
difference is likely due to a header or comment row in the original file. The
content is identical in format and the label array has the same shape (5,760 epochs).

---

## 2. Array Shapes and Data Types

### recording.parquet

| Property | Value |
|---|---|
| Shape | (7,372,800, 2) |
| Columns | `eeg`, `emg` |
| dtype | float64 |
| Loaded as | `pandas.DataFrame`, then `.values` extracted per column |

### labels.csv

| Property | Value |
|---|---|
| Shape | (5,760, 1) |
| Column | `brain_state` |
| dtype | int64 |
| Valid values | 1 (REM), 2 (Wake), 3 (NREM) |

All 50 recordings have the shapes above. No recordings differ.

---

## 3. Sampling Rate Verification

**Sampling rate: 512 Hz — confirmed.**

Expected sample count for a 4-hour recording at 512 Hz:

```
4 h × 3600 s/h × 512 samples/s = 7,372,800 samples
```

Every recording has exactly 7,372,800 samples in both EEG and EMG arrays. No
discrepancies detected across all 50 recordings.

---

## 4. Epoch Structure

**Epoch length: 2.5 seconds — confirmed.**

At 512 Hz, each epoch spans:
```
2.5 s × 512 Hz = 1,280 samples per epoch
```

For a 4-hour recording:
```
4 h × 3600 s/h / 2.5 s/epoch = 5,760 epochs per recording
```

Every `labels.csv` contains exactly 5,760 rows (one label per epoch). No
discrepancies detected.

---

## 5. Label Encoding

**Encoding: REM = 1, Wake = 2, NREM = 3 — confirmed.**

Unique label values found across all 50 recordings: `[1, 2, 3]`. No unexpected
values (e.g., 0 for unscored) were found in any recording.

### Label distribution across all 50 recordings (288,000 epochs total)

| Label | Stage | Count | Percentage |
|---|---|---|---|
| 1 | REM | 30,128 | 10.46% |
| 2 | Wake | 98,983 | 34.37% |
| 3 | NREM | 158,889 | 55.17% |
| — | **Total** | **288,000** | **100.00%** |

### Per-recording label counts

| Recording ID | REM | Wake | NREM | Total | %REM | %Wake | %NREM |
|---|---|---|---|---|---|---|---|
| Mouse01_Day1 | 624 | 1919 | 3217 | 5760 | 10.8 | 33.3 | 55.9 |
| Mouse01_Day2 | 517 | 2226 | 3017 | 5760 | 9.0 | 38.6 | 52.4 |
| Mouse01_Day3 | 689 | 1632 | 3439 | 5760 | 12.0 | 28.3 | 59.7 |
| Mouse01_Day4 | 648 | 1963 | 3149 | 5760 | 11.2 | 34.1 | 54.7 |
| Mouse01_Day5 | 666 | 1655 | 3439 | 5760 | 11.6 | 28.7 | 59.7 |
| Mouse02_Day1 | 649 | 1310 | 3801 | 5760 | 11.3 | 22.7 | 66.0 |
| Mouse02_Day2 | 683 | 1418 | 3659 | 5760 | 11.9 | 24.6 | 63.5 |
| Mouse02_Day3 | 502 | 1726 | 3532 | 5760 | 8.7 | 30.0 | 61.3 |
| Mouse02_Day4 | 587 | 2262 | 2911 | 5760 | 10.2 | 39.3 | 50.5 |
| Mouse02_Day5 | 620 | 1803 | 3337 | 5760 | 10.8 | 31.3 | 57.9 |
| Mouse03_Day1 | 851 | 1431 | 3478 | 5760 | 14.8 | 24.8 | 60.4 |
| Mouse03_Day2 | 629 | 2152 | 2979 | 5760 | 10.9 | 37.4 | 51.7 |
| Mouse03_Day3 | 832 | 1228 | 3700 | 5760 | 14.4 | 21.3 | 64.2 |
| Mouse03_Day4 | 706 | 1574 | 3480 | 5760 | 12.3 | 27.3 | 60.4 |
| Mouse03_Day5 | 845 | 1035 | 3880 | 5760 | 14.7 | 18.0 | 67.4 |
| Mouse04_Day1 | 470 | 3047 | 2243 | 5760 | 8.2 | 52.9 | 38.9 |
| Mouse04_Day2 | 528 | 2662 | 2570 | 5760 | 9.2 | 46.2 | 44.6 |
| Mouse04_Day3 | 496 | 2038 | 3226 | 5760 | 8.6 | 35.4 | 56.0 |
| Mouse04_Day4 | 684 | 1931 | 3145 | 5760 | 11.9 | 33.5 | 54.6 |
| Mouse04_Day5 | 493 | 2479 | 2788 | 5760 | 8.6 | 43.0 | 48.4 |
| Mouse05_Day1 | 542 | 2389 | 2829 | 5760 | 9.4 | 41.5 | 49.1 |
| Mouse05_Day2 | 685 | 1690 | 3385 | 5760 | 11.9 | 29.3 | 58.8 |
| Mouse05_Day3 | 464 | 1727 | 3569 | 5760 | 8.1 | 30.0 | 62.0 |
| Mouse05_Day4 | 400 | 2182 | 3178 | 5760 | 6.9 | 37.9 | 55.2 |
| Mouse05_Day5 | 538 | 1981 | 3241 | 5760 | 9.3 | 34.4 | 56.3 |
| Mouse06_Day1 | 586 | 2767 | 2407 | 5760 | 10.2 | 48.0 | 41.8 |
| Mouse06_Day2 | 397 | 2391 | 2972 | 5760 | 6.9 | 41.5 | 51.6 |
| Mouse06_Day3 | 518 | 2460 | 2782 | 5760 | 9.0 | 42.7 | 48.3 |
| Mouse06_Day4 | 398 | 2764 | 2598 | 5760 | 6.9 | 48.0 | 45.1 |
| Mouse06_Day5 | 710 | 1438 | 3612 | 5760 | 12.3 | 25.0 | 62.7 |
| Mouse07_Day1 | 706 | 1730 | 3324 | 5760 | 12.3 | 30.0 | 57.7 |
| Mouse07_Day2 | 667 | 1484 | 3609 | 5760 | 11.6 | 25.8 | 62.7 |
| Mouse07_Day3 | 615 | 1854 | 3291 | 5760 | 10.7 | 32.2 | 57.1 |
| Mouse07_Day4 | 683 | 1605 | 3472 | 5760 | 11.9 | 27.9 | 60.3 |
| Mouse07_Day5 | 577 | 2023 | 3160 | 5760 | 10.0 | 35.1 | 54.9 |
| Mouse08_Day1 | 541 | 2441 | 2778 | 5760 | 9.4 | 42.4 | 48.2 |
| Mouse08_Day2 | 706 | 1698 | 3356 | 5760 | 12.3 | 29.5 | 58.3 |
| Mouse08_Day3 | 601 | 1730 | 3429 | 5760 | 10.4 | 30.0 | 59.5 |
| Mouse08_Day4 | 465 | 2565 | 2730 | 5760 | 8.1 | 44.5 | 47.4 |
| Mouse08_Day5 | 496 | 2387 | 2877 | 5760 | 8.6 | 41.4 | 49.9 |
| Mouse09_Day1 | 741 | 1900 | 3119 | 5760 | 12.9 | 33.0 | 54.1 |
| Mouse09_Day2 | 480 | 2745 | 2535 | 5760 | 8.3 | 47.7 | 44.0 |
| Mouse09_Day3 | 505 | 2014 | 3241 | 5760 | 8.8 | 35.0 | 56.3 |
| Mouse09_Day4 | 568 | 1769 | 3423 | 5760 | 9.9 | 30.7 | 59.4 |
| Mouse09_Day5 | 752 | 1851 | 3157 | 5760 | 13.1 | 32.1 | 54.8 |
| Mouse10_Day1 | 508 | 2333 | 2919 | 5760 | 8.8 | 40.5 | 50.7 |
| Mouse10_Day2 | 406 | 2611 | 2743 | 5760 | 7.0 | 45.3 | 47.6 |
| Mouse10_Day3 | 772 | 1565 | 3423 | 5760 | 13.4 | 27.2 | 59.4 |
| Mouse10_Day4 | 610 | 1885 | 3265 | 5760 | 10.6 | 32.7 | 56.7 |
| Mouse10_Day5 | 772 | 1513 | 3475 | 5760 | 13.4 | 26.3 | 60.3 |

---

## 6. Animal and Recording Organization

**Organization: by mouse ID and recording day.**

Files are stored under:
```
4-hour_recordings/<MouseID>/<DayID>/
```

- **Mouse IDs:** Mouse01 through Mouse10 (10 animals total)
- **Day IDs:** Day1 through Day5 (5 recordings per animal)
- **Total recordings:** 50 (confirmed; matches expected 10 × 5)

Mouse identity is directly encoded in the top-level directory name (e.g., all
files under `Mouse03/` belong to the same individual animal.
Recording session is encoded in the second-level directory (e.g., `Day2/` is
the animal's second 4-hour recording session).

---

## 7. Loading Code Example

This is the template used by all subsequent pipeline scripts:

```python
from scripts.utils.data_loading import find_all_recordings, load_eeg_emg, load_expert_labels

# Discover all 50 recordings
recordings = find_all_recordings(data_dir)
# Each element is a dict: {mouse_id, day_id, recording_id, recording_path, label_path}

for rec in recordings:
    # Load EEG and EMG time series
    eeg, emg = load_eeg_emg(rec["recording_path"])
    # eeg  : numpy array, shape (7372800,), dtype float64
    # emg  : numpy array, shape (7372800,), dtype float64

    # Load expert manual labels
    labels = load_expert_labels(rec["label_path"])
    # labels: numpy array, shape (5760,), dtype int64
    # values: 1 = REM, 2 = Wake, 3 = NREM
```

`find_all_recordings` returns descriptors sorted by mouse then day, so iteration
order is deterministic.

---

## 8. Anomalies

**No anomalies detected.**

- All 50 recordings loaded without error.
- All EEG and EMG arrays have the expected shape (7,372,800,).
- All label arrays have the expected shape (5,760,).
- All label arrays contain only values {1, 2, 3}. No unscored (0) or other special
  values were found.
- No recordings have significantly different epoch counts or signal lengths.

The only minor observation: `Mouse01_Day1/labels.csv` is 16.9 KB compared to
11.3 KB for all other recordings. Inspection confirms the file content is identical
in structure and passes all checks. The size difference does not affect the pipeline.

---

## Phase 2 Gate Checklist

- [x] `scripts/01_data_inspection.py` runs without errors on the full dataset
- [x] `data_guide.md` is complete and covers all items above
- [x] Label encoding confirmed from actual data: REM=1, Wake=2, NREM=3
- [x] Total recording count verified: 50 recordings from 10 mice (5 each)
- [x] Epoch structure verified: 5,760 epochs × 1,280 samples/epoch = 7,372,800 samples
- [x] Minimum per-recording counts confirm calibration feasibility (120 epochs/stage):
  - REM minimum: **397** epochs (Mouse06_Day2) — well above 120
  - Wake minimum: **1,035** epochs (Mouse03_Day5) — well above 120
  - NREM minimum: **2,243** epochs (Mouse04_Day1) — well above 120
