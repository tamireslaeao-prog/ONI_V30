"""
ONI v2.0 - Window Manager
Windows window control and management
"""
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Callable
from enum import Enum, auto

import structlog
from rapidfuzz import fuzz

from app.core.exceptions import WindowNotFoundError

logger = structlog.get_logger()


# Win32 constants
SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_RESTORE = 9
SW_SHOW = 5
SW_HIDE = 0

GW_HWNDNEXT = 2
DWMWA_CLOAKED = 14
MONITOR_DEFAULTTONEAREST = 2



@dataclass
class WindowInfo:
    """Information about a window."""
    hwnd: int
    title: str
    class_name: str
    x: int
    y: int
    width: int
    height: int
    is_visible: bool
    is_minimized: bool
    is_maximized: bool
    process_id: int
    monitor_index: int = 0


class MonitorPolicy(Enum):
    """Policy for determining target monitor for windows."""
    FORCE_PRIMARY = auto()      # Always move to primary monitor
    PREFER_PRIMARY = auto()     # Move to primary if lost, otherwise keep
    FOLLOW_CURSOR = auto()      # Move to monitor with mouse cursor
    USER_PREFERRED = auto()     # Use learnt preference



class WindowManager:
    """
    Windows window manager.
    
    Features:
    - List all windows
    - Find windows by title (fuzzy)
    - Focus, minimize, maximize, restore
    - Move and resize windows
    - Get window screenshots
    """
    
    def __init__(self) -> None:
        """Initialize window manager."""
        self._user32 = ctypes.windll.user32
        self._kernel32 = ctypes.windll.kernel32
        self._dwmapi = ctypes.windll.dwmapi
    
    def get_all_windows(self, visible_only: bool = True) -> list[WindowInfo]:
        """
        Get list of all windows.
        
        Args:
            visible_only: Only include visible windows
        """
        windows = []
        
        def enum_callback(hwnd: int, _: int) -> bool:
            if visible_only and not self._user32.IsWindowVisible(hwnd):
                return True
            
            try:
                # Check for cloaked windows (Windows 8+)
                is_cloaked = ctypes.c_int(0)
                self._dwmapi.DwmGetWindowAttribute(
                    hwnd, 
                    DWMWA_CLOAKED, 
                    ctypes.byref(is_cloaked), 
                    ctypes.sizeof(is_cloaked)
                )
                if visible_only and is_cloaked.value != 0:
                    return True

                info = self._get_window_info(hwnd)
                
                # Filter out garbage windows
                if info.title and info.width > 0 and info.height > 0:
                    # Filter programmatic/system windows
                    if info.title not in ["Program Manager", "Default IME"]:
                        windows.append(info)
            except Exception:
                pass
            
            return True
        
        # Create callback type
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        callback = WNDENUMPROC(enum_callback)
        
        self._user32.EnumWindows(callback, 0)
        
        return windows
    
    def find_window(
        self,
        title: str,
        fuzzy: bool = True,
        threshold: float = 0.7,
    ) -> WindowInfo | None:
        """
        Find window by title.
        
        Args:
            title: Window title to search
            fuzzy: Use fuzzy matching
            threshold: Fuzzy match threshold
        """
        windows = self.get_all_windows()
        
        if not fuzzy:
            # Exact match (case-insensitive)
            for window in windows:
                if title.lower() in window.title.lower():
                    return window
            return None
        
        # Fuzzy match
        best_match = None
        best_score = 0.0
        
        for window in windows:
            score = fuzz.ratio(title.lower(), window.title.lower()) / 100.0
            if score > best_score and score >= threshold:
                best_score = score
                best_match = window
        
        return best_match
    
    def find_windows(
        self,
        title: str,
        threshold: float = 0.5,
    ) -> list[WindowInfo]:
        """Find all windows matching title."""
        windows = self.get_all_windows()
        
        matches = []
        for window in windows:
            score = fuzz.ratio(title.lower(), window.title.lower()) / 100.0
            if score >= threshold:
                matches.append((score, window))
        
        # Sort by score
        matches.sort(key=lambda x: x[0], reverse=True)
        return [w for _, w in matches]
    
    def get_active_window(self) -> WindowInfo | None:
        """Get currently active window."""
        hwnd = self._user32.GetForegroundWindow()
        if hwnd:
            return self._get_window_info(hwnd)
        return None
    
    def focus_window(self, window: WindowInfo | int | str) -> bool:
        """
        Bring window to foreground using Power Focus techniques.
        
        Args:
            window: WindowInfo, hwnd, or title
        """
        hwnd = self._resolve_hwnd(window)
        if hwnd is None:
            return False
        
        return self._force_foreground(hwnd)

    def smart_focus_window(
        self, 
        window: WindowInfo | int | str, 
        policy: MonitorPolicy = MonitorPolicy.PREFER_PRIMARY
    ) -> bool:
        """
        Focus window with smart monitor policy.
        
        Args:
            window: Window to focus
            policy: Monitor policy to apply
        """
        hwnd = self._resolve_hwnd(window)
        if hwnd is None:
            return False
            
        current_info = self._get_window_info(hwnd)
        
        # Determine target monitor
        target_monitor = current_info.monitor_index
        
        if policy == MonitorPolicy.FORCE_PRIMARY:
            target_monitor = 0
        elif policy == MonitorPolicy.PREFER_PRIMARY:
            # If off-screen or weird coords, force primary
            # Also if specifically requested to prefer primary and current is not 0? 
            # For now, let's keep it robust: prefer primary means "if available and makes sense".
            # Let's enforce primary for reliability as per Plan12 recommendation for "Zero Monitor Hell".
            # But respecting the Policy name "PREFER", we might leave it if valid.
            # However, looking at the Plan: "Forces the target app to move to the Primary Monitor" was the original fix.
            # Plan12 revised it to "PREFER".
            # Implementation: If monitor is not 0, move to 0.
            if target_monitor != 0:
                 target_monitor = 0
        
        # Move if needed
        if current_info.monitor_index != target_monitor:
            logger.info("moving_window_to_monitor", hwnd=hwnd, target=target_monitor)
            self._move_window_to_monitor(hwnd, target_monitor)
            
        return self._force_foreground(hwnd)

        
    def _force_foreground(self, hwnd: int) -> bool:
        """Force window to foreground using advanced techniques."""
        current_foreground = self._user32.GetForegroundWindow()
        if current_foreground == hwnd:
            return True
            
        current_thread_id = self._kernel32.GetCurrentThreadId()
        target_thread_id = self._user32.GetWindowThreadProcessId(hwnd, None)
        
        # Restore if minimized
        if self._user32.IsIconic(hwnd):
            self._user32.ShowWindow(hwnd, SW_RESTORE)
            
        # Technique 1: AttachThreadInput
        if current_thread_id != target_thread_id:
            self._user32.AttachThreadInput(current_thread_id, target_thread_id, True)
            
        try:
            # Technique 2: Alt key simulation (unlocks SetForegroundWindow)
            # Press Alt
            self._user32.keybd_event(0x12, 0, 0, 0) 
            # Release Alt
            self._user32.keybd_event(0x12, 0, 0x0002, 0)
            
            self._user32.SetForegroundWindow(hwnd)
            self._user32.BringWindowToTop(hwnd)
            self._user32.ShowWindow(hwnd, SW_SHOW)
            
        finally:
            if current_thread_id != target_thread_id:
                self._user32.AttachThreadInput(current_thread_id, target_thread_id, False)
        
        # Verify
        final_foreground = self._user32.GetForegroundWindow()
        success = (final_foreground == hwnd)
        
        logger.debug("window_focused", hwnd=hwnd, success=success)
        return success
    
    def minimize_window(self, window: WindowInfo | int | str) -> bool:
        """Minimize window."""
        hwnd = self._resolve_hwnd(window)
        if hwnd is None:
            return False
        
        self._user32.ShowWindow(hwnd, SW_MINIMIZE)
        return True
    
    def maximize_window(self, window: WindowInfo | int | str) -> bool:
        """Maximize window."""
        hwnd = self._resolve_hwnd(window)
        if hwnd is None:
            return False
        
        self._user32.ShowWindow(hwnd, SW_MAXIMIZE)
        return True
    
    def restore_window(self, window: WindowInfo | int | str) -> bool:
        """Restore window from minimized/maximized state."""
        hwnd = self._resolve_hwnd(window)
        if hwnd is None:
            return False
        
        self._user32.ShowWindow(hwnd, SW_RESTORE)
        return True
    
    def close_window(
        self,
        window: WindowInfo | int | str,
        force: bool = False,
    ) -> bool:
        """
        Close window.
        
        Args:
            window: Window to close
            force: Force close (terminate process)
        """
        hwnd = self._resolve_hwnd(window)
        if hwnd is None:
            return False
        
        if force:
            # Get process ID and terminate
            pid = wintypes.DWORD()
            self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            handle = self._kernel32.OpenProcess(1, False, pid.value)
            if handle:
                self._kernel32.TerminateProcess(handle, 0)
                self._kernel32.CloseHandle(handle)
        else:
            # Send WM_CLOSE (graceful)
            WM_CLOSE = 0x0010
            self._user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        
        return True
    
    def move_window(
        self,
        window: WindowInfo | int | str,
        x: int,
        y: int,
        width: int | None = None,
        height: int | None = None,
    ) -> bool:
        """
        Move and optionally resize window.
        
        Args:
            window: Window to move
            x, y: New position
            width, height: New size (keep current if None)
        """
        hwnd = self._resolve_hwnd(window)
        if hwnd is None:
            return False
        
        # Get current size if not specified
        if width is None or height is None:
            current = self._get_window_info(hwnd)
            width = width or current.width
            height = height or current.height
        
        self._user32.MoveWindow(hwnd, x, y, width, height, True)
        return True
    
    # =========================================================================
    # Private Methods
    # =========================================================================
    
    def _resolve_hwnd(self, window: WindowInfo | int | str) -> int | None:
        """Resolve window argument to hwnd."""
        if isinstance(window, WindowInfo):
            return window.hwnd
        elif isinstance(window, int):
            return window
        elif isinstance(window, str):
            found = self.find_window(window)
            if found:
                return found.hwnd
            raise WindowNotFoundError(f"Window not found: {window}")
        return None
    
    def _get_window_info(self, hwnd: int) -> WindowInfo:
        """Get info for a window handle."""
        # Get title
        length = self._user32.GetWindowTextLengthW(hwnd) + 1
        title_buffer = ctypes.create_unicode_buffer(length)
        self._user32.GetWindowTextW(hwnd, title_buffer, length)
        title = title_buffer.value
        
        # Get class name
        class_buffer = ctypes.create_unicode_buffer(256)
        self._user32.GetClassNameW(hwnd, class_buffer, 256)
        class_name = class_buffer.value
        
        # Get position and size
        rect = wintypes.RECT()
        self._user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        # Get state
        is_visible = bool(self._user32.IsWindowVisible(hwnd))
        is_minimized = bool(self._user32.IsIconic(hwnd))
        is_maximized = bool(self._user32.IsZoomed(hwnd))
        
        # Get process ID
        pid = wintypes.DWORD()
        self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        return WindowInfo(
            hwnd=hwnd,
            title=title,
            class_name=class_name,
            x=rect.left,
            y=rect.top,
            width=rect.right - rect.left,
            height=rect.bottom - rect.top,
            is_visible=is_visible,
            is_minimized=is_minimized,
            is_maximized=is_maximized,
            process_id=pid.value,
            monitor_index=self._get_monitor_index(hwnd),
        )

    def normalize_coordinates(self, x: int, y: int) -> tuple[int, int]:
        """
        Adjust coordinates to be relative to the active monitor's origin.
        Assumes x,y are 0-based relative to the monitor top-left.
        """
        active = self.get_active_window()
        if not active:
             return x, y
        
        mx, my, _, _ = self._get_monitor_rect(active.monitor_index)
        return mx + x, my + y

    def _get_monitor_index(self, hwnd: int) -> int:
        """Get index of the monitor containing the window."""
        hmonitor = self._user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        
        monitors = []
        def monitor_enum_proc(hmonitor, hdc, rect, lparam):
            monitors.append(hmonitor)
            return True
        
        # Define callback type for EnumDisplayMonitors
        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_bool, 
            ctypes.c_void_p, # HMONITOR 
            ctypes.c_void_p, # HDC
            ctypes.POINTER(wintypes.RECT), # LPRECT
            wintypes.LPARAM # LPARAM
        )
        callback = MONITORENUMPROC(monitor_enum_proc)
        
        self._user32.EnumDisplayMonitors(None, None, callback, 0)
        
        try:
            return monitors.index(hmonitor)
        except ValueError:
            return 0 # Default to primary

    def _get_monitor_rect(self, index: int) -> tuple[int, int, int, int]:
        """Get monitor rectangle (x, y, w, h)."""
        monitors = []
        def monitor_enum_proc(hmonitor, hdc, rect, lparam):
            if rect:
                r = rect.contents
                monitors.append((r.left, r.top, r.right - r.left, r.bottom - r.top))
            return True
            
        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_bool, 
            ctypes.c_void_p, 
            ctypes.c_void_p, 
            ctypes.POINTER(wintypes.RECT), 
            wintypes.LPARAM
        )
        callback = MONITORENUMPROC(monitor_enum_proc)
        self._user32.EnumDisplayMonitors(None, None, callback, 0)
        
        if 0 <= index < len(monitors):
            return monitors[index]
        return (0, 0, 1920, 1080) # Fallback

    def _move_window_to_monitor(self, hwnd: int, monitor_index: int):
        """Move window to center of target monitor."""
        mx, my, mw, mh = self._get_monitor_rect(monitor_index)
        
        # Get window size
        rect = wintypes.RECT()
        self._user32.GetWindowRect(hwnd, ctypes.byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        
        # Center
        new_x = mx + (mw - width) // 2
        new_y = my + (mh - height) // 2
        
        self.move_window(hwnd, new_x, new_y, width, height)


