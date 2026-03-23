# Powershell

**Date Started:** 2026-03-23

**Randy:**

Hey Claude! Please change the README.md file to use powershell instead of command prompt for windows. Thanks!

---

**Claude (Session 13):**

Done! `AccuSleePy_Demo/README.md` has been updated throughout to use PowerShell instead of Command Prompt for all Windows instructions. Here is a summary of every change made:

- **Terminal opening instruction** — updated to "Press `Win + X` and select Windows PowerShell (or Terminal in Windows 11)"
- **All `cmd` code blocks** — changed to `powershell`
- **Virtual environment activation** — changed from `venv\Scripts\activate` to `venv\Scripts\Activate.ps1`, and added a note explaining how to resolve the execution policy error that Windows users commonly encounter
- **Convenience variables** — label changed to "Windows (PowerShell)"; syntax changed from `set VAR=value` to `$env:VAR = "value"`
- **Variable usage explanation** — updated from `%DATA_DIR%` to `$env:DATA_DIR`
- **All 6 script commands** — variable references updated from `%VAR%` to `$env:VAR`, and line continuation characters updated from `^` (cmd) to `` ` `` (PowerShell backtick)
