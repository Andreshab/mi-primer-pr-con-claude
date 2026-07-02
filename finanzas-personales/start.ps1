$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$root\.venv\Scripts\python.exe" -m uvicorn main:app --reload --app-dir "$root\backend"
