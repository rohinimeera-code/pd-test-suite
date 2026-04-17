@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM run_tests.bat — Windows test runner for the Pose Director E2E suite
REM
REM Usage:
REM   run_tests.bat              -> all tests
REM   run_tests.bat smoke        -> smoke tests
REM   run_tests.bat summary      -> Summary page tests
REM   run_tests.bat judge        -> Judge page tests
REM   run_tests.bat crawler      -> Crawler page tests
REM   run_tests.bat regression   -> full regression
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0"

SET MARKER=%1
FOR /F "tokens=1-3 delims=/ " %%A IN ("%DATE%") DO SET DATESTAMP=%%A-%%B-%%C
FOR /F "tokens=1-3 delims=:. " %%A IN ("%TIME%") DO SET TIMESTAMP=%DATESTAMP%_%%A-%%B-%%C

echo.
echo ===========================================================
echo   Pose Director -- E2E Test Runner (Windows)
echo ===========================================================
echo   Timestamp : %TIMESTAMP%
echo   Marker    : %MARKER%
echo.

IF NOT EXIST "storage_state.json" (
  echo ERROR: storage_state.json not found.
  echo Run once:  python setup_auth.py
  exit /b 1
)

IF NOT EXIST "reports" mkdir reports
IF NOT EXIST "screenshots" mkdir screenshots

IF "%MARKER%"=="" (
  python -m pytest --html=reports\report_%TIMESTAMP%.html --self-contained-html -v
) ELSE (
  python -m pytest -m %MARKER% --html=reports\report_%TIMESTAMP%.html --self-contained-html -v
)

SET EXIT_CODE=%ERRORLEVEL%

echo.
echo -----------------------------------------------------------
echo   Report saved to reports\report_%TIMESTAMP%.html
echo   Screenshots  in screenshots\
echo -----------------------------------------------------------
echo.

exit /b %EXIT_CODE%
