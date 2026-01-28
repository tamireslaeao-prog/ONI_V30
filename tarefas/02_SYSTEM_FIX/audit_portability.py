import os
import sys
import re

def check_portability():
    print("🔍 ONI PORTABILITY AUDIT (CATEGORIZED)")
    print("="*60)
    
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Categories
    categories = {
        "CRITICAL": [], # Imports, System Core, Base Paths
        "WARNING": [],  # Scripts relying on Desktop, old Versions
        "INFO": []      # Comments, logs, minor references
    }
    
    suspicious_patterns = [
        r"C:\\Users", r"C:/Users", r"Desktop",
        r"ONI_V\d+", r"ONI\s*V\d+", r"ONIV\d+", r"V\d{2}\.\d", r"Legacy"
    ]
    
    count = 0
    
    for root, dirs, files in os.walk(root_dir):
        if any(x in root for x in ["venv", ".git", "__pycache__", "archive", "node_modules"]):
            continue
            
        for file in files:
            if file.endswith((".py", ".jsx", ".bat", ".json", ".js")):
                file_path = os.path.join(root, file)
                if "audit_portability.py" in file: continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    for i, line in enumerate(lines):
                        for pattern in suspicious_patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                match_text = match.group(0)
                                # Whitelist
                                if any(x in match_text.upper() for x in ["ONI_V30", "ONIV30"]): continue
                                if "os.path" in line and "Desktop" in match_text: continue
                                
                                rel_path = os.path.relpath(file_path, root_dir)
                                issue = f"{rel_path}:{i+1} -> {match_text}"
                                
                                # Classification Logic
                                if file.endswith(".py") and ("import" in line or "sys.path" in line or "ROOT" in line):
                                    categories["CRITICAL"].append(issue)
                                elif "Desktop" in match_text or "C:" in match_text:
                                    categories["WARNING"].append(issue)
                                else:
                                    categories["INFO"].append(issue)
                                count += 1
                                break # One report per line is enough
                except: pass

    # Report
    for cat, items in categories.items():
        print(f"\n[{cat}] - {len(items)} Items")
        print("-" * 40)
        # Limit output for readability
        for item in items[:20]: 
            print(f"  - {item}")
        if len(items) > 20: print(f"  ... and {len(items)-20} more.")

    print("="*60)
    print(f"TOTAL ISSUES: {count}")

if __name__ == "__main__":
    check_portability()
