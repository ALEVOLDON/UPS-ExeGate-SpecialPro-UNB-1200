@echo off
setlocal
title ExeGate UNB-1200 UPS Monitor

rem Always use the folder where this .bat lives (portable)
cd /d "%~dp0"

rem Prefer Windows Python launcher, then python on PATH
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 desktop_app.py
  goto :finish
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python desktop_app.py
  goto :finish
)

echo.
echo [!] Python not found.
echo     Install Python 3 and ensure "py" or "python" is on PATH.
echo     Or run:  pip install -r requirements.txt
echo.
pause
exit /b 1

:finish
if errorlevel 1 (
  echo.
  echo [!] Application exited with an error.
  pause
)
endlocal
