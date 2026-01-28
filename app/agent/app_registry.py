"""
ONI v5.0 - Application Registry

Resolves application names to their executable paths on Windows.
Provides a unified way to locate installed applications across:
- System PATH
- Known installation locations
- Windows Registry (App Paths)

Usage:
    from app.agent.app_registry import get_app_path, is_system_tool
    
    path = get_app_path("photoshop")  # Returns full path or None
    is_sys = is_system_tool("notepad")  # Returns True for system tools

Supported applications:
- System tools: notepad, calc, cmd, powershell, explorer, mspaint
- Browsers: chrome, firefox
- Creative: photoshop, coreldraw, vscode
- And more via KNOWN_APPS dict
"""

import os
import shutil
import winreg
from typing import Optional
from functools import lru_cache
KNOWN_APPS = {
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "mspaint": "mspaint.exe",
    "calculator": "calc.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "explorer": "explorer.exe",
    "vscode": ["code.exe", "Code.exe"],
    "chrome": ["chrome.exe", "Google Chrome"],
    "firefox": ["firefox.exe", "Mozilla Firefox"],
    "photoshop": ["Photoshop.exe"],
    "coreldraw": ["CorelDRW.exe"],
}

SYSTEM_TOOLS = {"cmd", "powershell", "explorer", "notepad", "calc", "calculator", "mspaint"}

@lru_cache(maxsize=32)
def get_app_path(app_name: str) -> Optional[str]:
    """
    Resolves the executable path for a given application name.
    """
    app_name = app_name.lower()
    
    # 1. Direct match in PATH
    if shutil.which(app_name):
        return app_name
        
    # 2. Known apps lookup
    targets = KNOWN_APPS.get(app_name)
    if not targets:
        return None
        
    if isinstance(targets, str):
        targets = [targets]
        
    for target in targets:
        # Check PATH again for target name
        path = shutil.which(target)
        if path:
            return path
            
        # Check Common Program Files locations
        common_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Microsoft VS Code", "Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe",
            r"C:\Program Files\Adobe\Adobe Photoshop 2023\Photoshop.exe",
            r"C:\Program Files\Corel\CorelDRAW Graphics Suite 2024\Programs64\CorelDRW.exe",
        ]
        
        for common_path in common_paths:
            if os.path.exists(common_path) and target.lower() in common_path.lower():
                return common_path

    # 3. Registry Fallback (Simplified)
    # This could be expanded to search HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths
    
    return None

def is_system_tool(app_name: str) -> bool:
    """Returns True if the app is a built-in system tool."""
    return app_name.lower() in SYSTEM_TOOLS
