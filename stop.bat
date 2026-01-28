@echo off
echo ========================================
echo   ONI V24 - KILL SWITCH
echo ========================================
echo.
echo [AVISO] Encerrando processos python relacionados...

taskkill /F /IM python.exe /T
taskkill /F /IM uvicorn.exe /T

echo.
echo [ONI] Sistema desligado.
pause
