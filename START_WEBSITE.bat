@echo off
cd /d "%~dp0"
echo Open http://localhost:8000 in your browser.
echo Press Ctrl+C to stop.
start "" "http://localhost:8000"
py -3 --version >nul 2>&1
if errorlevel 1 goto usepython
py -3 -m http.server 8000 --directory dist
goto end
:usepython
python -m http.server 8000 --directory dist
:end
pause
