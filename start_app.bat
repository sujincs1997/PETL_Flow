@echo off
REM Batch file to start the ETL Flow FastAPI server and open the web UI

:: Change to the project root directory (where this .bat resides)
cd /d "%~dp0"

:: Start the FastAPI app using uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

:: After the server starts, open the default browser to the API docs
start "" "http://localhost:8000/docs"
