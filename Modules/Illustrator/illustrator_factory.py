import os
import subprocess
import time
import argparse

class IllustratorFactory:
    def __init__(self):
        # Auto-detect Illustrator Path (Hardcoded based on user recon)
        self.ai_path = r"C:\Program Files\Adobe\Adobe Illustrator 2023\Support Files\Contents\Windows\Illustrator.exe"
        if not os.path.exists(self.ai_path):
            print(f"[ERROR] Illustrator not found at: {self.ai_path}")
    
    def generate_trace_script(self, input_image, output_svg):
        """Generates the JSX script to control Illustrator."""
        
        # Escape paths for ExtendScript
        input_safe = input_image.replace("\\", "\\\\")
        output_safe = output_svg.replace("\\", "\\\\")
        # Use forward slashes for JS to avoid escaping hell
        log_path = os.path.join(os.path.dirname(input_image), "trace_error.txt").replace("\\", "/")
        
        jsx_content = f'''
        #target illustrator
        
        function traceImage() {{
            // 1. Setup
            app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
            
            // 2. Open Image
            var fileRef = new File("{input_safe}");
            if (!fileRef.exists) {{
                alert("Input file not found: " + fileRef.fsName);
                return;
            }}
            
            var doc = open(fileRef);
            
            // 3. Image Selection & Embedding Logic
            var traceItem = null;
            
            // Force embed if placed items exist
            if (doc.placedItems.length > 0) {{
                doc.placedItems[0].embed();
            }}
            
            // Now grabs the raster item (either original or result of embed)
            if (doc.rasterItems.length > 0) {{
                traceItem = doc.rasterItems[0];
            }}
            
            if (!traceItem) {{
                throw new Error("No traceable RasterItem found! Placed: " + doc.placedItems.length + ", Raster: " + doc.rasterItems.length);
            }}
            
            // Select the item to be sure
            doc.selection = null;
            traceItem.selected = true;
            
            // 4. Trace
            var plugin = traceItem.trace();
            var tracing = plugin.tracing;
            var options = tracing.tracingOptions;
            
            // 4. Configure Trace (High Fidelity)
            options.tracingMode = TracingModeType.TRACINGMODECOLOR;
            options.viewMode = ViewType.TRACINGVIEWVECTORTRACINGRESULT;
            options.colorPrecision = 100; // Max precision
            options.cornerFidelity = 100;
            options.pathFidelity = 100;
            options.noiseFidelity = 1; // Min noise
            options.ignoreWhite = true;
            
            // Execute
            app.redraw();
            
            // 5. Expand (Convert to Paths)
            // Try on tracing object first (Modern AI)
            tracing.expandTracing().selected = true;
            
            // 6. Resize Artboard to Fit Content MATCHING ORIGINAL DIMENSIONS
            doc.artboards[0].artboardRect = doc.visibleBounds;

            // 7. Save as SVG
            var exportOptions = new ExportOptionsSVG();
            exportOptions.embedRasterImages = false;
            exportOptions.cssProperties = SVGCSSPropertyLocation.STYLEATTRIBUTES;
            exportOptions.fontSubsetting = SVGFontSubsetting.None;
            exportOptions.documentEncoding = SVGDocumentEncoding.UTF8;
            
            var outFile = new File("{output_safe}");
            doc.exportFile(outFile, ExportType.SVG, exportOptions);
            
            // 7. Close
            doc.close(SaveOptions.DONOTSAVECHANGES);
        }}
        
        
        try {{
            traceImage();
        }} catch(e) {{
            var logFile = new File("{log_path}");
            logFile.open("w");
            logFile.writeln("Error: " + e);
            logFile.close();
            // alert("Error: " + e); // Fallback alert
        }}
        '''
        return jsx_content

    def trace_image(self, input_path):
        """Main entry point to run the trace."""
        input_abs = os.path.abspath(input_path)
        output_abs = input_abs + ".svg"
        
        print(f"\n[ILLUSTRATOR NATIVE TRACE]")
        print(f"Input: {input_abs}")
        print(f"Engine: High Fidelity Photo Trace")
        
        # 1. Create Script
        jsx_path = os.path.join(os.path.dirname(input_abs), "trace_job.jsx")
        script = self.generate_trace_script(input_abs, output_abs)
        
        with open(jsx_path, "w", encoding="utf-8") as f:
            f.write(script)
            
        # 2. Execute Illustrator (Non-blocking)
        # Note: Illustrator -r expects the script path
        cmd = [self.ai_path, "-r", jsx_path]
        
        # Cleanup stale error log
        error_log = os.path.join(os.path.dirname(input_abs), "trace_error.txt")
        if os.path.exists(error_log):
            os.remove(error_log)
        
        try:
            print("Launching Illustrator...")
            # Use Popen to start without waiting for exit
            subprocess.Popen(cmd)
            
            # Wait loop for file creation
            max_wait = 120 # Increased wait for Ultra quality
            print(f"Waiting for SVG output (max {max_wait}s)...")
            
            for i in range(max_wait):
                if os.path.exists(output_abs):
                    # Give it a moment to finish writing
                    time.sleep(1) 
                    print(f"\n[SUCCESS] Vector generated: {output_abs}")
                    return output_abs
                
                # Check for error log
                error_log = os.path.join(os.path.dirname(input_abs), "trace_error.txt")
                if os.path.exists(error_log):
                    with open(error_log, 'r') as f:
                        err_msg = f.read()
                    print(f"\n[ERROR] Illustrator Script Failed:\n{err_msg}")
                    return None
                    
                time.sleep(1)
                if i % 5 == 0: print(".", end="", flush=True)
                
            print("\n[TIMEOUT] Illustrator did not produce output in time.")
            return None
            
        except Exception as e:
            print(f"[ERROR] Failed to run Illustrator: {e}")
            return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to input image")
    args = parser.parse_args()
    
    factory = IllustratorFactory()
    factory.trace_image(args.image)
