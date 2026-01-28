import os

def patch_ae_prefs_v3():
    # Target 25.0 this time
    prefs_path = r"C:\Users\user\AppData\Roaming\Adobe\After Effects\25.0\Preferências do Adobe After Effects 25.0.txt"
    
    # Also try the "25.6" again just in case (redundancy)
    paths = [
        r"C:\Users\user\AppData\Roaming\Adobe\After Effects\25.0\Preferências do Adobe After Effects 25.0.txt",
        r"C:\Users\user\AppData\Roaming\Adobe\After Effects\25.6\Preferências do Adobe After Effects 25.6.txt"
    ]

    for p in paths:
        if not os.path.exists(p):
            print(f"Skipping {p} (Not found)")
            continue
            
        print(f"Patching {p}")
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            new_lines = []
            scripting_found = False
            for line in lines:
                if '["Scripting"]' in line:
                    scripting_found = True
                    new_lines.append(line)
                    # Force insert next
                    new_lines.append('\t"Allow Scripts to Write Files and Access Network" = "1"\n')
                    new_lines.append('\t"Show Welcome Screen" = "0"\n')
                    continue
                # Remove duplicates if we overwrite
                if "Allow Scripts to Write" in line or "Show Welcome Screen" in line:
                    continue
                new_lines.append(line)

            if not scripting_found:
                 new_lines.append('\n["Scripting"]\n')
                 new_lines.append('\t"Allow Scripts to Write Files and Access Network" = "1"\n')
                 new_lines.append('\t"Show Welcome Screen" = "0"\n')

            with open(p, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("Success.")
        except Exception as e:
            print(f"Error patching {p}: {e}")

if __name__ == "__main__":
    patch_ae_prefs_v3()
