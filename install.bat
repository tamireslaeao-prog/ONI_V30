@echo off
title ONI V30 - INSTALLATION
color 0B
cls

cd /d "%~dp0"

echo.
echo  ========================================
echo   ONI V30 - SETUP WIZARD
echo  ========================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale Python 3.10 ou superior.
    pause
    exit /b
)

echo.
echo [2/4] Atualizando PIP...
python -m pip install --upgrade pip --quiet

echo.
echo [3/4] Instalando Torch com CUDA (Critico)...
:: Insta-la versão especifica estável
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --index-url https://download.pytorch.org/whl/cu121 --quiet
pip install yt-dlp pytubefix

echo.
echo [4/4] Instalando Dependencias do ONI V30...
pip install -r requirements.txt
pip install dxcam-cpp
echo.
echo ========================================
echo   INSTALACAO V30 CONCLUIDA!
echo ========================================
echo   Execute 'run.bat' para iniciar.
pause
