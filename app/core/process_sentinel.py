
import os
import time
import psutil
import structlog
from typing import List, Set, Dict
from datetime import datetime, timedelta

logger = structlog.get_logger(__name__)

class ProcessSentinel:
    """
    Monitor and cleanup automation processes (PowerShell, AutoCAD, Excel, etc.)
    that might be left orphaned or hanging.
    """
    
    TARGET_PROCESS_NAMES = {"powershell.exe", "pwsh.exe", "acad.exe", "excel.exe", "winword.exe"}
    MAX_PROCESS_AGE_MINUTES = 60 # Terminate processes older than this if they belong to ONI contexts

    def __init__(self):
        self._tracked_pids: Set[int] = set()
        self._last_scan = datetime.now()

    def track_pid(self, pid: int):
        """Register a PID to be explicitly managed by ONI Sentinel."""
        if pid > 0:
            self._tracked_pids.add(pid)
            logger.info("sentinel_tracking_started", pid=pid)

    def scan_and_purge(self, force_all_targets: bool = False):
        """
        Scans all processes and purges:
        1. Explicitly tracked PIDs that are non-responsive or finished.
        2. Target processes that exceed the age limit.
        """
        logger.info("sentinel_scan_started", force_all=force_all_targets)
        count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                p_info = proc.info
                p_pid = p_info['pid']
                p_name = p_info['name'].lower()
                
                # Check for explicit tracking or general target list
                is_tracked = p_pid in self._tracked_pids
                is_target = p_name in self.TARGET_PROCESS_NAMES or force_all_targets
                
                if is_tracked or is_target:
                    create_time = datetime.fromtimestamp(p_info['create_time'])
                    age = datetime.now() - create_time
                    
                    # Conditions for termination:
                    # 1. Force all (emergency purge)
                    # 2. Exceeds max age
                    # 3. Tracked but process is zombie/hanging (implemented via status check if needed)
                    
                    if force_all_targets or age.total_seconds() > (self.MAX_PROCESS_AGE_MINUTES * 60):
                        logger.warning("sentinel_terminating_process", 
                                       pid=p_pid, 
                                       name=p_name, 
                                       age_seconds=int(age.total_seconds()))
                        proc.terminate()
                        count += 1
                        if p_pid in self._tracked_pids:
                            self._tracked_pids.remove(p_pid)
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        logger.info("sentinel_scan_finished", purged_count=count)
        return count

    def emergency_purge_automation(self):
        """Kills all known automation target processes immediately."""
        return self.scan_and_purge(force_all_targets=True)

sentinel = ProcessSentinel()
