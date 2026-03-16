# AccuSleePy Demo Project — Project Details

## Project Overview

This project applies the **AccuSleePy** automated sleep staging tool to a publicly available rodent EEG/EMG dataset. The goal is to produce a complete, reproducible sleep staging analysis package: scored sleep data for all recordings, descriptive sleep architecture metrics, validation against expert manual labels, publication-quality figures, and a written methods section.

The dataset comes from a published paper that used AccuSleePy as its scoring tool, making this an end-to-end demonstration of the standard AccuSleePy workflow on well-characterized data.

---

## The Dataset

**Source:** Open Science Framework repository [https://osf.io/py5eb/]

**Associated Paper:** Barger, Z., Frye, C. G., Liu, D., Dan, Y., & Bouchard, K. E. (2019). Robust, automated sleep scoring by a compact neural network with distributional shift correction. PLOS ONE, 14(12), 1–18. [https://doi.org/10.1371/journal.pone.0224642]

**Local data path:** `C:\Datasets\AccuSleePy_Data`

**Basic specifications:**

| Property | Value |
|----------|-------|
| Species | Mouse (C57BL/6) |
| Number of animals | 10 |
| Recordings | 50 × 4-hour recordings (5 per mouse, daytime) |
| EEG configuration | Standard mouse cortical EEG |
| EMG configuration | Nuchal (neck) EMG |
| Sampling rate | 512 Hz (both EEG and EMG) |
| Epoch length (manual labels) | 2.5 seconds |
| Sleep stages labeled | Wake, NREM, REM |

**Label encoding** (verify this against the dataset during Phase 2):

| Label Value | Sleep Stage |
|------------|-------------|
| 1 | REM |
| 2 | Wake |
| 3 | NREM |

This encoding matches AccuSleePy's standard convention (REM=1, Wake=2, NREM=3). Confirm this is consistent in the deposited dataset files before proceeding.

**How to cite this dataset:**

> Barger, Z., & Frye, C. (2025, June 6). AccuSleep. https://doi.org/10.17605/OSF.IO/PY5EB

All use of this dataset must credit the original paper and dataset repository as above.

---

## The Tool: AccuSleePy

**AccuSleePy** is a Python implementation of the AccuSleep automated rodent sleep staging algorithm. It applies a compact neural network to EEG and EMG spectrograms to classify each epoch as Wake, NREM, or REM.

**GitHub:** [https://github.com/zekebarger/AccuSleePy]

**Pre-trained model:** `C:\Datasets\models\ssann_2(5)s.pth`
This is the 2.5-second epoch model, matching the epoch length used in this dataset.


AccuSleePy produces one label per epoch. The model classifies 3 states: Wake (2), NREM (3), REM (1).

---

## The Deliverable

The final product is a self-contained folder, `AccuSleePy_Demo/`, that contains everything needed to understand, reproduce, and present the analysis.

```
AccuSleePy_Demo/
├── README.md                          ← How to navigate and reproduce all results
├── requirements.txt                   ← All Python dependencies with pinned versions
├── .gitignore                         ← Ignore __pycache__, temp files, etc.
├── data_guide.md                      ← Technical dataset reference (built in Phase 2)
├── scripts/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_loading.py            ← Functions for loading EEG, EMG, and label files
│   │   ├── metrics.py                 ← Cohen's kappa, F1, accuracy computation
│   │   └── plotting.py                ← Shared figure generation utilities
│   ├── 01_data_inspection.py          ← Load and summarize the full dataset
│   ├── 02_accusleepy_scoring.py       ← Run AccuSleePy; save predicted label files
│   ├── 03_quality_control.py          ← Flag recordings with unusual stage proportions
│   ├── 04_validation.py               ← Compare predictions to expert labels; compute metrics
│   ├── 05_sleep_metrics.py            ← Descriptive analysis: stage %, bouts, transitions
│   └── 06_figures.py                  ← Generate all publication-quality figures
├── outputs/
│   ├── data_info.txt                  ← Full dataset inspection report saved by 01_data_inspection.py (mirrors stdout)
│   ├── predicted_labels/              ← One output file per recording (AccuSleePy native: predicted label + confidence score) + one companion calibration indices file per recording
│   ├── sleep_metrics.csv              ← Per-recording stage %, bout stats, transition rates, low-confidence epoch counts
│   └── validation_summary.csv         ← Per-recording kappa, accuracy, per-class F1
├── figures/
│   ├── hypnograms/                    ← Predicted hypnogram per representative recording
│   ├── stage_percentages/             ← Group-level % Wake / % NREM / % REM
│   ├── bout_analysis/                 ← Bout duration and count by stage
│   ├── validation/                    ← Confusion matrix, kappa distribution
│   └── transitions/                   ← Stage transition probability matrix
├── QC_report.md                       ← Flags for recordings with potential quality issues
├── low_confidence_epochs/             ← Per-recording CSV listing epochs at or below confidence threshold
└── report/
    ├── report.tex                     ← LaTeX source for the final report
    └── report.pdf                     ← Compiled final deliverable
```

**Anyone should be able to:**
1. Open `README.md` and understand the project without examining any code
2. Run any script from the command line using the instructions in `README.md`
3. Read `report.pdf` and understand the data, methods, and results without examining the code

---

## Phase Structure

Work proceeds in gated phases. **Do not begin a new phase until the gate condition for the current phase is satisfied and documented.**

---

### Phase 1: Environment Setup

**Goal:** Create a clean, portable Python environment and project structure for the deliverable.

**Steps:**

1. **Create a virtual environment** at the root of the project (not inside `AccuSleePy_Demo/`):
   ```bash
   python -m venv venv
   ```

   You must use this virtual environment for the duration of the project.

2. **Activate the environment and install dependencies:**
   ```bash
   # Windows
   venv\Scripts\activate

   pip install accusleepy numpy scipy matplotlib pandas
   ```
   Install additional packages as needed during development.

3. **Create the root `.gitignore`** (this goes at the project root, not inside the deliverable folder):

   Create an appropriate `.gitignore` file for the root of the project. This should exclude the virtual environment, OS metadata files, scratch artifacts, and any other machine-local files that should not be tracked in version control. Do **not** ignore the canonical contents of `AccuSleePy_Demo/`; the deliverable itself is meant to be versioned.

4. **Create `AccuSleePy_Demo/.gitignore`** (this goes inside the deliverable folder to handle when someone else runs the pipeline on their own machine):

   Create an appropriate `.gitignore` file for the deliverable folder. This should exclude only runtime artifacts that are recreated locally when someone else runs the pipeline on their own machine (for example `__pycache__/`, `*.pyc`, `.DS_Store`, temporary scratch folders). Do **not** ignore the intended deliverable outputs (`outputs/`, `figures/`, `report/`, `QC_report.md`, `low_confidence_epochs/`), because those are part of the reproducibility package and should remain visible in version control.

5. **Create `AccuSleePy_Demo/requirements.txt`** by pinning installed packages:
   ```bash
   pip freeze > AccuSleePy_Demo/requirements.txt
   ```
   This file lives inside the deliverable folder because it documents what is needed to run the analysis — it is part of the reproducibility record. The virtual environment itself lives at the root and is excluded from version control.

   **Note on portability:** The `requirements.txt` specifies the Python package dependencies, not the virtual environment itself. Anyone who downloads the deliverable folder creates a fresh virtual environment on their own machine and runs `pip install -r requirements.txt` to reproduce the environment. The virtual environment does not need to travel with the deliverable.

**Gate before Phase 2:**
- [ ] Virtual environment created at project root and activated without errors
- [ ] `accusleepy` importable from the environment
- [ ] Root `.gitignore` present and correct
- [ ] `AccuSleePy_Demo/.gitignore` present
- [ ] `AccuSleePy_Demo/requirements.txt` present with pinned versions

---

### Phase 2: Data Exploration and Documentation

**Goal:** Fully understand the structure and contents of the dataset. Produce `data_guide.md` as the authoritative dataset reference that all agents will use throughout the project.

**Write `scripts/01_data_inspection.py`** that loads the dataset and prints a human-readable summary. It must be runnable with a single command from the CLI using an argument for the data path:
```bash
python scripts/01_data_inspection.py --data_dir C:\Datasets\AccuSleePy_Data
```

**`data_guide.md` must cover the following. Be explicit and thorough.**

1. **File inventory:**
   - List every file (or file category) in `C:\Datasets\AccuSleePy_Data`
   - Include file names or naming patterns, file sizes, and file format
   - Indicate which files correspond to EEG signals, EMG signals, and manual labels

2. **Array shapes and data types:**
   - For a representative recording: print the shape and dtype of the EEG array, EMG array, and label array
   - Do this for at least one recording; note if any recordings differ

3. **Sampling rate verification:**
   - Confirm the sampling rate is 512 Hz
   - For a 4-hour recording at 512 Hz: expected number of samples = 4 × 3600 × 512 = 7,372,800
   - Verify this (or note any discrepancy)

4. **Epoch structure:**
   - Each epoch is 2.5 seconds
   - At 512 Hz, each epoch contains 2.5 × 512 = 1,280 samples
   - For a 4-hour recording: 4 × 3600 / 2.5 = 5,760 epochs per recording
   - Verify the label array length matches expected epoch count

5. **Label encoding:**
   - List all unique values found in the label arrays
   - Confirm or correct the encoding: REM=1, Wake=2, NREM=3
   - Note any values not matching this encoding (e.g., 0 for unscored, or other special values)
   - Document the label distribution: count and percentage of each label across all recordings
   - Report the minimum per-recording count for Wake, NREM, and REM so Phase 3 can confirm that 120 calibration epochs per stage is feasible for every recording

6. **Animal and recording organization:**
   - How are files organized — by mouse ID, by recording session, or some other structure?
   - Identify which files belong to which animal (if identifiable from file names)
   - Confirm total recording count (expected: 50 recordings from 10 mice)

7. **Loading code example:**
   - Provide the exact Python code to load one recording's EEG, EMG, and label arrays
   - This will be the template all subsequent scripts use

8. **Anomalies:**
   - Any files with unexpected shapes, unexpected label values, or that fail to load
   - Any recordings with significantly different epoch counts or signal lengths

**Gate before Phase 3:**
- [ ] `scripts/01_data_inspection.py` runs without errors on the full dataset
- [ ] `data_guide.md` is complete and covers all items above
- [ ] Label encoding confirmed (or corrected) from actual data inspection
- [ ] Total recording count and epoch structure verified
- [ ] Minimum per-recording count for each sleep stage confirms that 120 calibration epochs per stage is feasible for every recording

---

### Phase 3: AccuSleePy Scoring

**Goal:** Run AccuSleePy on all recordings using the 2.5-second model. Save one predicted label file per recording.

**Write `scripts/02_accusleepy_scoring.py`** with CLI arguments:
```bash
python scripts/02_accusleepy_scoring.py \
  --data_dir C:\Datasets\AccuSleePy_Data \
  --model_path C:\Datasets\models\ssann_2(5)s.pth \
  --output_dir AccuSleePy_Demo/outputs/predicted_labels
```

**Calibration:**

AccuSleePy includes a distributional shift correction step (referred to as "calibration") that uses a small set of manually labeled epochs from the target recording to adjust the model's decision boundaries. This is a core part of the standard AccuSleePy workflow and must be performed for each recording before scoring.

For this project, calibration data is drawn from the expert manual labels available in the dataset. For each recording, select **120 epochs per sleep stage** using the following distributed sampling procedure:

1. For each sleep stage (Wake, NREM, REM), find all epoch indices where that stage occurs in the expert labels.
2. Before sampling, verify that each stage has at least 120 labeled epochs in that recording. If any stage has fewer than 120 available epochs, stop with a clear error message that reports the stage counts for that recording rather than silently duplicating indices.
3. Select 120 epochs from those indices using evenly spaced positions: `np.linspace(0, len(stage_indices) - 1, 120, dtype=int)` to index into the stage's occurrence array. This distributes the selected epochs evenly across the full span of each stage's occurrences throughout the recording.
4. Combine the three per-stage sets to form the calibration set (360 epochs total).

This approach ensures all three stages are represented and that selected epochs are spread across the recording rather than concentrated at a single time point. Temporal distribution is important because calibration estimates per-stage feature statistics — epochs drawn from different points in the recording capture variability across the session.

**Save the calibration epoch indices** (e.g., as a `_calibration_indices.npy` or `_calibration_indices.csv` companion file in `outputs/predicted_labels/`) so that the validation script in Phase 4 can exclude exactly these epochs.

The calibration method will be documented in the report methods section as: *"Distributional shift correction was performed using AccuSleePy's built-in calibration function. For each recording, 120 epochs per sleep stage (360 total) were selected using evenly distributed sampling across each stage's occurrence indices. All remaining epochs were scored using the calibrated model. Calibration epochs were excluded from validation."*

**Steps:**
1. Load EEG, EMG, and expert label arrays for each recording using the loading code from `data_guide.md`
2. Compute calibration epoch indices using the distributed per-stage sampling procedure above (120 per stage, 360 total). Validate that each stage has at least 120 available expert-labeled epochs before sampling. Save the calibration epoch indices as a companion file alongside the predicted labels output for use in Phase 4.
3. Load the pre-trained model using `accusleepy` with the 2.5-second model path
4. Calibrate the model using the 360-epoch calibration set for this recording
5. Score all epochs of the recording using the calibrated model
6. AccuSleePy natively outputs a file containing the predicted label and confidence score for each epoch — save this output directly to `outputs/predicted_labels/` using the recording file name (without extension) as the output file name. Do not create a separate CSV; use AccuSleePy's native output.
7. After scoring is complete for this recording, delete any large intermediate files written to disk during the scoring process (e.g., temporary spectrogram files). After a test run on a single recording, inspect the working directory and any temporary locations AccuSleePy uses, and add cleanup code for any files that are not part of the final output.
8. Print progress to the terminal (e.g., `Scored recording 12/50: mouse01_recording01`)

**Gate before Phase 4:**
- [ ] All 50 recordings scored without errors
- [ ] One output file per recording in `outputs/predicted_labels/`, containing predicted label and confidence score columns
- [ ] One companion calibration indices file per recording in `outputs/predicted_labels/`, listing the 360 calibration epoch indices
- [ ] Predicted label arrays contain only values {1, 2, 3}
- [ ] No large intermediate files remain in the working directory after the script completes
- [ ] Calibration set (360 epochs: 120 per stage, distributed) and scoring method logged in script output

---

### Phase 4: Quality Control and Validation

This phase has two components that can be distributed across agents in parallel.

**Component A: Quality Control**

Write `scripts/03_quality_control.py`. For each recording, check:

1. **Stage proportion plausibility** (for a 4-hour daytime mouse recording):
   - Wake > 80%: flag (possible electrode or signal quality issue)
   - REM > 25%: flag (unusually high for a light-phase recording)
   - NREM < 10%: flag
2. **Long unbroken runs:** any unbroken stretch of a single stage longer than 60 minutes
3. **Low-confidence epoch listing:** A confidence score ≤ 0.8 is considered low-confidence. For each recording, create a CSV in `AccuSleePy_Demo/low_confidence_epochs/<recording_name>_low_confidence.csv` with columns `[epoch_index, predicted_label, confidence_score]`, listing all epochs at or below the threshold. If a recording has no low-confidence epochs, write an empty CSV with the header row only. This file is organized so that a researcher can identify these epochs and manually score them if desired.
4. Write all stage-proportion and long-run flags to `AccuSleePy_Demo/QC_report.md` with the recording name and the reason for flagging. Include a summary of low-confidence epoch counts per recording in the report (counts come from the per-recording CSVs above).

Policy: do not exclude flagged recordings from the analysis automatically. Document them and note their status in the report. The researcher (or future user) makes the final call on exclusion.

**Component B: Validation Against Expert Labels**

Write `scripts/04_validation.py`. For each recording:

1. Load the predicted labels (from Phase 3 outputs)
2. Load the expert manual labels (from the dataset)
3. **Exclude the calibration epochs** — load the companion calibration indices file saved in Phase 3 for this recording and exclude those epoch indices from the comparison. Validation is performed only on held-out epochs not used in calibration.
4. Confirm the compared arrays have the same length
5. Compute:
   - Confusion matrix (3×3: Wake, NREM, REM)
   - Cohen's kappa
   - Per-class F1 (precision, recall) for Wake, NREM, REM
   - Overall accuracy
6. Save all per-recording metrics to `outputs/validation_summary.csv`
7. Compute and print aggregate statistics: mean ± SD kappa, mean ± SD accuracy across all recordings

**Expected benchmark:** The AccuSleePy paper reports ~96.8% accuracy on this dataset with the same pre-trained model. Results close to this confirm correct pipeline execution.

**Note on framing:** The validation comparison to expert labels is included here because the dataset provides it and it is a useful technical quality check. The primary deliverable of a standard AccuSleePy engagement is the sleep architecture characterization (Phase 5), not the accuracy comparison itself. Treat validation as a confirmation that the pipeline is executing correctly, not as the scientific endpoint.

**Gate before Phase 5:**
- [ ] `QC_report.md` written with all flagged recordings noted
- [ ] `outputs/validation_summary.csv` complete with per-recording metrics
- [ ] Aggregate kappa and accuracy printed or saved

---

### Phase 5: Descriptive Sleep Metrics

**Goal:** Compute the standard sleep architecture metrics that form the core analytical deliverable. These metrics characterize the sleep behavior of the animals per recording and are what a researcher primarily needs from an AccuSleePy analysis.

Write `scripts/05_sleep_metrics.py`:

**Stage Proportions (per recording):**
- Percent time Wake, percent time NREM, percent time REM

**Bout Analysis (per stage, per recording):**
- A *bout* is a continuous run of epochs with the same predicted stage
- For each stage: mean bout duration (seconds), maximum bout duration, total bout count
- At 2.5 seconds per epoch: a 5-epoch bout = 12.5 seconds; convert all durations to seconds

**Transition Analysis (per recording):**
- State transition probability matrix: for each current state, what fraction of transitions lead to each other state?
- This characterizes sleep architecture beyond simple stage proportions

**Low-confidence Epoch Summary (per recording):**
- Count of epochs with confidence score ≤ 0.8
- Percentage of total epochs with confidence score ≤ 0.8
- This gives a recording-level signal of overall scoring reliability

Save all metrics to `outputs/sleep_metrics.csv` with columns for: recording ID, animal ID (if identifiable), % Wake, % NREM, % REM, all bout and transition statistics, low-confidence epoch count, and low-confidence epoch percentage.

**Gate before Phase 6:**
- [ ] `outputs/sleep_metrics.csv` complete for all 50 recordings
- [ ] All metrics computed from predicted labels only (not manual labels)

---

### Phase 6: Figure Generation


Write `scripts/06_figures.py`. All figures must meet the requirements in the Software Engineering Best Practices section: 300+ DPI, labeled axes, clear titles. Use consistent colors throughout: **Wake = green, NREM = blue, REM = red**
**Figure set:**

1. **Hypnograms** (`figures/hypnograms/`): For 4–6 representative animals, plot the predicted sleep stage sequence over the full 4-hour recording. If a mouse has multiple recordings, choose one representative recording and state the selection rule in the script or README. x-axis = time in hours; y-axis = stage (Wake/NREM/REM). One file per animal shown.

2. **Stage percentage plots** (`figures/stage_percentages/`): Box or bar plots showing % Wake, % NREM, % REM across all 10 animals. Each animal is one data point; if there are multiple recordings per mouse, first average within mouse so repeated recordings from the same animal are not treated as independent samples. Show mean and SEM across animals.

3. **Bout duration plots** (`figures/bout_analysis/`): Box plots of mean bout duration per stage across animals. If there are multiple recordings per mouse, aggregate to one value per mouse before plotting. One panel per stage, or a grouped box plot with all three stages.

4. **Aggregate confusion matrix** (`figures/validation/`): Summed confusion matrix across all recordings, normalized to show row percentages. Rows = expert label; columns = predicted label.

5. **Kappa distribution** (`figures/validation/`): Box plot or histogram of per-recording kappa values.

6. **Transition matrix heatmap** (`figures/transitions/`): Mean state transition probability matrix across recordings, shown as a 3×3 heatmap.

**Gate before Phase 7:**
- [ ] All six figure types generated and saved in the correct subdirectories
- [ ] All figures meet quality standards (300+ DPI, labeled axes, titles)

---

### Phase 7: Report Assembly

**Goal:** Write and compile the final `report.pdf` using LaTeX.

**Report format:** The report is written in **LaTeX** and compiled to PDF. The LaTeX source (`report.tex`) and compiled PDF (`report.pdf`) both live in `AccuSleePy_Demo/report/`. Embed figures from the `figures/` directory using relative paths via `\includegraphics`.

The report is a technical analysis document — the writing style should match a methods-and-results section of a scientific publication: precise, passive voice where appropriate, and fully citable.

---

**Abstract** 

The report opens with an abstract that stands on its own. It must contain:
- What dataset was used (species, number of animals and recordings, citation, OSF link)
- What tool was used (AccuSleePy, model, epoch length, calibration method in one sentence: 120 epochs per stage distributed across each recording)
- What the pipeline produced (scored labels, validation metrics, sleep architecture metrics)
- Key aggregate results (mean kappa, mean accuracy, brief summary of group-level stage proportions)

A reader who reads only the abstract should understand what was done and what was found.

---

**Section 1: Data**

- Dataset citation (Barger et al., PLOS ONE 2019) and OSF repository link
- Species (C57BL/6 mouse), number of animals and recordings, recording duration
- Sampling rate (512 Hz), epoch length (2.5 seconds), channel configuration (standard cortical EEG + nuchal EMG)
- Label encoding: REM=1, Wake=2, NREM=3
- Summary table: recording count, total epochs, label distribution across all recordings (from Phase 2)

---

**Section 2: Methods**

Written to the standard of a methods section in a peer-reviewed journal article. Each subsection must be complete enough to cite in a paper.

- **Data loading:** File format, how EEG, EMG, and label arrays were read; Python tools used.
- **Calibration:** AccuSleePy's distributional shift correction; calibration set composition (120 epochs per sleep stage, 360 total) and selection method (evenly distributed across each stage's occurrence indices using `np.linspace`); why calibration is performed; citation to the AccuSleePy paper (Barger et al. 2019).
- **Scoring:** Model used (`ssann_2(5)s.pth`, 2.5-second epoch model); how the model was applied after calibration; confidence score output.
- **Quality control:** Stage proportion plausibility thresholds; long-run detection rule; confidence score threshold (≤0.8) for low-confidence epoch listing; QC decision rule (flag but do not exclude).
- **Validation:** How predicted labels were compared to expert labels; metrics used (Cohen's kappa, per-class precision/recall/F1, overall accuracy); note that calibration epochs (360 per recording) were excluded from validation (validation is performed on held-out epochs only).
- **Descriptive metrics:** Definition of a bout; stage percentage computation; transition probability matrix definition; time resolution (2.5 s per epoch); low-confidence epoch count and percentage.
- **Software:** Python version; AccuSleePy version; all packages with pinned versions from `requirements.txt`.

---

**Section 3: Results**

**3.1 Pipeline Validation** *(framed explicitly as a technical quality check, not the primary scientific result)*
- Aggregate 3×3 confusion matrix (figure from `figures/validation/`); rows = expert label, columns = predicted label
- Mean ± SD kappa and accuracy across all 50 recordings
- Per-class F1 (precision, recall) for Wake, NREM, and REM
- Comparison to published benchmark: the AccuSleePy paper reports ~96.8% accuracy on this dataset; note whether results are consistent with this

**3.2 Quality Control Summary**
- Number of recordings flagged and reasons (from `QC_report.md`)
- Distribution of low-confidence epoch counts across recordings (median, range)
- Statement that no recordings were excluded from the analysis

**3.3 Sleep Architecture** *(the primary analytical deliverable)*
- Group-level stage percentage plots with mean and SEM (figure from `figures/stage_percentages/`)
- Bout duration analysis: mean bout duration per stage across all animals (figure from `figures/bout_analysis/`)
- Mean state transition probability matrix heatmap (figure from `figures/transitions/`)
- Representative hypnograms for 4–6 animals (figures from `figures/hypnograms/`)
- Descriptive text accompanying each figure; describe what the figures show without mechanistic interpretation

---

**Section 4: Limitations**

- This analysis uses the standard cortical EEG/EMG configuration for which AccuSleePy was designed; model performance may differ for non-standard or multi-region recording setups.
- All analyses are descriptive. Biological interpretation of results is the responsibility of the researcher.
- No recordings were excluded; flagged recordings from QC are noted in Section 3.2 and included in all analyses.

---

**Section 5: References**

Formatted bibliography entries for appropriate sources.

---

**Write `AccuSleePy_Demo/README.md`** covering:
- What this project is and what dataset it uses
- How to set up the environment (`pip install -r requirements.txt`)
- How to run each script in order, with example commands
- Expected outputs at each step

**Gate before project complete:**
- [ ] `report.tex` and `report.pdf` complete and in `AccuSleePy_Demo/report/`
- [ ] All six report elements present (Abstract, Data, Methods, Results, Limitations, References)
- [ ] All figures referenced in the report are present in `figures/`
- [ ] `README.md` explains how to reproduce results from scratch
- [ ] `AccuSleePy_Demo/` folder is fully self-contained and organized as specified

---

## Reproducibility and Portability

**These are hard requirements, not preferences.**

- **No hard-coded paths in any script.** All machine-specific paths (data directory, model path, output directory) must be passed via CLI arguments with `required=True`. A script that silently fails with a wrong path is a reproducibility failure.
- **`AccuSleePy_Demo/` must be fully portable.** It must run correctly on any machine given the correct data path and a fresh environment installed from `requirements.txt`. Do not assume any path outside of what is passed via CLI argument.
- **Use `argparse` for all scripts.** CLI arguments are the reproducibility standard for scientific computing pipelines. The full command appears in shell history; the parameters are explicit. Include example commands in `README.md`.
- **Output directories use project-relative defaults.** Scripts write outputs relative to the project root, not to absolute paths.
- **Pin all dependencies in `requirements.txt`.** Include version numbers. Results should be reproducible from the requirements file alone.


---

## Scientific Best Practices

- **Primary metric for validation:** Cohen's kappa — not raw accuracy. Kappa accounts for class imbalance. Report kappa, accuracy, and per-class F1 (precision, recall) for Wake, NREM, and REM.
- **Validation framing:** The comparison to expert labels is a technical quality check confirming the pipeline executes correctly. It is not the primary scientific result of this analysis. Report it clearly but frame it accordingly.
- **Scope of analysis:** All analysis is descriptive. Figures and metrics characterize what the data shows — stage proportions, bout structure, transition patterns. Do not make mechanistic claims about biology or interpret findings in terms of specific hypotheses. The data speaks for itself.
- **Transparency:** Report all recordings, including those flagged in QC. Document the QC decision rule (flag but do not exclude) and apply it consistently.
- **Reproducibility:** Log all script runs with parameters. Results must be fully reproducible from the `README.md` instructions.

---

## Software Engineering Best Practices

- **Modular scripts:** Each script has one clear purpose. No monolithic notebooks.
- **Command-line interfaces:** All scripts accept arguments via `argparse`. No hard-coded paths.
- **Pinned dependencies:** `requirements.txt` with locked package versions.
- **Docstrings:** Every function has a docstring stating inputs, outputs, and purpose.
- **Clear output:** Scripts print progress to stdout and write results to named output files. No silent failures.
- **Figure quality:** Save as PNG at 300+ DPI with labeled axes, titles, and consistent color scheme. Figures should be immediately interpretable without reading the code.
- **Error handling:** Validate inputs at entry points. Raise clear, informative errors.
- **`utils/` for shared code:** Functions used by multiple scripts (data loading, metrics, plotting) live in `scripts/utils/`. Do not copy-paste logic across scripts.
