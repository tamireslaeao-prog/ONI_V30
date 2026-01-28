"""
ONI App Finder - Version-Agnostic Software Detection
Auto-detects installed software regardless of version.

Usage:
    from oni_app_finder import AppFinder
    
    finder = AppFinder()
    blender = finder.find_blender()
    maya = finder.find_maya()
    
    # Or get all at once
    apps = finder.find_all()
    print(apps['blender']['path'])
    print(apps['maya']['version'])

Version: 1.0.0
Date: 2026-01-14
Author: ONI Team
"""

import os
import glob
import winreg
import subprocess
from typing import Optional, Dict, List, Any
import logging

import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ONI_AppFinder")

KNOWLEDGE_PATH = Path(__file__).parent / "Knowledge" / "app_paths.json"

class AppFinder:
    """
    Version-Agnostic Software Detection System
    
    Automatically finds installed applications regardless of version.
    Uses multiple detection methods:
    1. Knowledge Base (Memory) - First priority
    2. Windows Registry
    3. Common installation paths (glob patterns)
    4. PATH environment variable
    5. COM objects (for Office apps)
    """
    
    VERSION = "1.1.0 (Self-Learning)"
    
    def __init__(self, prefer_latest: bool = True):
        """
        Initialize AppFinder with Auto-Memory.
        """
        self.prefer_latest = prefer_latest
        self._cache = {}
        self._load_knowledge()

    def _load_knowledge(self):
        """Load known paths from persistent memory with SELF-HEALING."""
        try:
            if KNOWLEDGE_PATH.exists():
                with open(KNOWLEDGE_PATH, 'r') as f:
                    data = json.load(f)
                    
                    if 'apps' in data:
                        loaded_count = 0
                        healed_count = 0
                        
                        for name, info in data['apps'].items():
                            exe_path = info['path']
                            
                            # SELF-HEALING CHECK
                            if os.path.exists(exe_path):
                                # Valid memory -> Load to cache
                                self._cache[name.lower()] = {
                                    'path': str(Path(exe_path).parent),
                                    'exe': exe_path,
                                    'version': 'Known',
                                    'name': name,
                                    'args_script': info.get('args_script')
                                }
                                loaded_count += 1
                            else:
                                # Invalid memory -> Heal (Ignore)
                                logger.warning(f"Self-Healing: Triggered for {name}. Path not found: {exe_path}")
                                healed_count += 1
                                
                logger.info(f"Memory: {loaded_count} loaded, {healed_count} healed (discarded).")
        except Exception as e:
            logger.warning(f"Failed to load memory: {e}")

    def _save_knowledge(self):
        """Save current cache to persistent memory."""
        try:
            KNOWLEDGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            output = {
                "description": "ONI Knowledge Base - Known Application Paths (Auto-Learned)",
                "updated_at": "Auto-Generated",
                "apps": {}
            }
            
            for key, val in self._cache.items():
                if val and 'exe' in val:
                    # Map generic keys to proper names
                    name_map = {
                        'blender': 'Blender', 'maya': 'Maya', 'autocad': 'AutoCAD',
                        'photoshop': 'Photoshop', 'after_effects': 'AfterEffects',
                        'illustrator': 'Illustrator', 'coreldraw': 'CorelDRAW',
                        'excel': 'Excel', 'word': 'Word', 'chrome': 'Chrome',
                        'foxit': 'Foxit'
                    }
                    proper_name = name_map.get(key, val['name'])
                    
                    output['apps'][proper_name] = {
                        "path": val['exe'],
                        "args_script": val.get('args_script', None) # Future support
                    }
            
            with open(KNOWLEDGE_PATH, 'w') as f:
                json.dump(output, f, indent=2)
            logger.info("Memory consolidated successfully.")
            
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    # =========================================================================
    # BLENDER
    # =========================================================================
    
    def find_blender(self) -> Optional[Dict[str, Any]]:
        """
        Find Blender installation.
        
        Returns:
            Dict with 'path', 'version', 'exe' or None if not found
        """
        if 'blender' in self._cache:
            return self._cache['blender']
        
        result = None
        
        # Method 1: Common paths (Windows)
        base_paths = [
            r"C:\Program Files\Blender Foundation",
            r"C:\Program Files (x86)\Blender Foundation",
            os.path.expanduser(r"~\AppData\Roaming\Blender Foundation"),
        ]
        
        for base in base_paths:
            if os.path.exists(base):
                folders = glob.glob(os.path.join(base, "Blender *"))
                
                if folders:
                    # Sort by version (extract number)
                    def get_version(path):
                        name = os.path.basename(path)
                        try:
                            return float(name.replace("Blender ", "").split()[0])
                        except:
                            return 0
                    
                    folders.sort(key=get_version, reverse=self.prefer_latest)
                    
                    for folder in folders:
                        exe = os.path.join(folder, "blender.exe")
                        if os.path.exists(exe):
                            version = os.path.basename(folder).replace("Blender ", "")
                            result = {
                                'path': folder,
                                'exe': exe,
                                'version': version,
                                'name': 'Blender'
                            }
                            break
                
                if result:
                    break
        
        # Method 2: PATH environment
        if not result:
            try:
                output = subprocess.check_output(['where', 'blender'], 
                                                stderr=subprocess.DEVNULL,
                                                text=True)
                exe = output.strip().split('\n')[0]
                if os.path.exists(exe):
                    result = {
                        'path': os.path.dirname(exe),
                        'exe': exe,
                        'version': 'Unknown',
                        'name': 'Blender'
                    }
            except:
                pass
        
        self._cache['blender'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # MAYA
    # =========================================================================
    
    def find_maya(self) -> Optional[Dict[str, Any]]:
        """
        Find Maya installation.
        
        Returns:
            Dict with 'path', 'version', 'exe' or None if not found
        """
        if 'maya' in self._cache:
            return self._cache['maya']
        
        result = None
        
        # Method 1: Registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Autodesk\Maya")
            versions = []
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(key, i)
                    if subkey.isdigit() or '.' in subkey:
                        versions.append(subkey)
                    i += 1
                except:
                    break
            
            if versions:
                versions.sort(reverse=self.prefer_latest)
                
                for ver in versions:
                    try:
                        ver_key = winreg.OpenKey(key, ver)
                        install_path = winreg.QueryValueEx(ver_key, 
                                                          "MAYA_INSTALL_LOCATION")[0]
                        exe = os.path.join(install_path, "bin", "maya.exe")
                        
                        if os.path.exists(exe):
                            result = {
                                'path': install_path,
                                'exe': exe,
                                'version': ver,
                                'name': 'Maya'
                            }
                            break
                    except:
                        continue
        except:
            pass
        
        # Method 2: Common paths
        if not result:
            base = r"C:\Program Files\Autodesk"
            if os.path.exists(base):
                folders = glob.glob(os.path.join(base, "Maya*"))
                
                def get_year(path):
                    name = os.path.basename(path)
                    try:
                        return int(''.join(filter(str.isdigit, name)))
                    except:
                        return 0
                
                folders.sort(key=get_year, reverse=self.prefer_latest)
                
                for folder in folders:
                    exe = os.path.join(folder, "bin", "maya.exe")
                    if os.path.exists(exe):
                        version = os.path.basename(folder).replace("Maya", "").strip()
                        result = {
                            'path': folder,
                            'exe': exe,
                            'version': version,
                            'name': 'Maya'
                        }
                        break
        
        self._cache['maya'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # AUTOCAD
    # =========================================================================
    
    def find_autocad(self) -> Optional[Dict[str, Any]]:
        """
        Find AutoCAD installation.
        
        Returns:
            Dict with 'path', 'version', 'exe' or None if not found
        """
        if 'autocad' in self._cache:
            return self._cache['autocad']
        
        result = None
        
        # Method 1: Registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Autodesk\AutoCAD")
            versions = []
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(key, i)
                    versions.append(subkey)
                    i += 1
                except:
                    break
            
            if versions:
                versions.sort(reverse=self.prefer_latest)
                
                for ver in versions:
                    try:
                        ver_key = winreg.OpenKey(key, ver)
                        # AutoCAD has nested keys
                        j = 0
                        while True:
                            try:
                                product = winreg.EnumKey(ver_key, j)
                                prod_key = winreg.OpenKey(ver_key, product)
                                install_path = winreg.QueryValueEx(prod_key, 
                                                                  "AcadLocation")[0]
                                exe = os.path.join(install_path, "acad.exe")
                                
                                if os.path.exists(exe):
                                    result = {
                                        'path': install_path,
                                        'exe': exe,
                                        'version': ver,
                                        'name': 'AutoCAD'
                                    }
                                    break
                                j += 1
                            except:
                                break
                        
                        if result:
                            break
                    except:
                        continue
        except:
            pass
        
        # Method 2: Common paths
        if not result:
            base = r"C:\Program Files\Autodesk"
            if os.path.exists(base):
                folders = glob.glob(os.path.join(base, "AutoCAD *"))
                
                def get_year(path):
                    name = os.path.basename(path)
                    try:
                        return int(''.join(filter(str.isdigit, name)))
                    except:
                        return 0
                
                folders.sort(key=get_year, reverse=self.prefer_latest)
                
                for folder in folders:
                    exe = os.path.join(folder, "acad.exe")
                    if os.path.exists(exe):
                        version = os.path.basename(folder).replace("AutoCAD ", "")
                        result = {
                            'path': folder,
                            'exe': exe,
                            'version': version,
                            'name': 'AutoCAD'
                        }
                        break
        
        self._cache['autocad'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # PHOTOSHOP
    # =========================================================================
    
    def find_photoshop(self) -> Optional[Dict[str, Any]]:
        """
        Find Photoshop installation.
        
        Returns:
            Dict with 'path', 'version', 'exe' or None if not found
        """
        if 'photoshop' in self._cache:
            return self._cache['photoshop']
        
        result = None
        
        # Method 1: Common paths (Adobe CC)
        bases = [
            r"C:\Program Files\Adobe",
            r"C:\Program Files (x86)\Adobe",
        ]
        
        for base in bases:
            if os.path.exists(base):
                folders = glob.glob(os.path.join(base, "Adobe Photoshop *"))
                
                def get_year(path):
                    name = os.path.basename(path)
                    try:
                        # Extract year (2024, 2025, etc.)
                        return int(''.join(filter(str.isdigit, name)))
                    except:
                        return 0
                
                folders.sort(key=get_year, reverse=self.prefer_latest)
                
                for folder in folders:
                    exe = os.path.join(folder, "Photoshop.exe")
                    if os.path.exists(exe):
                        version = os.path.basename(folder).replace("Adobe Photoshop ", "")
                        result = {
                            'path': folder,
                            'exe': exe,
                            'version': version,
                            'name': 'Photoshop'
                        }
                        break
            
            if result:
                break
        
        self._cache['photoshop'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # AFTER EFFECTS
    # =========================================================================
    
    def find_after_effects(self) -> Optional[Dict[str, Any]]:
        """
        Find After Effects installation.
        
        Returns:
            Dict with 'path', 'version', 'exe' or None if not found
        """
        if 'after_effects' in self._cache:
            return self._cache['after_effects']
        
        result = None
        
        bases = [
            r"C:\Program Files\Adobe",
            r"C:\Program Files (x86)\Adobe",
        ]
        
        for base in bases:
            if os.path.exists(base):
                folders = glob.glob(os.path.join(base, "Adobe After Effects *"))
                
                def get_year(path):
                    name = os.path.basename(path)
                    try:
                        return int(''.join(filter(str.isdigit, name)))
                    except:
                        return 0
                
                folders.sort(key=get_year, reverse=self.prefer_latest)
                
                for folder in folders:
                    exe = os.path.join(folder, "Support Files", "AfterFX.exe")
                    if os.path.exists(exe):
                        version = os.path.basename(folder).replace("Adobe After Effects ", "")
                        result = {
                            'path': folder,
                            'exe': exe,
                            'version': version,
                            'name': 'After Effects'
                        }
                        break
            
            if result:
                break
        
        self._cache['after_effects'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # ILLUSTRATOR
    # =========================================================================
    
    def find_illustrator(self) -> Optional[Dict[str, Any]]:
        """Find Adobe Illustrator installation."""
        if 'illustrator' in self._cache:
            return self._cache['illustrator']
        
        result = None
        
        bases = [r"C:\Program Files\Adobe", r"C:\Program Files (x86)\Adobe"]
        
        for base in bases:
            if os.path.exists(base):
                folders = glob.glob(os.path.join(base, "Adobe Illustrator *"))
                folders.sort(reverse=self.prefer_latest)
                
                for folder in folders:
                    exe = os.path.join(folder, "Support Files", "Contents", 
                                      "Windows", "Illustrator.exe")
                    if os.path.exists(exe):
                        version = os.path.basename(folder).replace("Adobe Illustrator ", "")
                        result = {
                            'path': folder,
                            'exe': exe,
                            'version': version,
                            'name': 'Illustrator'
                        }
                        break
            
            if result:
                break
        
        self._cache['illustrator'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # CORELDRAW
    # =========================================================================
    
    def find_coreldraw(self) -> Optional[Dict[str, Any]]:
        """Find CorelDRAW installation."""
        if 'coreldraw' in self._cache:
            return self._cache['coreldraw']
        
        result = None
        
        base = r"C:\Program Files\Corel"
        if os.path.exists(base):
            folders = glob.glob(os.path.join(base, "CorelDRAW Graphics Suite *"))
            folders.sort(reverse=self.prefer_latest)
            
            for folder in folders:
                # Try different possible exe locations
                exe_paths = [
                    os.path.join(folder, "Programs64", "CorelDRW.exe"),
                    os.path.join(folder, "Programs", "CorelDRW.exe"),
                ]
                
                for exe in exe_paths:
                    if os.path.exists(exe):
                        version = os.path.basename(folder).replace(
                            "CorelDRAW Graphics Suite ", "")
                        result = {
                            'path': folder,
                            'exe': exe,
                            'version': version,
                            'name': 'CorelDRAW'
                        }
                        break
                
                if result:
                    break
        
        self._cache['coreldraw'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # EXCEL
    # =========================================================================
    
    def find_excel(self) -> Optional[Dict[str, Any]]:
        """Find Microsoft Excel installation."""
        if 'excel' in self._cache:
            return self._cache['excel']
        
        result = None
        
        # Try via COM object
        try:
            import win32com.client
            excel = win32com.client.Dispatch("Excel.Application")
            version = excel.Version
            path = excel.Path
            excel.Quit()
            
            result = {
                'path': path,
                'exe': os.path.join(path, "EXCEL.EXE"),
                'version': version,
                'name': 'Excel'
            }
        except:
            pass
        
        # Fallback: Common paths
        if not result:
            bases = [
                r"C:\Program Files\Microsoft Office",
                r"C:\Program Files (x86)\Microsoft Office",
            ]
            
            for base in bases:
                if os.path.exists(base):
                    folders = glob.glob(os.path.join(base, "root", "Office*"))
                    folders.sort(reverse=self.prefer_latest)
                    
                    for folder in folders:
                        exe = os.path.join(folder, "EXCEL.EXE")
                        if os.path.exists(exe):
                            version = os.path.basename(folder).replace("Office", "")
                            result = {
                                'path': folder,
                                'exe': exe,
                                'version': version,
                                'name': 'Excel'
                            }
                            break
                
                if result:
                    break
        
        self._cache['excel'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # WORD
    # =========================================================================
    
    def find_word(self) -> Optional[Dict[str, Any]]:
        """Find Microsoft Word installation."""
        if 'word' in self._cache:
            return self._cache['word']
        
        result = None
        
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            version = word.Version
            path = word.Path
            word.Quit()
            
            result = {
                'path': path,
                'exe': os.path.join(path, "WINWORD.EXE"),
                'version': version,
                'name': 'Word'
            }
        except:
            pass
        
        self._cache['word'] = result
        if result: self._save_knowledge()
        return result
    
    # =========================================================================
    # FIND ALL
    # =========================================================================
    
    def find_all(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Find all supported applications.
        
        Returns:
            Dict with app names as keys and info dicts as values
        """
        return {
            'blender': self.find_blender(),
            'maya': self.find_maya(),
            'autocad': self.find_autocad(),
            'photoshop': self.find_photoshop(),
            'premiere': self.find_premiere(),
            'after_effects': self.find_after_effects(),
            'illustrator': self.find_illustrator(),
            'coreldraw': self.find_coreldraw(),
            'excel': self.find_excel(),
            'word': self.find_word(),
            'foxit': self.find_foxit(),
            'acrobat': self.find_acrobat(),
            'chrome': self.find_chrome(),
        }

    # =========================================================================
    # PREMIERE
    # =========================================================================

    def find_premiere(self) -> Optional[Dict[str, Any]]:
        """Find Adobe Premiere Pro installation."""
        if 'premiere' in self._cache:
            return self._cache['premiere']
        
        result = None
        bases = [r"C:\Program Files\Adobe", r"C:\Program Files (x86)\Adobe"]
        
        for base in bases:
            if os.path.exists(base):
                folders = glob.glob(os.path.join(base, "Adobe Premiere Pro *"))
                folders.sort(reverse=self.prefer_latest)
                
                for folder in folders:
                    exe = os.path.join(folder, "Adobe Premiere Pro.exe")
                    if os.path.exists(exe):
                        version = os.path.basename(folder).replace("Adobe Premiere Pro ", "")
                        result = {
                            'path': folder,
                            'exe': exe,
                            'version': version,
                            'name': 'Premiere Pro'
                        }
                        break
            if result: break
            
        self._cache['premiere'] = result
        if result: self._save_knowledge()
        return result

    # =========================================================================
    # FOXIT
    # =========================================================================

    def find_foxit(self) -> Optional[Dict[str, Any]]:
        """Find Foxit PDF Reader/Editor."""
        if 'foxit' in self._cache:
            return self._cache['foxit']
        
        result = None
        
        # Registry Check
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Foxit Software")
            # This requires recursive search usually, let's keep it simple for now or use common paths
        except:
            pass
            
        # Common Paths
        candidates = [
            r"C:\Program Files\Foxit Software\Foxit PDF Reader\FoxitPDFReader.exe",
            r"C:\Program Files (x86)\Foxit Software\Foxit PDF Reader\FoxitPDFReader.exe",
            r"C:\Program Files\Foxit Software\Foxit PDF Editor\FoxitPDFEditor.exe"
        ]
        
        for exe in candidates:
            if os.path.exists(exe):
                result = {
                    'path': os.path.dirname(exe),
                    'exe': exe,
                    'version': 'Unknown',
                    'name': 'Foxit PDF'
                }
                break
                
        self._cache['foxit'] = result
        if result: self._save_knowledge()
        return result

    # =========================================================================
    # CHROME
    # =========================================================================

    def find_chrome(self) -> Optional[Dict[str, Any]]:
        """Find Google Chrome."""
        if 'chrome' in self._cache:
            return self._cache['chrome']
            
        result = None
        
        # Registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
            exe = winreg.QueryValue(key, None)
            if exe and os.path.exists(exe):
                result = {
                    'path': os.path.dirname(exe),
                    'exe': exe,
                    'version': 'Latest',
                    'name': 'Chrome'
                }
        except:
            pass
            
        if not result:
            candidates = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
            for exe in candidates:
                if os.path.exists(exe):
                    result = {
                        'path': os.path.dirname(exe),
                        'exe': exe,
                        'version': 'Latest',
                        'name': 'Chrome'
                    }
                    break
                    
        self._cache['chrome'] = result
        if result: self._save_knowledge()
        return result

    # =========================================================================
    # ACROBAT
    # =========================================================================

    def find_acrobat(self) -> Optional[Dict[str, Any]]:
        """Find Adobe Acrobat."""
        if 'acrobat' in self._cache:
            return self._cache['acrobat']
            
        result = None
        
        # Registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Acrobat.exe")
            exe = winreg.QueryValue(key, None)
            if exe and os.path.exists(exe):
                result = {
                    'path': os.path.dirname(exe),
                    'exe': exe,
                    'version': 'Unknown',
                    'name': 'Acrobat'
                }
        except:
            pass
            
        if not result:
             # Common paths
            bases = [r"C:\Program Files\Adobe", r"C:\Program Files (x86)\Adobe"]
            for base in bases:
                if os.path.exists(base):
                    folders = glob.glob(os.path.join(base, "Acrobat *"))
                    for folder in folders:
                        exe = os.path.join(folder, "Acrobat", "Acrobat.exe")
                        if os.path.exists(exe):
                            result = {
                                'path': os.path.dirname(exe),
                                'exe': exe,
                                'version': 'Unknown',
                                'name': 'Acrobat'
                            }
                            break
                if result: break
        
        self._cache['acrobat'] = result
        if result: self._save_knowledge()
        return result
    
    def print_all(self) -> None:
        """Print all found applications."""
        apps = self.find_all()
        
        print("\n" + "="*70)
        print("  ONI APP FINDER - Installed Applications")
        print("="*70)
        
        for name, info in apps.items():
            if info:
                print(f"\n  ✓ {info['name']} {info['version']}")
                print(f"    Path: {info['exe']}")
            else:
                print(f"\n  ✗ {name.title()} - Not found")
        
        print("\n" + "="*70)
    
    def clear_cache(self) -> None:
        """Clear cached results."""
        self._cache = {}


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

def get_blender_exe() -> Optional[str]:
    """Get Blender executable path."""
    result = AppFinder().find_blender()
    return result['exe'] if result else None

def get_maya_exe() -> Optional[str]:
    """Get Maya executable path."""
    result = AppFinder().find_maya()
    return result['exe'] if result else None

def get_autocad_exe() -> Optional[str]:
    """Get AutoCAD executable path."""
    result = AppFinder().find_autocad()
    return result['exe'] if result else None

def get_photoshop_exe() -> Optional[str]:
    """Get Photoshop executable path."""
    result = AppFinder().find_photoshop()
    return result['exe'] if result else None

def get_after_effects_exe() -> Optional[str]:
    """Get After Effects executable path."""
    result = AppFinder().find_after_effects()
    return result['exe'] if result else None


# ==============================================================================
# STANDALONE TEST
# ==============================================================================

if __name__ == "__main__":
    finder = AppFinder(prefer_latest=True)
    finder.print_all()
