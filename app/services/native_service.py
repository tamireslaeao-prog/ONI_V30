import win32gui
import win32con
import win32process
import win32api
import psutil
import subprocess
import os
import time
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from structlog import get_logger
from app.soul.types import SoulToken, ValidationSource

logger = get_logger()

class WindowInfo(BaseModel):
    hwnd: int
    title: str
    process_name: str
    pid: int
    is_visible: bool
    is_minimized: bool
    is_maximized: bool

class NativeService:
    """
    Win32 API Wrapper for "Total System Dominion" (ONI v6.2).
    Allows window manipulation, process management and shell interaction
    without relying on visual automation or mouse clicks.
    """
    
    def __init__(self):
        logger.info("native_service_initialized")

    def _validate_soul(self, token: Optional[SoulToken], action_name: str) -> None:
        """
        Enforce Axiom 5/8: Soul Validation.
        If strict mode is enabled, raises AxiomViolationError.
        """
        from app.core.config import settings
        from app.soul.exceptions import AxiomViolationError
        
        if token is None:
            msg = f"SoulToken missing for action '{action_name}'. Axiom Violation."
            if settings.safety.enforce_axioms:
                logger.error("axiom_violation_enforced", action=action_name)
                raise AxiomViolationError(msg, axiom_id=5)
            else:
                logger.warning("soul_token_missing", action=action_name, consequence="Axiom Violation Possible")
        else:
            logger.info("soul_token_verified", action=action_name, context=token.context)

    def _get_process_name(self, pid: int) -> str:
        try:
            return psutil.Process(pid).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "Unknown"

    def list_windows(self) -> List[WindowInfo]:
        """List all visible windows with their metadata."""
        windows = []

        def enum_callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            
            title = win32gui.GetWindowText(hwnd)
            if not title: # Skip untitled invisible windows
                return

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            placement = win32gui.GetWindowPlacement(hwnd)
            # placement[1] is showCmd. 
            # SW_SHOWMINIMIZED = 2, SW_SHOWMAXIMIZED = 3, SW_SHOWNORMAL = 1
            show_cmd = placement[1]
            
            windows.append(WindowInfo(
                hwnd=hwnd,
                title=title,
                process_name=self._get_process_name(pid),
                pid=pid,
                is_visible=True,
                is_minimized=(show_cmd == win32con.SW_SHOWMINIMIZED),
                is_maximized=(show_cmd == win32con.SW_SHOWMAXIMIZED)
            ))

        win32gui.EnumWindows(enum_callback, None)
        return windows

    def find_window(self, query: str) -> Optional[WindowInfo]:
        """Find a window by partial title match or exact PID."""
        windows = self.list_windows()
        query_lower = query.lower()
        
        # 1. Try match by PID if query is digit
        if query.isdigit():
            target_pid = int(query)
            for win in windows:
                if win.pid == target_pid:
                    return win
        
        # 2. Try exact process name match
        for win in windows:
            if win.process_name.lower() == query_lower:
                return win

        # 3. Try partial title match
        for win in windows:
            if query_lower in win.title.lower():
                return win
                
        return None

    def focus_window(self, query: str, token: Optional[SoulToken] = None) -> Dict[str, Any]:
        """Forces a window to foreground using Win32 API."""
        self._validate_soul(token, "focus_window")
        win = self.find_window(query)
        if not win:
            raise ValueError(f"Window not found for query: {query}")
        
        try:
            # Force restore if minimized
            if win.is_minimized:
                win32gui.ShowWindow(win.hwnd, win32con.SW_RESTORE)
            
            # This 'trick' is sometimes needed to bypass Windows foreground lock
            # Send an Alt key press to trick Windows into thinking user is active
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_EXTENDEDKEY | 0, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
            
            win32gui.SetForegroundWindow(win.hwnd)
            time.sleep(0.1) # Wait for animation
            
            return {"success": True, "message": f"Focused window: {win.title}", "hwnd": win.hwnd}
        except Exception as e:
            logger.error("focus_window_failed", error=str(e))
            raise RuntimeError(f"Failed to focus window: {str(e)}")

    def set_window_state(self, query: str, state: str) -> Dict[str, Any]:
        """Set window state: 'minimize', 'maximize', 'restore', 'close'."""
        win = self.find_window(query)
        if not win:
             raise ValueError(f"Window not found for query: {query}")
        
        cmd = None
        if state == "minimize":
            cmd = win32con.SW_MINIMIZE
        elif state == "maximize":
            cmd = win32con.SW_MAXIMIZE
        elif state == "restore":
            cmd = win32con.SW_RESTORE
        elif state == "close":
            win32gui.PostMessage(win.hwnd, win32con.WM_CLOSE, 0, 0)
            return {"success": True, "message": f"Closed window: {win.title}"}
        else:
            raise ValueError(f"Invalid state: {state}")
            
        win32gui.ShowWindow(win.hwnd, cmd)
        return {"success": True, "message": f"Set state {state} for window: {win.title}"}

    def start_process(self, command: str, args: List[str] = [], work_dir: Optional[str] = None, token: Optional[SoulToken] = None) -> Dict[str, Any]:
        """Start a process natively."""
        self._validate_soul(token, "start_process")
        try:
            full_cmd = [command] + args
            # Using Popen to not block. shell=False prevents command injection.
            proc = subprocess.Popen(full_cmd, cwd=work_dir, shell=False)
            return {
                "success": True, 
                "pid": proc.pid, 
                "message": f"Started process: {command} (PID: {proc.pid})"
            }
        except Exception as e:
             raise RuntimeError(f"Failed to start process: {str(e)}")

    def open_shell_item(self, path: str, token: Optional[SoulToken] = None) -> Dict[str, Any]:
        """Open a file or folder using native ShellExecute."""
        self._validate_soul(token, "open_shell_item")
        try:
            if not os.path.exists(path):
                # Try to resolve env vars
                path = os.path.expandvars(path)
                if not os.path.exists(path):
                     raise ValueError(f"Path does not exist: {path}")

            os.startfile(path)
            return {"success": True, "message": f"Opened shell item: {path}"}
        except Exception as e:
             raise RuntimeError(f"Failed to open shell item: {str(e)}")
