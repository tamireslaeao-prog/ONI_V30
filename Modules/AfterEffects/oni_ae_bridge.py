"""
ONI AE Bridge v1.0
Python API for After Effects automation via file-based job queue.
"""

import os
import json
import time
import uuid
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path

# Configuration - Portable paths based on this file's location
# This file is at: ONIV24/Modules/AfterEffects/oni_ae_bridge.py
_ONI_ROOT = Path(__file__).parent.parent.parent.resolve()
JOB_FOLDER = str(_ONI_ROOT / "temp" / "ae_jobs")
AE_PATH = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
DEFAULT_TIMEOUT = 30  # seconds


def ensure_job_folder():
    """Ensure the job folder exists."""
    if not os.path.exists(JOB_FOLDER):
        os.makedirs(JOB_FOLDER)


def launch_ae() -> bool:
    """Launch After Effects if not running."""
    import psutil
    
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'AfterFX' in proc.info['name']:
            return True  # Already running
    
    if os.path.exists(AE_PATH):
        subprocess.Popen([AE_PATH])
        time.sleep(10)  # Wait for AE to start
        return True
    return False


def submit_job(job: Dict[str, Any]) -> str:
    """
    Submit a job to After Effects.
    
    Args:
        job: Dictionary with job parameters. Must include 'type'.
              Optional: 'id' (auto-generated if missing).
    
    Returns:
        job_id: The ID of the submitted job.
    """
    ensure_job_folder()
    
    if 'id' not in job:
        job['id'] = str(uuid.uuid4())[:8]
    
    job_file = os.path.join(JOB_FOLDER, f"job_{job['id']}.json")
    
    with open(job_file, 'w', encoding='utf-8') as f:
        json.dump(job, f, indent=2)
    
    return job['id']


def wait_for_result(job_id: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[Dict]:
    """
    Wait for a job result from After Effects.
    
    Args:
        job_id: The ID of the job to wait for.
        timeout: Maximum seconds to wait.
    
    Returns:
        Result dictionary or None if timeout.
    """
    result_file = os.path.join(JOB_FOLDER, f"result_{job_id}.json")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            os.remove(result_file)  # Clean up
            return result
        time.sleep(0.5)
    
    return None


def execute_job(job: Dict[str, Any], timeout: int = DEFAULT_TIMEOUT) -> Optional[Dict]:
    """
    Submit a job and wait for the result.
    
    Args:
        job: Job dictionary.
        timeout: Maximum seconds to wait.
    
    Returns:
        Result dictionary or None if failed/timeout.
    """
    job_id = submit_job(job)
    return wait_for_result(job_id, timeout)


# ============================================================
# HIGH-LEVEL API
# ============================================================

def ping() -> bool:
    """Test if AE Bridge is working."""
    result = execute_job({"type": "ping"}, timeout=10)
    return result is not None and result.get("status") == "pong"


def create_project(save_path: Optional[str] = None) -> bool:
    """Create a new AE project."""
    job = {"type": "create_project"}
    if save_path:
        job["save_path"] = save_path.replace("\\", "/")
    result = execute_job(job)
    return result is not None and result.get("status") == "success"


def create_comp(name: str, width: int = 1920, height: int = 1080, 
                duration: float = 10, fps: int = 30) -> Optional[int]:
    """Create a composition. Returns comp_id or None."""
    result = execute_job({
        "type": "create_comp",
        "name": name,
        "width": width,
        "height": height,
        "duration": duration,
        "fps": fps
    })
    if result and result.get("status") == "success":
        return result.get("comp_id")
    return None


def import_file(file_path: str) -> Optional[int]:
    """Import a file into the project. Returns item_id or None."""
    result = execute_job({
        "type": "import_file",
        "file_path": file_path.replace("\\", "/")
    })
    if result and result.get("status") == "success":
        return result.get("item_id")
    return None


def save_project(path: Optional[str] = None) -> bool:
    """Save the current project."""
    job = {"type": "save_project"}
    if path:
        job["path"] = path.replace("\\", "/")
    result = execute_job(job)
    return result is not None and result.get("status") == "success"


def run_script(code: str) -> Optional[str]:
    """Execute arbitrary JSX code. Returns result or None."""
    result = execute_job({"type": "run_script", "code": code})
    if result and result.get("status") == "success":
        return result.get("message")
    return None


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    print("=== ONI AE BRIDGE TEST ===")
    
    # Check if AE is running
    print("[1] Launching AE if needed...")
    if launch_ae():
        print("    AE is running.")
    else:
        print("    WARN: Could not launch AE.")
    
    # Ping test
    print("[2] Pinging AE Bridge...")
    if ping():
        print("    SUCCESS: AE responded!")
    else:
        print("    FAIL: No response. Is the watcher installed?")
        print(f"    Check: {JOB_FOLDER}")
