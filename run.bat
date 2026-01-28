@echo off
title ONI V28 - ONE CLICK START
color 0A
cls

echo.
echo  ========================================
echo   ONI V28 - MASTER LAUNCHER
echo  ========================================
echo.

:: Define Root as current directory
set ONI_ROOT=%~dp0
cd /d "%ONI_ROOT%"

:: Python Check
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    pause
    exit /b
)

:: Handover to Python Orchestrator
echo [INFO] Handing over to run.py Orchestrator...
python run.py

echo.
echo [INFO] Sessions closed.
pause
