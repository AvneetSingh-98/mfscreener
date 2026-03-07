@echo off
REM =========================
REM DAILY PIPELINE CRON WRAPPER (Windows)
REM =========================

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%.."
set "PROJECT_ROOT=%BACKEND_DIR%\.."

REM Change to backend directory
cd /d "%BACKEND_DIR%"

REM Load environment variables from .env file
if exist "%PROJECT_ROOT%\.env" (
    for /f "usebackq tokens=1,* delims==" %%a in ("%PROJECT_ROOT%\.env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            set "%%a=%%b"
        )
    )
)

REM Create logs directory
set "LOG_DIR=%BACKEND_DIR%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Generate log filename with timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "LOG_FILE=%LOG_DIR%\daily_pipeline_%datetime:~0,8%_%datetime:~8,6%.log"

REM Log start
echo ========================== >> "%LOG_FILE%"
echo Pipeline started at: %date% %time% >> "%LOG_FILE%"
echo Working directory: %cd% >> "%LOG_FILE%"
echo Python: >> "%LOG_FILE%"
where python >> "%LOG_FILE%" 2>&1
echo MONGO_URI: %MONGO_URI:~0,20%... >> "%LOG_FILE%"
echo ========================== >> "%LOG_FILE%"

REM Run the pipeline
python "%SCRIPT_DIR%daily_pipeline.py" >> "%LOG_FILE%" 2>&1

REM Log completion
echo ========================== >> "%LOG_FILE%"
echo Pipeline finished at: %date% %time% >> "%LOG_FILE%"
echo Exit code: %ERRORLEVEL% >> "%LOG_FILE%"
echo ========================== >> "%LOG_FILE%"

exit /b %ERRORLEVEL%
