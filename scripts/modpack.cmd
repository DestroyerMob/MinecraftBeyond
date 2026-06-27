@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python "%SCRIPT_DIR%..\tools\modpack.py" %*
  exit /b %ERRORLEVEL%
)

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 "%SCRIPT_DIR%..\tools\modpack.py" %*
  exit /b %ERRORLEVEL%
)

echo Python 3 was not found on PATH.
exit /b 1
