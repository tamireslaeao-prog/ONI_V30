"""
ONI v5.0 - Windows Routines
System-level and application management routines for Windows.
"""

import asyncio
from typing import Any

import structlog

from .base import RoutinesBase

logger = structlog.get_logger(__name__)


class WindowsRoutines(RoutinesBase):
    """Windows system routines: apps, documents, explorer, system operations."""
    
    # =========================================================================
    # APPLICATION MANAGEMENT
    # =========================================================================
    
    async def open_app(self, app_name: str, wait_time: float = 2.0) -> bool:
        """Open application - uses registry for known apps, else Start Menu."""
        if not self._keyboard:
            return False
        
        try:
            from app.agent.app_registry import get_app_path, is_system_tool
            
            app_path = get_app_path(app_name)
            
            if app_path and not is_system_tool(app_name):
                logger.info("routine_open_app_direct", app=app_name, path=app_path)
                await self._keyboard.hotkey("win", "r")
                await asyncio.sleep(0.4)
                await self._keyboard.type_text(f'"{app_path}"')
                await asyncio.sleep(0.2)
                await self._keyboard.hotkey("enter")
                await asyncio.sleep(wait_time)
                return True
            elif app_path and is_system_tool(app_name):
                logger.info("routine_open_app_system", app=app_name, cmd=app_path)
                await self._keyboard.hotkey("win", "r")
                await asyncio.sleep(0.4)
                await self._keyboard.type_text(app_path)
                await asyncio.sleep(0.2)
                await self._keyboard.hotkey("enter")
                await asyncio.sleep(wait_time)
                return True
            else:
                logger.info("routine_open_app_search", app=app_name)
                await self._keyboard.hotkey("win")
                await asyncio.sleep(0.8)
                await self._keyboard.type_text(app_name)
                await asyncio.sleep(0.5)
                await self._keyboard.hotkey("enter")
                await asyncio.sleep(wait_time)
                return True
                
        except ImportError:
            await self._keyboard.hotkey("win")
            await asyncio.sleep(0.8)
            await self._keyboard.type_text(app_name)
            await asyncio.sleep(0.5)
            await self._keyboard.hotkey("enter")
            await asyncio.sleep(wait_time)
            logger.info("routine_open_app_fallback", app=app_name)
            return True
        except Exception as e:
            logger.error("routine_failed", routine="open_app", error=str(e))
            return False
    
    async def run_command(self, command: str) -> bool:
        """Execute command via Win+R."""
        if not self._keyboard:
            return False
        try:
            await self._keyboard.hotkey("win", "r")
            await asyncio.sleep(0.5)
            await self._keyboard.type_text(command)
            await asyncio.sleep(0.1)
            await self._keyboard.hotkey("enter")
            await asyncio.sleep(1.0)
            return True
        except Exception as e:
            logger.error("routine_failed", routine="run_command", error=str(e))
            return False
    
    # Window management
    async def close_window(self) -> bool:
        """Close active window (Alt+F4)."""
        return await self.press_keys("alt", "F4")
    
    async def minimize_window(self) -> bool:
        """Minimize window (Win+Down)."""
        return await self.press_keys("win", "down")
    
    async def maximize_window(self) -> bool:
        """Maximize window (Win+Up)."""
        return await self.press_keys("win", "up")
    
    async def restore_window(self) -> bool:
        """Restore maximized window (Win+Down)."""
        return await self.press_keys("win", "down")
    
    async def snap_left(self) -> bool:
        """Snap window to left (Win+Left)."""
        return await self.press_keys("win", "left")
    
    async def snap_right(self) -> bool:
        """Snap window to right (Win+Right)."""
        return await self.press_keys("win", "right")
    
    async def switch_window(self) -> bool:
        """Switch between windows (Alt+Tab)."""
        return await self.press_keys("alt", "tab")
    
    async def show_desktop(self) -> bool:
        """Show/hide desktop (Win+D)."""
        return await self.press_keys("win", "d")
    
    async def task_view(self) -> bool:
        """Task view (Win+Tab)."""
        return await self.press_keys("win", "tab")
    
    # =========================================================================
    # DOCUMENT OPERATIONS
    # =========================================================================
    
    async def new_document(self) -> bool:
        """New document (Ctrl+N)."""
        return await self.press_keys("ctrl", "n")
    
    async def open_file(self) -> bool:
        """Open file (Ctrl+O)."""
        return await self.press_keys("ctrl", "o")
    
    async def save(self) -> bool:
        """Save document (Ctrl+S)."""
        return await self.press_keys("ctrl", "s")
    
    async def save_as(self) -> bool:
        """Save as (Ctrl+Shift+S)."""
        return await self.press_keys("ctrl", "shift", "s")
    
    async def print_doc(self) -> bool:
        """Print (Ctrl+P)."""
        return await self.press_keys("ctrl", "p")
    
    async def close_tab(self) -> bool:
        """Close tab (Ctrl+W)."""
        return await self.press_keys("ctrl", "w")
    
    async def new_tab(self) -> bool:
        """New tab (Ctrl+T)."""
        return await self.press_keys("ctrl", "t")
    
    async def reopen_tab(self) -> bool:
        """Reopen last closed tab (Ctrl+Shift+T)."""
        return await self.press_keys("ctrl", "shift", "t")
    
    async def next_tab(self) -> bool:
        """Next tab (Ctrl+Tab)."""
        return await self.press_keys("ctrl", "tab")
    
    async def prev_tab(self) -> bool:
        """Previous tab (Ctrl+Shift+Tab)."""
        return await self.press_keys("ctrl", "shift", "tab")
    
    # =========================================================================
    # EDIT OPERATIONS
    # =========================================================================
    
    async def select_all(self) -> bool:
        """Select all (Ctrl+A)."""
        return await self.press_keys("ctrl", "a")
    
    async def copy(self) -> bool:
        """Copy (Ctrl+C)."""
        return await self.press_keys("ctrl", "c")
    
    async def paste(self) -> bool:
        """Paste (Ctrl+V)."""
        return await self.press_keys("ctrl", "v")
    
    async def paste_plain(self) -> bool:
        """Paste without formatting (Ctrl+Shift+V)."""
        return await self.press_keys("ctrl", "shift", "v")
    
    async def cut(self) -> bool:
        """Cut (Ctrl+X)."""
        return await self.press_keys("ctrl", "x")
    
    async def undo(self) -> bool:
        """Undo (Ctrl+Z)."""
        return await self.press_keys("ctrl", "z")
    
    async def redo(self) -> bool:
        """Redo (Ctrl+Y)."""
        return await self.press_keys("ctrl", "y")
    
    async def redo_alt(self) -> bool:
        """Redo alternative (Ctrl+Shift+Z)."""
        return await self.press_keys("ctrl", "shift", "z")
    
    async def find(self) -> bool:
        """Find (Ctrl+F)."""
        return await self.press_keys("ctrl", "f")
    
    async def replace(self) -> bool:
        """Find and replace (Ctrl+H)."""
        return await self.press_keys("ctrl", "h")
    
    # =========================================================================
    # FILE EXPLORER
    # =========================================================================
    
    async def open_explorer(self, path: str = None) -> bool:
        """Open File Explorer (Win+E or with path)."""
        if path:
            return await self.run_command(f'explorer "{path}"')
        return await self.press_keys("win", "e")
    
    async def new_folder(self) -> bool:
        """Create new folder (Ctrl+Shift+N)."""
        return await self.press_keys("ctrl", "shift", "n")
    
    async def rename(self) -> bool:
        """Rename (F2)."""
        return await self.press_keys("F2")
    
    async def delete(self) -> bool:
        """Delete to Recycle Bin."""
        return await self.press_keys("delete")
    
    async def delete_permanent(self) -> bool:
        """Delete permanently (Shift+Delete)."""
        return await self.press_keys("shift", "delete")
    
    async def refresh(self) -> bool:
        """Refresh (F5)."""
        return await self.press_keys("F5")
    
    async def properties(self) -> bool:
        """Properties (Alt+Enter)."""
        return await self.press_keys("alt", "enter")
    
    async def address_bar(self) -> bool:
        """Address bar (Alt+D)."""
        return await self.press_keys("alt", "d")
    
    async def context_menu(self) -> bool:
        """Context menu (Shift+F10)."""
        return await self.press_keys("shift", "F10")
    
    async def preview_pane(self) -> bool:
        """Preview pane (Alt+P)."""
        return await self.press_keys("alt", "p")
    
    async def details_pane(self) -> bool:
        """Details pane (Alt+Shift+P)."""
        return await self.press_keys("alt", "shift", "p")
    
    # =========================================================================
    # SYSTEM OPERATIONS
    # =========================================================================
    
    async def lock_screen(self) -> bool:
        """Lock computer (Win+L)."""
        return await self.press_keys("win", "l")
    
    async def task_manager(self) -> bool:
        """Task Manager (Ctrl+Shift+Esc)."""
        return await self.press_keys("ctrl", "shift", "esc")
    
    async def settings(self) -> bool:
        """Settings (Win+I)."""
        return await self.press_keys("win", "i")
    
    async def action_center(self) -> bool:
        """Action Center (Win+A)."""
        return await self.press_keys("win", "a")
    
    async def search(self) -> bool:
        """Windows Search (Win+S)."""
        return await self.press_keys("win", "s")
    
    async def screenshot_full(self) -> bool:
        """Full screenshot (Win+PrintScreen)."""
        return await self.press_keys("win", "printscreen")
    
    async def screenshot_area(self) -> bool:
        """Area screenshot (Win+Shift+S)."""
        return await self.press_keys("win", "shift", "s")
    
    async def screenshot_window(self) -> bool:
        """Window screenshot (Alt+PrintScreen)."""
        return await self.press_keys("alt", "printscreen")
    
    async def open_cmd(self) -> bool:
        """Open Command Prompt."""
        return await self.open_app("cmd")
    
    async def open_cmd_admin(self) -> bool:
        """Open CMD as Admin."""
        if not self._keyboard:
            return False
        try:
            await self._keyboard.hotkey("win")
            await asyncio.sleep(0.5)
            await self._keyboard.type_text("cmd")
            await asyncio.sleep(0.3)
            await self._keyboard.hotkey("ctrl", "shift", "enter")
            await asyncio.sleep(1.0)
            return True
        except Exception as e:
            logger.error("routine_failed", routine="open_cmd_admin", error=str(e))
            return False
    
    async def open_powershell(self) -> bool:
        """Open PowerShell."""
        return await self.open_app("powershell")
    
    async def open_regedit(self) -> bool:
        """Open Registry Editor."""
        return await self.run_command("regedit")
    
    async def open_services(self) -> bool:
        """Open Windows Services."""
        return await self.run_command("services.msc")
    
    async def open_msinfo(self) -> bool:
        """Open System Information."""
        return await self.run_command("msinfo32")
    
    async def open_winver(self) -> bool:
        """Open Windows Version."""
        return await self.run_command("winver")
    
    async def open_steps_recorder(self) -> bool:
        """Open Steps Recorder."""
        return await self.run_command("psr")
    
    async def clean_temp(self) -> bool:
        """Open temp folder."""
        return await self.run_command("temp")
    
    async def clean_temp_user(self) -> bool:
        """Open user temp folder."""
        return await self.run_command("%temp%")
    
    # =========================================================================
    # ZOOM
    # =========================================================================
    
    async def zoom_in(self) -> bool:
        """Zoom in (Ctrl++)."""
        return await self.press_keys("ctrl", "plus")
    
    async def zoom_out(self) -> bool:
        """Zoom out (Ctrl+-)."""
        return await self.press_keys("ctrl", "minus")
    
    async def zoom_reset(self) -> bool:
        """Reset zoom (Ctrl+0)."""
        return await self.press_keys("ctrl", "0")
