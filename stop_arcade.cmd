@echo off
setlocal
where py >nul 2>&1
if not errorlevel 1 goto py
where python >nul 2>&1
if not errorlevel 1 goto python
echo Codex Arcade could not find Python. Install Python 3.10+ and rerun install.py.
exit /b 1
:py
py -3 "%~dp0stop.py" --workspace "%CD%"
exit /b %errorlevel%
:python
python "%~dp0stop.py" --workspace "%CD%"
