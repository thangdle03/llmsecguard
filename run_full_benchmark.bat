@echo off
echo ========================================
echo  LLMSecGuard Benchmark Runner
echo ========================================
echo.

REM Activate virtual environment
call D:\LLMSecGuard\venv\Scripts\activate.bat

REM Change to backend directory
cd /d D:\LLMSecGuard\backend

echo Starting analyzer service...
start "Analyzer Service" cmd /k "python services/analyzer/service.py"
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo Testing Branch: DR (Direct)
echo ========================================
python manage.py runbenchmark --model 4 --limit 15 --branch DR

echo.
echo ========================================
echo Testing Branch: IP (Ignore Previous Instructions)
echo ========================================
python manage.py runbenchmark --model 4 --limit 15 --branch IP

echo.
echo ========================================
echo Testing Branch: IR (Indirect Reference)
echo ========================================
python manage.py runbenchmark --model 4 --limit 15 --branch IR

echo.
echo ========================================
echo Testing Branch: PE (Privilege Escalation)
echo ========================================
python manage.py runbenchmark --model 4 --limit 15 --branch PE

echo.
echo ========================================
echo Testing Branch: SM (Stats per Model)
echo ========================================
python manage.py runbenchmark --model 4 --limit 15 --branch SM

echo.
echo ========================================
echo  ALL BENCHMARKS COMPLETED!
echo ========================================
echo.
echo Total Tests: 75 (15 per branch x 5 branches)
echo Check your Overview page now!
echo.
pause