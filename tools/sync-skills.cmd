@echo off
rem Sync the two skill copies (.claude/skills <-> skills). ASCII-only + CRLF on purpose.
setlocal
set "PY=%~dp0..\runtime\python\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0sync_skills.py" %*
endlocal
exit /b %errorlevel%
