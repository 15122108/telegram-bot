@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 bot.py
  pause
  exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
  python bot.py
  pause
  exit /b
)

set "CODEX_PY=C:\Users\acer\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%CODEX_PY%" (
  "%CODEX_PY%" bot.py
  pause
  exit /b
)

echo Python topilmadi. Python 3 o'rnating yoki PATH sozlang.
pause
