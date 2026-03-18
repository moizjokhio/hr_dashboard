$ErrorActionPreference = "Stop"

Set-Location "C:\Users\dell\Employee_Tracker\hr-analytics-system\backend"

$pythonExe = "C:\Users\dell\Employee_Tracker\hr-analytics-system\.venv\Scripts\python.exe"

Write-Host "Starting backend on port 8000..." -ForegroundColor Green
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Cyan

& $pythonExe -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
