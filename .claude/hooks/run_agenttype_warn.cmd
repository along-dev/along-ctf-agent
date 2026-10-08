@echo off
rem ==============================================================
rem PreToolUse hook wrapper (drive-letter agnostic)
rem Warn-only: advises Explore instead of general-purpose. Never blocks.
rem ASCII-ONLY + CRLF ON PURPOSE: cmd.exe parses .cmd with the OEM
rem codepage, so UTF-8 text here would shift line parsing. Comments
rem stay ASCII. %~dp0 is this script's own directory.
rem Prefer portable Python; fall back to system python; if neither is
rem available, exit silently so the session is never blocked.
rem ==============================================================
setlocal
set "PY=%~dp0..\..\runtime\python\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%~dp0agenttype_warn.py" 2>nul
exit /b 0
