@echo off
rem ==============================================================
rem UserPromptSubmit hook wrapper (drive-letter agnostic)
rem
rem ASCII-ONLY + CRLF ON PURPOSE: cmd.exe parses .cmd files with the
rem OEM codepage (GBK here), so UTF-8 box-drawing/Chinese text in this
rem file gets mis-decoded and shifts line parsing (reproduced: cmd
rem printed garbage instead of the rem line). Comments stay ASCII.
rem
rem %~dp0 is always this script's own directory, so changing the drive
rem letter or path does not matter.
rem
rem Prefer portable Python; fall back to system python; if neither is
rem available, exit silently so the session is never blocked.
rem ==============================================================
setlocal
set "PY=%~dp0..\..\runtime\python\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0ctf_normalize.py" 2>nul
exit /b 0
