import sys
import os
import json
import time
import subprocess
import psutil

# Setup path to import app logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.core.process_sentinel import sentinel
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import app.core.process_sentinel: {e}")
    sys.exit(1)

def check_paths():
    print("\n=== 1. CHECKING CRITICAL PATHS (app_paths.json) ===")
    
    # Locate paths file
    paths_file = os.path.join("Modules", "Core", "Knowledge", "app_paths.json")
    if not os.path.exists(paths_file):
        print(f"FAIL: Configuration file not found at {paths_file}")
        return

    try:
        with open(paths_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAIL: Could not read JSON: {e}")
        return
    
    apps = data.get("apps", {})
    fail_count = 0
    pass_count = 0
    
    for app_name, info in apps.items():
        path = info.get("path")
        if not path:
            print(f"WARN: {app_name} has no path defined")
            continue
            
        if os.path.exists(path):
            print(f"PASS: {app_name:<15} -> FOUND")
            pass_count += 1
        else:
            print(f"FAIL: {app_name:<15} -> NOT FOUND ({path})")
            fail_count += 1
            
    print(f"\n[PATH SUMMARY] PASS: {pass_count} | FAIL: {fail_count}")

def check_sentinel():
    print("\n=== 2. CHECKING SENTINEL PID TRACKING ===")
    
    # 1. Start a dummy process (notepad) to test tracking
    try:
        proc = subprocess.Popen("notepad.exe")
        pid = proc.pid
        print(f"INFO: Started Notepad for testing. PID: {pid}")
        
        # Give it a moment to start
        time.sleep(1)
        
        # 2. Register with Sentinel
        print("INFO: Registering PID with Sentinel...")
        sentinel.track_pid(pid)
        
        # 3. Verify internal state
        if pid in sentinel._tracked_pids:
            print("PASS: Sentinel successfully tracked the PID.")
        else:
            print("FAIL: Sentinel failed to track the PID (Internal State).")

        # 4. Dry Run Scan (Ensure it doesn't kill it immediately)
        print("INFO: Running scan_and_purge(force_all_targets=False)...")
        purged = sentinel.scan_and_purge(force_all_targets=False)
        
        if psutil.pid_exists(pid):
            print("PASS: Process survived normal scan.")
        else:
            print("FAIL: Process was killed by scan unexpectedly!")

    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
    finally:
        # Cleanup
        if 'proc' in locals():
            try:
                proc.terminate()
                proc.wait(timeout=2)
                print("INFO: Test process cleaned up.")
            except:
                pass

if __name__ == "__main__":
    print("ONI-CHECK DIAGNOSTIC TOOL v1.0")
    print(f"CWD: {os.getcwd()}")
    check_paths()
    check_sentinel()
