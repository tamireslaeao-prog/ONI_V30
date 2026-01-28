@echo off
title ONI V24 - DEEP CLEAN
color 0E

echo [ONI] Limpando Cache e Temporarios...
echo.

:: Limpar __pycache__ em toda a arvore
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"


echo [ONI] Limpeza concluida.
pause
