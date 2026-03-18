# AccuSleePy Demo

Automated sleep staging of a publicly available rodent EEG/EMG dataset using
[AccuSleePy](https://github.com/zekebarger/AccuSleePy). This package contains
all scripts, outputs, figures, and a written report needed to understand and
reproduce the full analysis.

---

## What You Need Before You Start

Before running the pipeline, you need two things that are **not included** in
this package:

1. **The dataset** — Download it from the Open Science Framework:
   <https://osf.io/py5eb/>
   Save it somewhere on your computer. You will use that folder path when
   running the scripts. In this guide we use the example path:
   - Windows: `C:\path\to\your\AccuSleePy_dataset`
   - Mac/Linux: `/path/to/your/AccuSleePy_dataset`

2. **The pre-trained model file** — The file is named `ssann_2(5)s.pth`.
   It is available in the same OSF repository. Download it and save it
   somewhere on your computer. In this guide we use the example path:
   - Windows: `C:\path\to\ssann_2(5)s.pth`
   - Mac/Linux: `/path/to/ssann_2(5)s.pth`

> **Tip:** Keep a note of where you saved these two items — you will need
> their paths several times below.

---

## Dataset

**Source:** Barger, Z., Frye, C. G., Liu, D., Dan, Y., & Bouchard, K. E. (2019).
Robust, automated sleep scoring by a compact neural network with distributional
shift correction. *PLOS ONE*, 14(12), 1–18.
<https://doi.org/10.1371/journal.pone.0224642>

**OSF repository:** <https://osf.io/py5eb/>

10 C57BL/6 mice × 5 four-hour daytime recordings = 50 recordings, 288,000
epochs total. EEG and EMG sampled at 512 Hz; epoch length 2.5 s.

---

## Environment Setup

This project requires **Python 3.11**. If you do not have Python installed,
download it from <https://www.python.org/downloads/>.

All commands below are run in a **terminal**:
- **Windows:** Press `Win + R`, type `cmd`, and press Enter.
- **Mac:** Open the **Terminal** app (find it in Applications → Utilities).

### Step 1 — Open a terminal and navigate to this folder

Replace the path below with the actual location of the `AccuSleePy_Demo`
folder on your computer.

**Windows:**
```cmd
cd C:\path\to\AccuSleePy_Demo
```

**Mac/Linux:**
```bash
cd /path/to/AccuSleePy_Demo
```

### Step 2 — Create a virtual environment

A virtual environment keeps all the packages for this project separate from
the rest of your system. Run this once:

**Windows:**
```cmd
python -m venv venv
```

**Mac/Linux:**
```bash
python3 -m venv venv
```

### Step 3 — Activate the virtual environment

You need to activate the environment **every time** you open a new terminal
to work on this project.

**Windows:**
```cmd
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

When activation succeeds, you will see `(venv)` at the start of your
terminal prompt.

### Step 4 — Install the required packages

```
pip install -r requirements.txt
```

This downloads and installs all the Python packages the scripts need.
It may take a few minutes. You only need to do this once.

---

## Setting Up Convenience Variables

Typing long file paths repeatedly is tedious and error-prone. You can save
your paths as short-hand variables and reuse them throughout the session.

> **Important:** These variables only last for the current terminal session.
> If you close the terminal and reopen it, you will need to set them again
> (and re-activate the virtual environment).

Replace the example paths below with your actual paths.

**Windows (Command Prompt):**
```cmd
set DATA_DIR=C:\path\to\your\AccuSleePy_dataset
set MODEL_PATH=C:\path\to\ssann_2(5)s.pth
set DEMO_DIR=C:\path\to\AccuSleePy_Demo
```

**Mac/Linux (Terminal):**
```bash
export DATA_DIR=/path/to/your/AccuSleePy_dataset
export MODEL_PATH=/path/to/ssann_2(5)s.pth
export DEMO_DIR=/path/to/AccuSleePy_Demo
```

Once set, every script command in this guide that uses `%DATA_DIR%` (Windows)
or `$DATA_DIR` (Mac/Linux) will automatically use your actual path.

---

## Running the Pipeline

Run the six scripts **in order**. Each one builds on the outputs of the
previous step.

> All commands assume you are in the `AccuSleePy_Demo` folder with the
> virtual environment activated and convenience variables set.

---

### Step 1 — Data Inspection

Loads and summarises all 50 recordings. Run this first to confirm your
dataset is set up correctly.

**Windows:**
```cmd
python scripts\01_data_inspection.py --data_dir %DATA_DIR% --output_dir outputs
```

**Mac/Linux:**
```bash
python scripts/01_data_inspection.py --data_dir $DATA_DIR --output_dir outputs
```

**Expected output:**
- A summary of all 50 recordings printed to the terminal
- `outputs/data_info.txt` — a saved copy of that summary

---

### Step 2 — AccuSleePy Scoring

Runs the sleep staging model on all 50 recordings. This step takes the
longest — expect **10–20 minutes**.

**Windows:**
```cmd
python scripts\02_accusleepy_scoring.py ^
  --data_dir %DATA_DIR% ^
  --model_path %MODEL_PATH% ^
  --output_dir %DEMO_DIR%\outputs\predicted_labels
```

**Mac/Linux:**
```bash
python scripts/02_accusleepy_scoring.py \
  --data_dir $DATA_DIR \
  --model_path $MODEL_PATH \
  --output_dir $DEMO_DIR/outputs/predicted_labels
```

**Expected output (100 files):**
- `outputs/predicted_labels/<recording_id>.csv` — predicted sleep stage and
  confidence score for each of the 5,760 epochs per recording
- `outputs/predicted_labels/<recording_id>_calibration_indices.csv` — the
  360 calibration epoch indices used for that recording

---

### Step 3 — Quality Control

Checks each recording for unusual stage proportions or long unbroken runs,
and lists any low-confidence epochs.

**Windows:**
```cmd
python scripts\03_quality_control.py ^
  --predicted_labels_dir %DEMO_DIR%\outputs\predicted_labels ^
  --output_dir %DEMO_DIR%
```

**Mac/Linux:**
```bash
python scripts/03_quality_control.py \
  --predicted_labels_dir $DEMO_DIR/outputs/predicted_labels \
  --output_dir $DEMO_DIR
```

**Expected output:**
- `QC_report.md` — quality control flags summary
- `low_confidence_epochs/<recording_id>_low_confidence.csv` (50 files) —
  per-recording list of epochs with confidence score ≤ 0.8

---

### Step 4 — Validation Against Expert Labels

Compares AccuSleePy's predictions to the expert manual labels to confirm
the pipeline is working correctly.

**Windows:**
```cmd
python scripts\04_validation.py ^
  --data_dir %DATA_DIR% ^
  --predicted_labels_dir %DEMO_DIR%\outputs\predicted_labels ^
  --output_path %DEMO_DIR%\outputs\validation_summary.csv
```

**Mac/Linux:**
```bash
python scripts/04_validation.py \
  --data_dir $DATA_DIR \
  --predicted_labels_dir $DEMO_DIR/outputs/predicted_labels \
  --output_path $DEMO_DIR/outputs/validation_summary.csv
```

**Expected output:**
- `outputs/validation_summary.csv` — per-recording Cohen's kappa, accuracy,
  and per-class precision/recall/F1
- Terminal: mean ± SD kappa and accuracy across all 50 recordings

---

### Step 5 — Descriptive Sleep Metrics

Computes stage proportions, bout statistics, and state transition
probabilities for all recordings.

**Windows:**
```cmd
python scripts\05_sleep_metrics.py ^
  --predicted_labels_dir %DEMO_DIR%\outputs\predicted_labels ^
  --output_path %DEMO_DIR%\outputs\sleep_metrics.csv
```

**Mac/Linux:**
```bash
python scripts/05_sleep_metrics.py \
  --predicted_labels_dir $DEMO_DIR/outputs/predicted_labels \
  --output_path $DEMO_DIR/outputs/sleep_metrics.csv
```

**Expected output:**
- `outputs/sleep_metrics.csv` — 50 rows × 26 columns of sleep architecture
  metrics per recording

---

### Step 6 — Figure Generation

Produces all publication-quality figures from the outputs of Steps 4 and 5.

**Windows:**
```cmd
python scripts\06_figures.py ^
  --sleep_metrics_csv %DEMO_DIR%\outputs\sleep_metrics.csv ^
  --validation_csv %DEMO_DIR%\outputs\validation_summary.csv ^
  --predicted_labels_dir %DEMO_DIR%\outputs\predicted_labels ^
  --output_dir %DEMO_DIR%\figures
```

**Mac/Linux:**
```bash
python scripts/06_figures.py \
  --sleep_metrics_csv $DEMO_DIR/outputs/sleep_metrics.csv \
  --validation_csv $DEMO_DIR/outputs/validation_summary.csv \
  --predicted_labels_dir $DEMO_DIR/outputs/predicted_labels \
  --output_dir $DEMO_DIR/figures
```

**Expected output (11 PNG files at 300 DPI):**

| File | Description |
|------|-------------|
| `figures/hypnograms/Mouse01_Day1_hypnogram.png` | Hypnogram for Mouse01, Day1 |
| `figures/hypnograms/Mouse02_Day1_hypnogram.png` | Hypnogram for Mouse02, Day1 |
| `figures/hypnograms/Mouse03_Day1_hypnogram.png` | Hypnogram for Mouse03, Day1 |
| `figures/hypnograms/Mouse04_Day1_hypnogram.png` | Hypnogram for Mouse04, Day1 |
| `figures/hypnograms/Mouse05_Day1_hypnogram.png` | Hypnogram for Mouse05, Day1 |
| `figures/hypnograms/Mouse06_Day1_hypnogram.png` | Hypnogram for Mouse06, Day1 |
| `figures/stage_percentages/stage_percentages.png` | Group-level % Wake / NREM / REM |
| `figures/bout_analysis/bout_duration.png` | Mean bout duration by stage |
| `figures/validation/confusion_matrix.png` | Aggregate 3×3 confusion matrix |
| `figures/validation/kappa_distribution.png` | Per-recording kappa distribution |
| `figures/transitions/transition_matrix.png` | Mean state transition heatmap |

---

## Folder Structure

```
AccuSleePy_Demo/
├── README.md                         ← This file
├── requirements.txt                  ← Pinned Python dependencies
├── .gitignore                        ← Excludes __pycache__, *.pyc, .DS_Store
├── data_guide.md                     ← Authoritative dataset reference
├── QC_report.md                      ← Quality control flags
├── scripts/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_loading.py           ← EEG/EMG/label loading functions
│   │   ├── metrics.py                ← Cohen's kappa, F1, accuracy, confusion matrix
│   │   └── plotting.py               ← Shared figure utilities and stage colors
│   ├── 01_data_inspection.py         ← Dataset summary and verification
│   ├── 02_accusleepy_scoring.py      ← AccuSleePy scoring for all 50 recordings
│   ├── 03_quality_control.py         ← Stage proportion and confidence QC
│   ├── 04_validation.py              ← Validation against expert labels
│   ├── 05_sleep_metrics.py           ← Descriptive sleep architecture metrics
│   └── 06_figures.py                 ← Publication-quality figure generation
├── outputs/
│   ├── data_info.txt                 ← Dataset inspection report
│   ├── predicted_labels/             ← 50 scoring CSVs + 50 calibration index CSVs
│   ├── sleep_metrics.csv             ← Per-recording sleep architecture metrics
│   └── validation_summary.csv        ← Per-recording validation metrics
├── figures/
│   ├── hypnograms/                   ← 6 hypnogram PNGs
│   ├── stage_percentages/            ← Stage proportion summary figure
│   ├── bout_analysis/                ← Bout duration figure
│   ├── validation/                   ← Confusion matrix and kappa distribution
│   └── transitions/                  ← Transition matrix heatmap
├── low_confidence_epochs/            ← 50 per-recording low-confidence CSVs
└── report/
    ├── report.tex                    ← LaTeX source
    └── report.pdf                    ← Compiled final report
```

---

## Key Results

| Metric | Value |
|--------|-------|
| Mean Cohen's kappa | 0.9490 ± 0.0148 |
| Mean accuracy | 97.25 ± 0.72% |
| Wake F1 | 0.9623 |
| NREM F1 | 0.9763 |
| REM F1 | 0.9754 |
| Mean % Wake | 34.53 ± 5.16% (across 10 animals) |
| Mean % NREM | 54.64 ± 4.00% (across 10 animals) |
| Mean % REM | 10.83 ± 1.37% (across 10 animals) |
| Recordings flagged in QC | 0 / 50 |
| Total low-confidence epochs | 481 / 288,000 (0.167%) |

---

## Citation

If you use this analysis or the dataset, please cite:

> Barger, Z., Frye, C. G., Liu, D., Dan, Y., & Bouchard, K. E. (2019).
> Robust, automated sleep scoring by a compact neural network with distributional
> shift correction. *PLOS ONE*, 14(12), 1–18.
> <https://doi.org/10.1371/journal.pone.0224642>

> Barger, Z., & Frye, C. (2025, June 6). AccuSleep. <https://doi.org/10.17605/OSF.IO/PY5EB>
