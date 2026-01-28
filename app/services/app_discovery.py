import os
import winreg
import structlog
from typing import Optional, Dict
from pathlib import Path

logger = structlog.get_logger(__name__)

class AppDiscoveryService:
    """
    Service to dynamically discover application paths on Windows.
    Eliminates the need for hardcoded paths in configuration.
    """
    
    COMMON_APPS = {
        "photoshop": ["Adobe Photoshop", "Photoshop.exe"],
        "aftereffects": ["Adobe After Effects", "AfterFX.exe"],
        "blender": ["Blender Foundation", "blender.exe"],
        "chrome": ["Google", "Chrome", "Application", "chrome.exe"]
    }

    @staticmethod
    def find_executable(app_key: str) -> Optional[str]:
        """Try to find an executable path via Registry or common Program Files locations."""
        # 1. Check common Program Files locations
        program_files = [os.environ.get("ProgramFiles", "C:\\Program Files"), 
                         os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")]
        
        for base in program_files:
            search_path = Path(base)
            if app_key == "photoshop":
                # Adobe specific search
                adobe_path = search_path / "Adobe"
                if adobe_path.exists():
                    for folder in adobe_path.iterdir():
                        if "Photoshop" in folder.name:
                            exe = folder / "Photoshop.exe"
                            if exe.exists():
                                return str(exe)
            
            elif app_key == "aftereffects":
                adobe_path = search_path / "Adobe"
                if adobe_path.exists():
                    for folder in adobe_path.iterdir():
                        if "After Effects" in folder.name:
                            exe = folder / "Support Files" / "AfterFX.exe"
                            if exe.exists():
                                return str(exe)
                                
            elif app_key == "blender":
                blender_base = search_path / "Blender Foundation"
                if blender_base.exists():
                    for folder in blender_base.iterdir():
                        exe = folder / "blender.exe"
                        if exe.exists():
                            return str(exe)

        logger.warning("app_not_found", app=app_key)
        return None

    @classmethod
    def get_all_paths(cls) -> Dict[str, str]:
        """Returns a map of all discovered application paths."""
        return {app: cls.find_executable(app) for app in cls.COMMON_APPS}
