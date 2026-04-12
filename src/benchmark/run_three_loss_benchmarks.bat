@echo off
setlocal

set SCRIPT_DIR=%~dp0
pushd "%SCRIPT_DIR%\..\.." >nul

where py >nul 2>&1
if %ERRORLEVEL%==0 (
    py -3 src\benchmark\run_three_loss_benchmarks.py
    set EXIT_CODE=%ERRORLEVEL%
    popd >nul
    exit /b %EXIT_CODE%
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
    python src\benchmark\run_three_loss_benchmarks.py
    set EXIT_CODE=%ERRORLEVEL%
    popd >nul
    exit /b %EXIT_CODE%
)

echo Error: no se encontro py ni python en PATH.
popd >nul
exit /b 1
