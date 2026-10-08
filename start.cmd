@echo off
REM Package-root anchor for the CTF workbench kit.
REM _kit_root() in .claude/hooks/ctf_normalize.py walks up to the dir holding this file.
setlocal
cd /d "%~dp0"
echo CTF workbench kit root: %CD%
endlocal
exit /b 0
