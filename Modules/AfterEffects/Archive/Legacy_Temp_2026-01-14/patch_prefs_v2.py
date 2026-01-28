import os

def patch_ae_prefs_v2():
    prefs_path = r"C:\Users\user\AppData\Roaming\Adobe\After Effects\25.6\Preferências do Adobe After Effects 25.6.txt"
    
    if not os.path.exists(prefs_path):
        print("Prefs not found")
        return

    with open(prefs_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    new_lines = []
    in_scripting = False
    scripting_section_found = False
    
    key_allow_scripts = '"Allow Scripts to Write Files and Access Network"'
    key_found = False

    for line in lines:
        if '["Scripting"]' in line:
            in_scripting = True
            scripting_section_found = True
            new_lines.append(line)
            continue
        
        if in_scripting and line.strip().startswith('['):
            # End of section, insert if missing
            if not key_found:
                new_lines.append('\t"Allow Scripts to Write Files and Access Network" = "1"\n')
                print("Inserted 'Allow Scripts' key.")
                key_found = True # Prevent double insert
            in_scripting = False
            new_lines.append(line)
            continue

        if in_scripting and key_allow_scripts in line:
            # Update existing
            new_lines.append('\t"Allow Scripts to Write Files and Access Network" = "1"\n')
            print("Updated existing key.")
            key_found = True
        else:
            new_lines.append(line)

    if not scripting_section_found:
        print("Scripting section NOT found. Appending it.")
        new_lines.append('\n["Scripting"]\n')
        new_lines.append('\t"Allow Scripts to Write Files and Access Network" = "1"\n')

    # Write back
    with open(prefs_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Patch complete.")

if __name__ == "__main__":
    patch_ae_prefs_v2()
