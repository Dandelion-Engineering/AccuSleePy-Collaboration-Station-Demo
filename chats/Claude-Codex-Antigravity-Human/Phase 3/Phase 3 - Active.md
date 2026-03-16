# Phase 3

**Date Started:** 2026-03-16


**Randy:**

Let's get started on Phase 3. Claude I will once again have you complete all the tasks for Phase 3. Codex and Antigravity will check the work to make sure all gates are passed and that it adheres to the standards of reproducibility and portability, scientific best practices and software engineering best practices set out in Project Details.md. Codex, Antigravity and I must explicitly approve the work before we move on to Phase 4.

I wanted to talk a bit more about how you should approach this phase. So running AccuSleePy creates some large files that might only be used temporarily and that we don't need for the rest of our work. Claude, run AccuSleePy on one of the recordings and determine if there are any files like that. If there are, you will make sure that 02_accusleepy_scoring.py automatically deletes them when they are no longer needed. Delete all outputs from this test run. 02_accusleepy_scoring.py shoud cleanly run on all recordings including the one you used for the test.

**Claude (Session 4):**

Understood, Randy. Here is my plan for Phase 3:

1. **Test run first:** I will run AccuSleePy on a single recording to discover any temporary or intermediate files created during the scoring process (e.g., spectrogram image files written to disk). I will inspect all directories that AccuSleePy touches during scoring.
2. **Build cleanup into the script:** Any temporary files discovered will be deleted within `02_accusleepy_scoring.py` as part of the per-recording loop — after saving the final outputs and before moving to the next recording.
3. **Delete test outputs:** All files from the test run will be removed before the full run.
4. **Full run:** Score all 50 recordings cleanly and verify all gate conditions.

Starting now.

---

**Claude (Session 4) — Phase 3 Complete:**

Phase 3 is complete. Here is a full summary of what was done:

**Test run (Randy's instruction):**
I ran AccuSleePy on one recording (`Mouse01_Day1`) and monitored the filesystem before and after scoring — checking both the project working directory and the system temp directory. Result: **AccuSleePy scoring is entirely in-memory**. No intermediate or temporary files are written to disk at any point during the scoring process. The `score_recording()` function builds the EEG/EMG spectrogram image as a numpy array, processes it in memory, runs inference in memory, and returns labels and confidence scores. No cleanup is required.

**Script written:** `AccuSleePy_Demo/scripts/02_accusleepy_scoring.py`

Key implementation details:
- CLI arguments: `--data_dir` (required), `--model_path` (required), `--output_dir` (default: `AccuSleePy_Demo/outputs/predicted_labels`)
- Calibration: 120 epochs per stage (REM, Wake, NREM) selected via `np.linspace` across each stage's occurrence indices — 360 total calibration epochs per recording
- Validation: script raises a clear error with all stage counts if any stage has fewer than 120 available epochs (none did)
- Saves predicted labels via `accusleepy.fileio.save_labels` (native AccuSleePy format: CSV with `brain_state` and `confidence_score` columns)
- Saves calibration indices as `<recording_id>_calibration_indices.csv` alongside each label file
- Notes in the script that no temporary file cleanup is needed (scoring is in-memory)

**Full run — all 50 recordings scored without errors.**

**Gate conditions verified:**
- [x] All 50 recordings scored without errors
- [x] One output file per recording in `outputs/predicted_labels/` — columns: `brain_state`, `confidence_score`; 5,760 rows each
- [x] One companion calibration indices file per recording — 360 rows each (120 per stage)
- [x] Predicted label arrays contain only values {1, 2, 3} — confirmed for all 50
- [x] No large intermediate files remain in the working directory after the script completes — confirmed (scoring is in-memory)
- [x] Calibration set (360 epochs: 120 per stage, distributed via np.linspace) and scoring method logged in script output

**Codex and Antigravity**: please verify that all gate conditions pass and that the script meets the reproducibility, portability, scientific, and software engineering standards from `Project Details.md`. Randy, Codex, and Antigravity must explicitly approve before Phase 4 begins.