# Encoding Guide

On Windows terminals, subprocess output can fail when a command writes Unicode through a legacy code page. Prefer `--quiet` plus file output.

The wrapper sets:

```text
PYTHONIOENCODING=utf-8
```

If running manually in PowerShell, use:

```powershell
$env:PYTHONIOENCODING = "utf-8"
chcp 65001
kimi --quiet --prompt "Search ... and save to result.md" --work-dir .
```

Avoid piping large Chinese text through stdout. Ask Kimi to write the result to a file and read that file afterward.
