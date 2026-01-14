@echo off
echo ========================================
echo  LLMSecGuard Quick Benchmark
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
python manage.py runbenchmark --model 4 --limit 5 --branch DR

echo.
echo ========================================
echo  QUICK BENCHMARK COMPLETED!
echo ========================================
echo.
echo Total Tests: 5 (1 branch x 5 cases)
echo Check your Overview page now!
echo.
pause
