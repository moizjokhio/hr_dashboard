@echo off
cd /d C:\Users\dell\Employee_Tracker\hr-analytics-system\backend
C:\Users\dell\Employee_Tracker\hr-analytics-system\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
