@echo off
title OmniVR Player 8K
cd /d "%~dp0"
if "%~1"=="" (
    python main.py
) else (
    python main.py "%~1"
)
pause
