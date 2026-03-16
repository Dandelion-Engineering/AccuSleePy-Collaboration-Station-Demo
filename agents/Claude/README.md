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
    └── HumanReport4.md                   ← End-of-session report from Session 4
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
| `chats/Claude-Codex-Antigravity-Human/Phase 3/Phase 3 - Active.md` | Co-owned (all four participants) | Phase 3 coordination chat — active |
| `AccuSleePy_Demo/` | Co-owned (all agents) | The deliverable — Claude is the primary author of all scripts and files |
| `AccuSleePy_Demo/scripts/utils/data_loading.py` | Claude (author) | Shared data loading utilities |
| `AccuSleePy_Demo/scripts/01_data_inspection.py` | Claude (author) | Phase 2 dataset inspection script |
| `AccuSleePy_Demo/scripts/02_accusleepy_scoring.py` | Claude (author) | Phase 3 scoring script |
| `AccuSleePy_Demo/data_guide.md` | Claude (author) | Authoritative dataset reference |
| `AccuSleePy_Demo/outputs/predicted_labels/` | Claude (author) | Phase 3 outputs: predicted labels + calibration indices (50 + 50 CSV files) |
| `.gitignore` | Claude (author) | Root gitignore |
| `AccuSleePy_Demo/.gitignore` | Claude (author) | Deliverable gitignore |
| `AccuSleePy_Demo/requirements.txt` | Claude (author) | Pinned Python dependencies |

## Navigation Notes

- Start with `Summary of Only Necessary Context.md` to understand the current state of work
- Read `Session Summaries/` in order to trace the evolution of Claude's contributions
- For project-wide context, read `Project Details/Project Details.md` and `AgentPrompt.md` at the project root
