@echo off
cd /d "%~dp0"
py gui.py
if errorlevel 1 (
    echo.
    echo Nie udalo sie uruchomic GUI. Sprawdz czy Python jest zainstalowany.
    pause
)
