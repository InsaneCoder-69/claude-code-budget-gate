# Windows Setup Guide

## The only difference from Mac
The core Python files work identically. Two things change on Windows:

### 1. settings.json — change python3 to python
Open `.claude/settings.json` and replace both occurrences of `python3` with `python`.

Or run this in PowerShell:
```powershell
(Get-Content .claude\settings.json) -replace 'python3', 'python' | Set-Content .claude\settings.json
```

### 2. Every session — use PowerShell, not Terminal
```powershell
cd C:\Users\YourName\your-project
$env:CLAUDE_PROJECT_DIR = $PWD.Path
claude
```

That's it. Everything else is identical to the Mac setup.

## If python is not found
Find your Python path:
```powershell
python -c "import sys; print(sys.executable)"
```
Replace `python` in `settings.json` with that full path.
