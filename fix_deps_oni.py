# -*- coding: utf-8 -*-
"""
Script para corrigir dependências do ONI_V30.

Este script tenta resolver conflitos de dependência identificados
no log fornecido, reinstalando pacotes com versões compatíveis.
"""

import subprocess
import sys
import os

def run_command(cmd_list):
    """Executa um comando shell e verifica se foi bem-sucedido."""
    print(f"[INFO] Executando: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERRO] Comando falhou: {' '.join(cmd_list)}")
        print(f"[STDERR] {result.stderr}")
        print(f"[STDOUT] {result.stdout}")
        return False
    else:
        print(f"[SUCESSO] Comando executado: {' '.join(cmd_list)}")
        print(result.stdout[-500:]) # Imprime os últimos 500 caracteres da saída
        return True

def main():
    """Função principal para resolver as dependências."""
    print("[INFO] Iniciando correção de dependências...")

    packages_to_uninstall = [
        "numpy",
        "torch",
        "torchvision",
        "torchaudio",
        "pillow",
        "huggingface-hub",
        "tokenizers",
        "transformers",
        "pytorch-lightning",
        "torchmetrics",
        "diffusers",
        "gradio",
        "bitsandbytes",
    ]

    print("[INFO] Desinstalando pacotes problemáticos...")
    for pkg in packages_to_uninstall:
        # Usar --user pode evitar problemas de permissão
        cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "--user", pkg]
        run_command(cmd) 

    # 3. Instalar versões compatíveis
    print("\n[INFO] Instalando versões compatíveis...")

    target_packages = [
        f"numpy<2.0.0", 
        f"torch==2.1.2+cu121", 
        f"torchvision==0.16.2",
        f"torchaudio==2.1.2", 
        f"pillow<11.0,>=8.0", 
        f"huggingface-hub>=0.16.4,<1.0",
        f"tokenizers==0.14.1", 
        f"transformers==4.34.1", 
        f"pytorch-lightning==2.1.2", 
        f"torchmetrics==1.8.2", 
        f"diffusers==0.20.2", 
        f"gradio==3.41.2",
        f"accelerate>=0.20.0", 
    ]

    for pkg_spec in target_packages:
        cmd = [sys.executable, "-m", "pip", "install", "--user", pkg_spec]
        if not run_command(cmd):
             print(f"[ERRO CRÍTICO] Falha ao instalar {pkg_spec}. Processo interrompido.")
             return 

    print("\n[INFO] Correção de dependências concluída.")

if __name__ == "__main__":
    main()
