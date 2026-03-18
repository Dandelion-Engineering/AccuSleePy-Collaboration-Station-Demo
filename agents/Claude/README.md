# Claude's Workspace — README

## Folder Tree

```
agents/Claude/
├── README.md                              ← This file. Navigation guide for Claude's workspace.
├── Summary of Only Necessary Context.md  ← Session continuity file. Rewritten each session.
└── Session Summaries/
    ├── HumanReport1.md                   ← End-of-session report from Session 1
    ├── HumanReport2.md                   ← End-of-session report from Session 2
    ├── HumanReport3.md                   ← End-of-session report from Session 3
    ├── HumanReport4.md                   ← End-of-session report from Session 4
    ├── HumanReport5.md                   ← End-of-session report from Session 5
    ├── HumanReport6.md                   ← End-of-session report from Session 6
    ├── HumanReport7.md                   ← End-of-session report from Session 7
    ├── HumanReport8.md                   ← End-of-session report from Session 8
    ├── HumanReport9.md                   ← End-of-session report from Session 9
    ├── HumanReport10.md                  ← End-of-session report from Session 10
    ├── HumanReport11.md                  ← End-of-session report from Session 11
    └── HumanReport12.md                  ← End-of-session report from Session 12
```

## File and Folder Descriptions

### `README.md` (this file)
Authoritative guide to this workspace. Updated when folder structure changes. Describes the purpose of all files and folders. Intended audience: any human or agent who needs to navigate Claude's workspace without prior context.

### `Summary of Only Necessary Context.md`
**Purpose:** Session continuity. Rewritten at the end of every session to contain all context Claude needs to resume work seamlessly in the next session.
**Authoritative vs. Temporary:** Authoritative for the current session state. Superseded at the start of each new session's rewrite.

### `Session Summaries/`
**Purpose:** Archive of human-readable end-of-session reports documenting what Claude accomplished, decisions made, and next steps.
**Naming:** Sequential — `HumanReport1.md`, `HumanReport2.md`, etc.
**Authoritative vs. Temporary:** Authoritative. These are permanent records.

## Files Owned or Co-Owned Outside This Workspace

| Path | Ownership | Purpose |
|------|-----------|---------|
| `chats/Claude-Codex-Antigravity-Human/Phase 1/Phase 1 - Concluded.md` | Co-owned (all four participants) | Phase 1 coordination chat — concluded |
| `chats/Claude-Codex-Antigravity-Human/Phase 1/Summary.md` | Co-owned | Phase 1 chat summary |
| `chats/Claude-Codex-Antigravity-Human/Phase 2/Phase 2 - Concluded.md` | Co-owned (all four participants) | Phase 2 coordination chat — concluded |
| `chats/Claude-Codex-Antigravity-Human/Phase 3/Phase 3 - Concluded.md` | Co-owned (all four participants) | Phase 3 coordination chat — concluded |
| `chats/Claude-Codex-Antigravity-Human/Phase 3/Summary.md` | Co-owned | Phase 3 chat summary |
| `chats/Claude-Codex-Antigravity-Human/Phase 4/Phase 4 - Concluded.md` | Co-owned (all four participants) | Phase 4 coordination chat — concluded |
| `chats/Claude-Codex-Antigravity-Human/Phase 4/Summary.md` | Co-owned | Phase 4 chat summary |
| `chats/Claude-Codex-Antigravity-Human/Phase 5/Phase 5 - Concluded.md` | Co-owned (all four participants) | Phase 5 coordination chat — concluded |
| `chats/Claude-Codex-Antigravity-Human/Phase 5/Summary.md` | Co-owned | Phase 5 chat summary |
| `chats/Claude-Codex-Antigravity-Human/Phase 6/Phase 6 - Concluded.md` | Co-owned (all four participants) | Phase 6 coordination chat — concluded |
| `chats/Claude-Codex-Antigravity-Human/Phase 6/Summary.md` | Co-owned | Phase 6 chat summary |
| `chats/Claude-Codex-Antigravity-Human/Phase 7/Phase 7 - Active.md` | Co-owned (all four participants) | Phase 7 coordination chat — active |
| `AccuSleePy_Demo/README.md` | Claude (author) | Project README — setup, run commands, expected outputs |
| `AccuSleePy_Demo/report/report.tex` | Claude (author) | Full LaTeX source for the final report |
| `AccuSleePy_Demo/report/report.pdf` | Claude (author) | Compiled 12-page final report |
| `AccuSleePy_Demo/` | Co-owned (all agents) | The deliverable — Claude is the primary author of all scripts and files |
| `AccuSleePy_Demo/scripts/utils/data_loading.py` | Claude (author) | Shared data loading utilities |
| `AccuSleePy_Demo/scripts/utils/metrics.py` | Claude (author) | Shared metric computation utilities (kappa, F1, accuracy, confusion matrix) |
| `AccuSleePy_Demo/scripts/utils/plotting.py` | Claude (author) | Shared plotting constants and helpers |
| `AccuSleePy_Demo/scripts/01_data_inspection.py` | Claude (author) | Phase 2 dataset inspection script |
| `AccuSleePy_Demo/scripts/02_accusleepy_scoring.py` | Claude (author) | Phase 3 scoring script |
| `AccuSleePy_Demo/scripts/03_quality_control.py` | Claude (author) | Phase 4A QC script |
| `AccuSleePy_Demo/scripts/04_validation.py` | Codex (author) | Phase 4B validation script |
| `AccuSleePy_Demo/scripts/05_sleep_metrics.py` | Claude (author) | Phase 5 sleep metrics script |
| `AccuSleePy_Demo/scripts/06_figures.py` | Claude (author) | Phase 6 figure generation script |
| `AccuSleePy_Demo/outputs/validation_summary.csv` | Codex (author) | Phase 4B per-recording validation metrics |
| `AccuSleePy_Demo/data_guide.md` | Claude (author) | Authoritative dataset reference |
| `AccuSleePy_Demo/outputs/predicted_labels/` | Claude (author) | Phase 3 outputs: predicted labels + calibration indices (50 + 50 CSV files) |
| `AccuSleePy_Demo/outputs/sleep_metrics.csv` | Claude (author) | Phase 5 per-recording sleep architecture metrics (50 rows × 26 columns) |
| `AccuSleePy_Demo/QC_report.md` | Claude (author) | Phase 4A QC report |
| `AccuSleePy_Demo/low_confidence_epochs/` | Claude (author) | Phase 4A per-recording low-confidence epoch CSVs (50 files) |
| `AccuSleePy_Demo/figures/` | Claude (author) | Phase 6 figure outputs (11 PNG files across 5 subdirectories) |
| `.gitignore` | Claude (author) | Root gitignore |
| `AccuSleePy_Demo/.gitignore` | Claude (author) | Deliverable gitignore |
| `AccuSleePy_Demo/requirements.txt` | Claude (author) | Pinned Python dependencies |

## Navigation Notes

- Start with `Summary of Only Necessary Context.md` to understand the current state of work
- Read `Session Summaries/` in order to trace the evolution of Claude's contributions
- For project-wide context, read `Project Details/Project Details.md` and `AgentPrompt.md` at the project root
