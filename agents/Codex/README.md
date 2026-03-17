# Codex Workspace

This folder is Codex's local workspace for the AccuSleePy Demo collaboration. It contains the files needed to understand Codex's current state quickly, review prior session outputs, and resume work without searching the full repository first.

## Folder Tree

```text
agents/Codex/
|-- README.md
|-- Summary of Only Necessary Context.md
`-- Session Summaries/
    |-- HumanReport1.md
    |-- HumanReport2.md
    |-- HumanReport3.md
    |-- HumanReport4.md
    |-- HumanReport5.md
    `-- HumanReport6.md
```

## Top-Level Files and Folders

- `README.md`: Navigation guide for this workspace. Authoritative for workspace structure and file purpose.
- `Summary of Only Necessary Context.md`: Restart document for the next Codex session. Authoritative for session-to-session continuity within Codex's workspace.
- `Session Summaries/`: Historical human-readable reports written at the end of each Codex session. These are records, not the live handoff source.

## Authoritative vs Temporary

- Authoritative:
  - `README.md` for workspace navigation
  - `Summary of Only Necessary Context.md` for resuming work next session
- Historical records:
  - `Session Summaries/*.md`
- Temporary or scratch:
  - None currently maintained in this workspace

## Files Outside This Workspace That Codex Owns or Co-Owns

- Codex co-owns any chat transcript in `/chats/` whose participant folder includes `Codex`.
- Current active co-owned transcript:
  - `chats/Claude-Codex-Antigravity-Human/Phase 5/Phase 5 - Active.md`

## How To Navigate This Folder

Start with `Summary of Only Necessary Context.md` if the goal is to resume work. Read `Session Summaries/` only if deeper historical detail is needed. Use this `README.md` when checking what each file is for or which external paths Codex is expected to maintain.
