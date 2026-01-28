import win32clipboard
import win32com.client
import os
import time
import tempfile

# ONI Corel-AI Bridge
# Replicates functionality of LanyaVBA's pdf2clip/clip2pdf
# Allows high-fidelity transfer between CorelDRAW and Illustrator via PDF

def get_corel():
    try:
        return win32com.client.Dispatch("CorelDRAW.Application")
    except:
        print("❌ CorelDRAW not found.")
        return None

def set_clipboard_pdf(pdf_path):
    """Reads a PDF file and puts it on the system clipboard as 'Portable Document Format'"""
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False

    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()

    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        
        # Register Format ID if needed, or use standard
        # Standard CF_PDF often doesn't exist, we register "Portable Document Format" which Adobe uses
        cf_pdf = win32clipboard.RegisterClipboardFormat("Portable Document Format")
        
        win32clipboard.SetClipboardData(cf_pdf, pdf_data)
        win32clipboard.CloseClipboard()
        print(f"✅ PDF data ({len(pdf_data)} bytes) copied to clipboard.")
        return True
    except Exception as e:
        print(f"❌ Clipboard Error: {e}")
        return False

def get_clipboard_pdf(output_path):
    """Saves clipboard PDF data to a file"""
    try:
        win32clipboard.OpenClipboard()
        cf_pdf = win32clipboard.RegisterClipboardFormat("Portable Document Format")
        
        if win32clipboard.IsClipboardFormatAvailable(cf_pdf):
            data = win32clipboard.GetClipboardData(cf_pdf)
            with open(output_path, 'wb') as f:
                f.write(data)
            print(f"✅ Clipboard content saved to {output_path}")
            win32clipboard.CloseClipboard()
            return True
        else:
            print("⚠️ No PDF data found on clipboard.")
            win32clipboard.CloseClipboard()
            return False
    except Exception as e:
        print(f"❌ Clipboard Read Error: {e}")
        return False

def copy_selection_to_ai(corel):
    """Exports Corel selection to PDF and places on Clipboard"""
    if corel.ActiveSelection.Shapes.Count == 0:
        print("⚠️ No objects selected in Corel.")
        return

    doc = corel.ActiveDocument
    temp_pdf = os.path.join(tempfile.gettempdir(), "ONI_Bridge_Export.pdf")
    
    print("⚙️ Configuring PDF Export...")
    # Replication of Lanya settings
    s = doc.PDFSettings
    s.PublishRange = 1 # pdfSelection
    s.ColorMode = 3 # pdfNative
    s.EmbedFonts = True
    s.TureTypeToType1 = True
    
    print(f"📤 Exporting to {temp_pdf}...")
    doc.PublishToPDF(temp_pdf)
    
    # Wait specifically for file write
    time.sleep(0.5)
    
    set_clipboard_pdf(temp_pdf)
    print("🚀 Ready to Paste in Illustrator!")

def paste_from_ai_to_corel(corel):
    """Reads PDF from Clipboard and Imports to Corel"""
    temp_pdf = os.path.join(tempfile.gettempdir(), "ONI_Bridge_Import.pdf")
    
    if get_clipboard_pdf(temp_pdf):
        print(f"📥 Importing into Corel...")
        try:
            layer = corel.ActiveLayer
            # structImportOptions not always needed via COM, ImportEx is robust
            layer.Import(temp_pdf) 
            print("✅ Import Successful.")
        except Exception as e:
            print(f"❌ Corel Import Error: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ONI Corel-AI Bridge")
    parser.add_argument("--copy", action="store_true", help="Copy Corel Selection to AI")
    parser.add_argument("--paste", action="store_true", help="Paste AI Clipboard to Corel")
    
    args = parser.parse_args()
    
    corel = get_corel()
    if corel:
        if args.copy:
            copy_selection_to_ai(corel)
        elif args.paste:
            paste_from_ai_to_corel(corel)
        else:
            print("ℹ️ Use --copy or --paste")
