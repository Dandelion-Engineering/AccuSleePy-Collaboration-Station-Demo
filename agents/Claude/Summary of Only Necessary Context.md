# Summary of Only Necessary Context — Claude Session 13 → Session 14

_Rewritten at the end of Session 13 (2026-03-23). Read this at the start of Session 14 before doing any work._

---

## Current Phase

**The project deliverable is complete.** All phases (1–7) are done and fully approved by Codex, Antigravity, and Randy.

---

## What Was Done in Session 13

1. **Concluded the Phase 7 chat** — renamed `Phase 7 - Active.md` to `Phase 7 - Concluded.md` and created `Summary.md` in `chats/Claude-Codex-Antigravity-Human/Phase 7/`.

2. **Updated `AccuSleePy_Demo/README.md` to use PowerShell** per Randy's request in the new Powershell chat:
   - Terminal opening instruction changed to PowerShell (`Win+X`)
   - All `cmd` code blocks changed to `powershell`
   - Activation command changed to `venv\Scripts\Activate.ps1` with an execution policy note
   - Convenience variables changed from `set VAR=value` to `$env:VAR = "value"`
   - Variable references changed from `%VAR%` to `$env:VAR`
   - Line continuation changed from `^` to `` ` `` (backtick)

3. **Replied to the Powershell chat** confirming all changes made.

---

## Current State of Work

### All Phase Outputs (complete and approved)

**Phase 3:**
- `AccuSleePy_Demo/outputs/predicted_labels/` — 50 predicted-label CSVs + 50 calibration-index CSVs

**Phase 4:**
- `AccuSleePy_Demo/QC_report.md` — 0 flagged recordings; 481 total low-confidence epochs
- `AccuSleePy_Demo/low_confidence_epochs/` — 50 per-recording CSVs
- `AccuSleePy_Demo/outputs/validation_summary.csv` — kappa 0.9490 ± 0.0148, accuracy 0.9725 ± 0.0072

**Phase 5:**
- `AccuSleePy_Demo/outputs/sleep_metrics.csv` — 50 rows × 26 columns

**Phase 6:**
- `AccuSleePy_Demo/figures/hypnograms/` — 6 PNG hypnograms (Mouse01–Mouse06, Day1)
- `AccuSleePy_Demo/figures/stage_percentages/stage_percentages.png`
- `AccuSleePy_Demo/figures/bout_analysis/bout_duration.png`
- `AccuSleePy_Demo/figures/validation/confusion_matrix.png`
- `AccuSleePy_Demo/figures/validation/kappa_distribution.png`
- `AccuSleePy_Demo/figures/transitions/transition_matrix.png`

**Phase 7 (complete):**
- `AccuSleePy_Demo/README.md` — final version with all fixes applied (now PowerShell)
- `AccuSleePy_Demo/report/report.tex` — all peer review corrections applied
- `AccuSleePy_Demo/report/report.pdf` — 12 pages, no errors

---

## Active Chats

### `chats/Claude-Human/Powershell/Powershell - Active.md`

**Status:** Active. Claude has posted the PowerShell conversion confirmation message. Awaiting Randy's response.

**Next action for Claude:** At the start of Session 14:
1. Read the Powershell chat
2. If Randy confirms the changes are satisfactory, conclude the chat and write a Summary.md
3. If there is further feedback, apply it
4. If Randy gives no further instructions, the project is complete

---

## Key Quantitative Results (for reference)

| Metric | Value |
|---|---|
| Kappa | 0.9490 ± 0.0148 |
| Accuracy | 97.25 ± 0.72% |
| Wake F1 | 0.9623 ± 0.0174 |
| NREM F1 | 0.9763 ± 0.0050 |
| REM F1 | 0.9754 ± 0.0093 |
| Wake precision / recall | 95.90% / 96.60% |
| NREM precision / recall | 98.12% / 97.17% |
| REM precision / recall | 95.54% / 99.64% |
| Mean % Wake | 34.53 ± 5.16% (animal-level, n=10) |
| Mean % NREM | 54.64 ± 4.00% (animal-level, n=10) |
| Mean % REM | 10.83 ± 1.37% (animal-level, n=10) |
| Mean Wake bout | 41.5 ± 10.4 s (animal-level) |
| Mean NREM bout | 62.9 ± 7.0 s (animal-level) |
| Mean REM bout | 76.4 ± 11.1 s (animal-level) |
| Total low-confidence epochs | 481 (mean 0.167%); median 8/recording, range 1–28 |
| Recordings flagged in QC | 0 / 50 |

---

## Key Constraints and Assumptions

- **No hard-coded paths anywhere.** All scripts use `argparse` with `required=True`.
- **Python environment:** `venv/Scripts/python.exe` — always use this interpreter.
- **Data path:** `C:\Datasets\AccuSleePy_Data` — pass via `--data_dir`.
- **Model path:** `C:\Datasets\models\ssann_2(5)s.pth` — pass via `--model_path`.
- **Label encoding:** REM=1, Wake=2, NREM=3 — confirmed.
- **File encoding:** Use `encoding="utf-8"` when writing markdown files on Windows.
- **SDs in report.tex:** Animal-level (n=10) SDs are used in Section 3.3 where text says "across 10 animals". Abstract uses recording-level (n=50) SDs — this is intentional and consistent.
