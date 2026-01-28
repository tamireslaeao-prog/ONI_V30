import os

def patch_ae_prefs():
    prefs_path = r"C:\Users\user\AppData\Roaming\Adobe\After Effects\25.6\Preferências do Adobe After Effects 25.6.txt"
    
    if not os.path.exists(prefs_path):
        print(f"Error: Prefs file not found at {prefs_path}")
        return

    with open(prefs_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Define settings to enforce
    updates = {
        '"Allow Scripts to Write Files and Access Network"': ' = "1"',
        '"Show Welcome Screen"': ' = "0"',
        '"Show Home Screen"': ' = "0"'
    }
    
    new_content = content
    # Dumb but effective replacement
    # Note: AE prefs structure is Section -> Key = Value
    # Using simple replace for known keys if they exist, or basic append if not (though appending to end might work if sections aren't strict, usually they are).
    # Safer: Look for the key.

    for key, val in updates.items():
        if key in new_content:
            # Regex or simple find/replace for the line?
            # Key usually appears as: "Key" = "Value"
            # Let's find index
            idx = new_content.find(key)
            if idx != -1:
                # Find the next newline
                next_newline = new_content.find('\n', idx)
                line = new_content[idx:next_newline]
                print(f"Found existing: {line}")
                # Replace logic
                # Key = "0" -> Key = "1"
                # Construct new line
                new_line = f'{key}{val}'
                new_content = new_content.replace(line, new_line)
                print(f"Replaced with: {new_line}")
        else:
            print(f"Key not found, skipping append (risky structure): {key}")

    if new_content != content:
        # Backup
        with open(prefs_path + ".bak", 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write
        with open(prefs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Preferences updated.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    patch_ae_prefs()
