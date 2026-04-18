@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM run_tests.bat — Windows test runner for the Pose Director E2E suite
REM
REM Usage:
REM   run_tests.bat                          -> all tests, all browsers
REM   run_tests.bat smoke                    -> smoke tests, all browsers
REM   run_tests.bat summary                  -> Summary page tests, all browsers
REM   run_tests.bat judge                    -> Judge page tests, all browsers
REM   run_tests.bat crawler                  -> Crawler page tests, all browsers
REM   run_tests.bat regression               -> full regression, all browsers
REM   run_tests.bat "" chromium              -> all tests, chromium only
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0"

SET MARKER=%1
SET BROWSERS=%2
IF "%BROWSERS%"=="" SET BROWSERS=chromium firefox webkit

FOR /F "tokens=1-3 delims=/ " %%A IN ("%DATE%") DO SET DATESTAMP=%%A-%%B-%%C
FOR /F "tokens=1-3 delims=:. " %%A IN ("%TIME%") DO SET TIMESTAMP=%DATESTAMP%_%%A-%%B-%%C

echo.
echo ===========================================================
echo   Pose Director -- E2E Test Runner (Windows)
echo ===========================================================
echo   Timestamp : %TIMESTAMP%
echo   Marker    : %MARKER%
echo   Browsers  : %BROWSERS%
echo.

IF NOT EXIST "storage_state.json" (
  echo ERROR: storage_state.json not found.
  echo Run once:  python setup_auth.py
  exit /b 1
)

IF NOT EXIST "reports" mkdir reports
IF NOT EXIST "screenshots" mkdir screenshots

SET OVERALL_EXIT=0

FOR %%B IN (%BROWSERS%) DO (
  echo ----------------------------------------------------------
  echo   Browser : %%B
  echo   Report  : reports\report_%%B_%TIMESTAMP%.html
  echo ----------------------------------------------------------

  IF "%MARKER%"=="" (
    python -m pytest --browser %%B --html=reports\report_%%B_%TIMESTAMP%.html --self-contained-html -v
  ) ELSE (
    python -m pytest --browser %%B -m %MARKER% --html=reports\report_%%B_%TIMESTAMP%.html --self-contained-html -v
  )

  IF ERRORLEVEL 1 SET OVERALL_EXIT=1
  echo.
)

echo ===========================================================
echo   Reports saved in reports\
FOR %%B IN (%BROWSERS%) DO (
  echo     - reports\report_%%B_%TIMESTAMP%.html
)
echo   Screenshots in screenshots\
echo ===========================================================
echo.

exit /b %OVERALL_EXIT%
