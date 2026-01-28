
import win32com.client
import os
from typing import List, Dict, Optional

class PhotoshopComposer:
    def __init__(self):
        self.app = None

    def _ensure_connection(self):
        if self.app:
            try:
                # Check if still alive
                self.app.Version
                return
            except:
                self.app = None

        try:
            self.app = win32com.client.Dispatch("Photoshop.Application")
            self.app.DisplayDialogs = 3 # NO Dialogs
        except Exception as e:
            print(f"❌ Photoshop Connect Error: {e}")
            self.app = None

    def _smart_edit_recursive(self, new_text, depth=0):
        if depth > 3: return # Safety limit
        
        # JSX for Recursive Edit + Safe Clean + Hunter Logic (V24)
        jsx = f"""
        var doc = app.activeDocument;
        var newText = "{new_text}";
        
        // --- 1. CONFIG ---
        var textTrash = ["psd", "edit", "smart object", "creative", "collection", "font", "link", "download", "preview"];
        var bgTrash = ["background", "bg ", "paper", "solid", "color fill", "preview", "layer 0", "white"];

        // --- 2. GLOBAL FINDERS ---
        var bestHeroText = null;
        var maxTextSize = 0;
        
        var bestHeroSO = null;
        var maxSOArea = 0;

        function deepScan(container) {{
             for(var i=0; i<container.layers.length; i++){{
                var l=container.layers[i];
                
                // Unlock
                if(l.allLocked || l.pixelsLocked || l.positionLocked || l.transparentPixelsLocked) l.allLocked = false;
                
                // --- A. CLEANER ---
                var n = l.name.toLowerCase();
                var isTrash = false;
                
                // Background Name Check
                if(l.kind != LayerKind.TEXT) {{
                    for(var k=0; k<bgTrash.length; k++){{ 
                        if(n.indexOf(bgTrash[k])!=-1){{ isTrash=true; break; }} 
                    }}
                }}
                
                // Text Content Check
                if(l.visible && l.kind == LayerKind.TEXT){{
                    var txt=""; try{{txt=l.textItem.contents.toLowerCase();}}catch(e){{}}
                    for(var t=0; t<textTrash.length; t++){{ 
                        if(txt.indexOf(textTrash[t])!=-1){{ isTrash=true; break; }} 
                    }}
                }}

                if(isTrash) {{
                    l.visible = false;
                }}
                
                if(!l.visible) continue; // Skip processing hidden/trash layers for Hero status

                // --- B. HERO HUNTER (Deep Scan) ---
                if(l.kind == LayerKind.TEXT) {{
                    var s=10; try{{s=l.textItem.size.as("px");}}catch(e){{}}
                    if(s > maxTextSize) {{ maxTextSize=s; bestHeroText=l; }}
                }}
                else if(l.kind == LayerKind.SMARTOBJECT) {{
                    var b=l.bounds; var area=(b[2]-b[0])*(b[3]-b[1]);
                    if(area > maxSOArea) {{ maxSOArea=area; bestHeroSO=l; }}
                }}
                else if(l.typename == "LayerSet") {{
                    deepScan(l); // RECURSE INTO GROUP
                }}
             }}
        }}

        // Run the Hunter
        deepScan(doc);

        // --- 3. ACTION ---
        if (bestHeroText) {{
            // Found Text -> Edit it
            bestHeroText.textItem.contents = newText;
            try {{ doc.revealAll(); }} catch(e){{}} // Fix Cropping
            "EDITED";
        }} else if (bestHeroSO) {{
            // No Text Found -> Dive into Best Smart Object
            doc.activeLayer = bestHeroSO;
            "DIVE";
        }} else {{
            "NOTHING";
        }}
        """
        
        res = self.app.DoJavaScript(jsx)
        
        if res == "DIVE":
            # Recurse
            self.app.DoJavaScript("""executeAction(stringIDToTypeID("placedLayerEditContents"), new ActionDescriptor(), DialogModes.NO);""")
            self._smart_edit_recursive(new_text, depth+1)
            # Close Child
            self.app.ActiveDocument.Close(1) # Save
        
        # If EDITED or NOTHING, we are done at this level.

    def compose_assets(
        self, 
        assets: List[Dict[str, any]], 
        output_name: str = "COMPOSITION.psd", 
        width: int = 2400, 
        height: int = 1600,
        dark_mode: bool = True
    ):
        self._ensure_connection()
        if not self.app: return {"status": "error"}

        # 1. Master Doc
        bg_js = ""
        if dark_mode:
            bg_js = """
            var c=new SolidColor(); c.rgb.hexValue='111111'; 
            doc.selection.selectAll(); doc.selection.fill(c); doc.selection.deselect();
            """
        
        create_jsx = f"""
        var docName = "{output_name}";
        try {{ app.documents.getByName(docName).close(2); }} catch(e) {{}}
        var doc = app.documents.add({width}, {height}, 72, docName, NewDocumentMode.RGB, DocumentFill.TRANSPARENT);
        {bg_js}
        """
        self.app.DoJavaScript(create_jsx)

        results = []
        
        # 2. Process Assets
        for asset in assets:
            path = asset.get('path')
            label = asset.get('label', 'Asset')
            text = asset.get('text_content', 'ONI') # Default Text
            y_offset = asset.get('y_offset', 0)
            
            if not os.path.exists(path):
                results.append({"label": label, "status": "missing"})
                continue
                
            path_js = path.replace("\\", "\\\\")
            
            # Place & Position
            place_jsx = f"""
            var f=new File("{path_js}");
            if(f.exists){{
                var d=new ActionDescriptor(); d.putPath(charIDToTypeID("null"), f); d.putEnumerated(charIDToTypeID("FTcs"), charIDToTypeID("QCSt"), charIDToTypeID("Qcsa")); 
                executeAction(charIDToTypeID("Plc "), d, DialogModes.NO);
                var l=app.activeDocument.activeLayer; l.name="{label}";
                
                var b=l.bounds; var w=b[2]-b[0]; 
                if(w>900){{var s=(900/w)*100; l.resize(s,s);}}
                var b2=l.bounds;
                var cx=b2[0].value+(b2[2].value-b2[0].value)/2; 
                var cy=b2[1].value+(b2[3].value-b2[1].value)/2;
                var tx=(app.activeDocument.width.value/2);
                var ty=(app.activeDocument.height.value/2)+{y_offset};
                l.translate(tx-cx, ty-cy);
                "ok"
            }} else {{ "err" }}
            """
            if self.app.DoJavaScript(place_jsx) == "ok":
                # Edit Content (V24 Hunter Logic)
                self.app.DoJavaScript("""executeAction(stringIDToTypeID("placedLayerEditContents"), new ActionDescriptor(), DialogModes.NO);""")
                self._smart_edit_recursive(text)
                self.app.ActiveDocument.Close(1) # Save level 1
                results.append({"label": label, "status": "success"})
            else:
                results.append({"label": label, "status": "failed_place"})

        return {"status": "success", "results": results}

    def vectorize_active_layer(self, tolerance: float = 1.0, auto_subject: bool = True) -> Dict[str, str]:
        """
        Converts the active raster layer into a vector shape layer.
        :param tolerance: Path tolerance (lower = more precise).
        :param auto_subject: If True, uses AI 'Select Subject' before vectorizing.
        """
        self._ensure_connection()
        if not self.app: return {"status": "error", "message": "No Connection"}

        jsx_payload = f"""
        var debugSteps = "";
        try {{
            var doc = app.activeDocument;
            var layer = doc.activeLayer;
            debugSteps += "[1] Start ";

            // 0. ENSURE LAYER IS UNLOCKED (Promote Background to Layer)
            if (layer.isBackgroundLayer || layer.allLocked) {{
                layer.isBackgroundLayer = false; // Promote to Layer 0
                layer.allLocked = false;
                debugSteps += "[0] Unlocked ";
            }}

            // --- 1. SELECTION STRATEGY ---
            if ({str(auto_subject).lower()}) {{
                // A. AI SELECT SUBJECT
                try {{
                    var idautoCutout = stringIDToTypeID( "autoCutout" );
                    var descSubject = new ActionDescriptor();
                    var idsampleAllLayers = stringIDToTypeID( "sampleAllLayers" );
                    descSubject.putBoolean( idsampleAllLayers, false );
                    executeAction( idautoCutout, descSubject, DialogModes.NO );
                    debugSteps += "[2A] SelectSubject ";
                }} catch(e) {{
                    // Fallback to Transparency if AI fails (e.g. old Photoshop)
                    loadTransparency();
                }}
            }} else {{
                // B. TRANSPARENCY
                loadTransparency();
            }}

            function loadTransparency() {{
                try {{
                    var desc = new ActionDescriptor();
                    var ref = new ActionReference();
                    ref.putProperty(stringIDToTypeID("channel"), stringIDToTypeID("selection"));
                    desc.putReference(stringIDToTypeID("null"), ref);
                    var ref2 = new ActionReference();
                    ref2.putEnumerated(stringIDToTypeID("channel"), stringIDToTypeID("channel"), stringIDToTypeID("transparencyEnum"));
                    desc.putReference(stringIDToTypeID("to"), ref2);
                    executeAction(stringIDToTypeID("set"), desc, DialogModes.NO);
                    debugSteps += "[2B] TrspLoaded ";
                }} catch(e1) {{
                    // Legacy Fallback
                    var idsetd = charIDToTypeID( "setd" );
                    var desc1 = new ActionDescriptor();
                    var idnull = charIDToTypeID( "null" );
                    var ref1 = new ActionReference();
                    var idChnl = charIDToTypeID( "Chnl" );
                    var idfsel = charIDToTypeID( "fsel" );
                    ref1.putProperty( idChnl, idfsel );
                    desc1.putReference( idnull, ref1 );
                    var idT = charIDToTypeID( "T" );
                    var ref2 = new ActionReference();
                    var idChnl = charIDToTypeID( "Chnl" );
                    var idTrsp = charIDToTypeID( "Trsp" );
                    ref2.putEnumerated( idChnl, idChnl, idTrsp );
                    desc1.putReference( idT, ref2 );
                    executeAction( idsetd, desc1, DialogModes.NO );
                    debugSteps += "[2C] LegacyTrsp ";
                }}
            }}

            // 2. Make Work Path (Action Manager - More Robust than DOM)
            // Equivalent to: doc.selection.makeWorkPath(tolerance);
            var idMk = charIDToTypeID( "Mk  " );
            var descPath = new ActionDescriptor();
            var idnull2 = charIDToTypeID( "null" );
            var refPath = new ActionReference();
            var idPath = charIDToTypeID( "Path" );
            refPath.putClass( idPath );
            descPath.putReference( idnull2, refPath );
            var idFrom = charIDToTypeID( "From" );
            var refSel = new ActionReference();
            var idSelc = charIDToTypeID( "Selc" );
            var idfsel2 = charIDToTypeID( "fsel" );
            refSel.putProperty( idSelc, idfsel2 );
            descPath.putReference( idFrom, refSel );
            var idTlrn = charIDToTypeID( "Tlrn" );
            var idPxl = charIDToTypeID( "#Pxl" );
            descPath.putUnitDouble( idTlrn, idPxl, {tolerance} );
            executeAction( idMk, descPath, DialogModes.NO );
            debugSteps += "[3] PathMade ";

            // 3. Create Solid Color Layer (Action Manager)
            var idMake = stringIDToTypeID( "make" );
            var descSC = new ActionDescriptor();
            var refSC = new ActionReference();
            var idContentLayer = stringIDToTypeID( "contentLayer" );
            refSC.putClass( idContentLayer );
            descSC.putReference( stringIDToTypeID( "null" ), refSC );
            var descUsng = new ActionDescriptor();
            var descType = new ActionDescriptor();
            var descColor = new ActionDescriptor();
            
            // ONI Blue Standard (R:0, G:84, B:139)
            descColor.putDouble( stringIDToTypeID("red"), 0.000000 );
            descColor.putDouble( stringIDToTypeID("green"), 84.000000 );
            descColor.putDouble( stringIDToTypeID("blue"), 139.000000 );
            
            var idSolidColorLayer = stringIDToTypeID( "solidColorLayer" );
            descType.putObject( stringIDToTypeID("color"), stringIDToTypeID("RGBColor"), descColor );
            descUsng.putObject( stringIDToTypeID("type"), idSolidColorLayer, descType );
            descSC.putObject( stringIDToTypeID("using"), idContentLayer, descUsng );
            executeAction( idMake, descSC, DialogModes.NO );
            debugSteps += "[4] SolidCreated ";

            // 4. Name it
            doc.activeLayer.name = "VECTOR_" + layer.name;
            debugSteps += "[5] Done";

            "Success: " + debugSteps
        }} catch(e) {{
            "Error at " + debugSteps + ": " + e
        }}
        """
        
        result = self.app.DoJavaScript(jsx_payload)
        
        if str(result).startswith("Success"):
            return {"status": "success", "message": str(result)}
        else:
            return {"status": "error", "message": str(result)}

    def vectorize_detailed_active_layer(self, max_colors: int = 16, tolerance: float = 1.0) -> Dict[str, str]:
        """
        [Ultra-Vector] Performs detailed multi-color vectorization.
        Protocol:
        1. Duplicate & Posterize (Reduce colors).
        2. Sample unique colors from the image.
        3. For each color: Select -> Make Path -> Create Shape Layer.
        """
        self._ensure_connection()
        if not self.app: return {"status": "error", "message": "No Connection"}

        # Advanced JSX Payload for Color Separation
        jsx_payload = f"""
        var debugSteps = "";
        try {{
            var doc = app.activeDocument;
            var originalLayer = doc.activeLayer;
            debugSteps += "[1] Start ";
            
            // CLEAR SAMPLERS (Fix for 'Create not available' error)
            try {{ doc.colorSamplers.removeAll(); }} catch(e) {{}}

            // 0. Unlock if background
            if (originalLayer.isBackgroundLayer || originalLayer.allLocked) {{
                originalLayer.isBackgroundLayer = false;
                originalLayer.allLocked = false;
            }}

            // 1. Create Vector Group
            var vectorGroup = doc.layerSets.add();
            vectorGroup.name = "VECTOR_DETAILED_" + originalLayer.name;
            
            // 2. Prepare Work Layer (Duplicate & Posterize)
            var workLayer = originalLayer.duplicate();
            workLayer.name = "Temp_Analysis";
            doc.activeLayer = workLayer;

            // --- A. ISOLATE SUBJECT (Crucial Fix) ---
            try {{
                // 1. Select Subject
                var idautoCutout = stringIDToTypeID( "autoCutout" );
                var descSubject = new ActionDescriptor();
                var idsampleAllLayers = stringIDToTypeID( "sampleAllLayers" );
                descSubject.putBoolean( idsampleAllLayers, false );
                executeAction( idautoCutout, descSubject, DialogModes.NO );
                
                // CHECK SELECTION
                var hasSelection = false;
                try {{ if(doc.selection.bounds) hasSelection = true; }} catch(e) {{}}

                if (hasSelection) {{
                    // 2. Invert Selection
                    executeAction(charIDToTypeID("Invs"), undefined, DialogModes.NO);
                    
                    var inverted = false;
                    try {{ if(doc.selection.bounds) inverted = true; }} catch(e){{}}
                    
                    if (inverted) {{
                        // 3. Clear (Delete Background)
                        executeAction(charIDToTypeID("Dlt "), undefined, DialogModes.NO);
                        debugSteps += "[2A] BackgroundRemoved ";
                    }} else {{
                        debugSteps += "[2A] InvertEmpty ";
                    }}
                }} else {{
                     debugSteps += "[2A] NoSubjectDetected ";
                }}
                
                // 4. Deselect
                doc.selection.deselect();
            }} catch(e) {{
                debugSteps += "[2A-Fail] " + e;
            }}
            
            // Posterize
            try {{
                var desc = new ActionDescriptor();
                desc.putInteger(charIDToTypeID("Lvls"), {max_colors});
                executeAction(charIDToTypeID("Pstr"), desc, DialogModes.NO);
                debugSteps += "[2] Posterized ";
            }} catch(e) {{}}

            // SAVE STATE (For Rollback if needed)
            var preIsolationState = doc.activeHistoryState;

            // --- A. ISOLATE SUBJECT ---
            try {{
                var idautoCutout = stringIDToTypeID( "autoCutout" );
                var descSubject = new ActionDescriptor();
                var idsampleAllLayers = stringIDToTypeID( "sampleAllLayers" );
                descSubject.putBoolean( idsampleAllLayers, false );
                executeAction( idautoCutout, descSubject, DialogModes.NO );
                
                var hasSelection = false;
                try {{ if(doc.selection.bounds) hasSelection = true; }} catch(e){{}}
                
                if (hasSelection) {{
                    executeAction(charIDToTypeID("Invs"), undefined, DialogModes.NO);
                    executeAction(charIDToTypeID("Dlt "), undefined, DialogModes.NO);
                    debugSteps +="[BgDel] ";
                }}
                doc.selection.deselect();
            }} catch(e) {{
                 doc.selection.deselect(); 
                 // If fail, just continue
            }}

            // 3. Extract Colors (Scan)
            var colors = [];
            var colorKeys = {{}};
            
            function scanImage() {{
                colors = []; colorKeys = {{}};
                var layer = doc.activeLayer;
                var b = layer.bounds;
                var w = b[2].value - b[0].value;
                var h = b[3].value - b[1].value;
                var step = Math.max(1, Math.floor(Math.max(w, h) / 50));
                debugSteps += "[Scan:W=" + w + ",H=" + h + ",S=" + step + "] ";
                
                // OPTIMIZATION: Reuse Single Sampler
                try {{ doc.colorSamplers.removeAll(); }} catch(e){{}}
                var sampler = null;
                try {{ sampler = doc.colorSamplers.add([b[0].value, b[1].value]); }} catch(e) {{ 
                    debugSteps += "[SamplerInitFail:" + e + "] ";
                    return;
                }}
                
                for (var x = 0; x < w; x+=step) {{
                    for (var y = 0; y < h; y+=step) {{
                        try {{
                            var sampleX = b[0].value + x + (step/2);
                            var sampleY = b[1].value + y + (step/2);
                            
                            sampler.move([sampleX, sampleY]); // Move existing sampler
                            
                            var c = sampler.color;
                            var key = Math.round(c.rgb.red) + "_" + Math.round(c.rgb.green) + "_" + Math.round(c.rgb.blue);
                            if (!colorKeys[key]) {{ colorKeys[key] = true; colors.push(c); }}
                        }} catch(err) {{}}
                        if (colors.length >= {max_colors}) break;
                    }}
                    if (colors.length >= {max_colors}) break;
                }}
                
                try {{ sampler.remove(); }} catch(e){{}}
            }}
            
            scanImage();
            debugSteps += "[3] Colors(" + colors.length + ") ";
            
            // ROLLBACK CHECK
            if (colors.length === 0) {{
                debugSteps += "[RETRY-FULL] ";
                doc.activeHistoryState = preIsolationState;
                scanImage(); // Re-scan active layer (restored)
                debugSteps += "-> " + colors.length;
            }}

            // 4. Vectorize Each Color
            if (colors.length === 0) throw "No colors found";

            for (var i = 0; i < colors.length; i++) {{
                doc.activeLayer = workLayer;
                var descC = new ActionDescriptor();
                var colorDesc = new ActionDescriptor();
                colorDesc.putDouble(charIDToTypeID("Rd  "), colors[i].rgb.red);
                colorDesc.putDouble(charIDToTypeID("Grn "), colors[i].rgb.green);
                colorDesc.putDouble(charIDToTypeID("Bl  "), colors[i].rgb.blue);
                descC.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), colorDesc);
                descC.putInteger(charIDToTypeID("Fzns"), 10);
                executeAction(charIDToTypeID("ClrR"), descC, DialogModes.NO);

                try {{
                    if (doc.selection.bounds) {{
                        var descP = new ActionDescriptor();
                        var refP = new ActionReference();
                        refP.putClass(charIDToTypeID("Path"));
                        descP.putReference(charIDToTypeID("null"), refP);
                        var refSel = new ActionReference();
                        refSel.putProperty(charIDToTypeID("csel"), charIDToTypeID("fsel"));
                        descP.putReference(charIDToTypeID("From"), refSel);
                        descP.putUnitDouble(charIDToTypeID("Tlrn"), charIDToTypeID("#Pxl"), {tolerance});
                        executeAction(charIDToTypeID("Mk  "), descP, DialogModes.NO);

                        var descL = new ActionDescriptor();
                        var refL = new ActionReference();
                        refL.putClass(stringIDToTypeID("contentLayer"));
                        descL.putReference(charIDToTypeID("null"), refL);
                        var fillDesc = new ActionDescriptor();
                        var cDesc = new ActionDescriptor();
                        cDesc.putDouble(charIDToTypeID("Rd  "), colors[i].rgb.red);
                        cDesc.putDouble(charIDToTypeID("Grn "), colors[i].rgb.green);
                        cDesc.putDouble(charIDToTypeID("Bl  "), colors[i].rgb.blue);
                        fillDesc.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), cDesc);
                        descL.putObject(charIDToTypeID("Usng"), stringIDToTypeID("solidColorLayer"), fillDesc);
                        executeAction(charIDToTypeID("Mk  "), descL, DialogModes.NO);
                        
                        doc.activeLayer.move(vectorGroup, ElementPlacement.INSIDE);
                    }}
                }} catch(eSel) {{}}
            }}
            
            doc.selection.deselect();
            workLayer.remove();
            
            "Success: " + debugSteps + " Layers:" + colors.length;

        }} catch(e) {{
            "Error: " + e + " at " + debugSteps;
        }}
        """
        
        result = self.app.DoJavaScript(jsx_payload)
        
        if str(result).startswith("Success"):
            return {"status": "success", "message": str(result)}
        else:
            return {"status": "error", "message": str(result)}
