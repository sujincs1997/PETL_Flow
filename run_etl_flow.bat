@echo off

REM -------------------------------------------------
REM  Run the complete ETL Flow environment (backend + frontend)
REM -------------------------------------------------

REM 1️⃣ Start FastAPI backend in a new console window
start "Backend" cmd /k "cd /d %~dp0 && uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload"

REM Give the backend a moment to start up
timeout /t 5 >nul

REM 2️⃣ Start Vite frontend dev server in a new console window
start "Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

REM Give the frontend a moment to compile
timeout /t 5 >nul

REM 3️⃣ Open the UI in the default browser (React app runs on port 3000)
start "" "http://localhost:3000"

REM -------------------------------------------------
REM  After the UI loads you will see the Login modal.
REM  Use the credentials you created earlier (e.g. username: admin, password: admin123).
REM  Once logged in you can drag‑drop nodes, save pipelines, and execute DAGs.
REM -------------------------------------------------
