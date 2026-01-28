
import win32com.client
import os
import sys

# --- Config ---
ASSETS_DIR = r"c:\Users\user\Desktop\ONI_V30\temp\poster_assets"
RICK_IMG = os.path.join(ASSETS_DIR, "rick_render.png")
OUTPUT_PSD = os.path.join(ASSETS_DIR, "Rick_Poster.psd")

def create_poster():
    try:
        ps = win32com.client.Dispatch("Photoshop.Application")
    except Exception as e:
        print(f"❌ Could not connect to Photoshop: {e}")
        return

    print("🎨 Connected to Photoshop")
    
    # 1. Create Document (1080x1350, 72dpi for screen, Dark Grey)
    # Documents.Add(Width, Height, Resolution, Name, Mode, InitialFill)
    doc = ps.Documents.Add(1080, 1350, 72, "Rick_Sanchez_Vile", 2, 2) # 2=RGB, 2=Transparent
    
    # Fill Background
    ps.DoJavaScript("""
    var c = new SolidColor(); 
    c.rgb.hexValue = '1a1a1a'; 
    app.activeDocument.selection.selectAll();
    app.activeDocument.selection.fill(c);
    app.activeDocument.selection.deselect();
    app.activeDocument.activeLayer.name = "Background";
    """)

    # 2. Place Rick
    if os.path.exists(RICK_IMG):
        print(f"🖼️ Placing {RICK_IMG}...")
        # Use JS for Place as it's more reliable than COM AddLayer
        js_place = f"""
        var f = new File("{RICK_IMG.replace(os.sep, '/')}");
        if(f.exists) {{
            var idPlc = charIDToTypeID( "Plc " );
            var desc = new ActionDescriptor();
            var idnull = charIDToTypeID( "null" );
            desc.putPath( idnull, f );
            executeAction( idPlc, desc, DialogModes.NO );
            app.activeDocument.activeLayer.name = "Rick Source";
            
            // Resize to 80% width if needed
            // But usually render is sized ok. Let's move him slightly up.
            var l = app.activeDocument.activeLayer;
            l.translate(0, -100); 
        }}
        """
        ps.DoJavaScript(js_place)
    else:
        print("❌ Rick Image not found!")

    # 3. Typography: "RICK"
    # ArtLayer.Kind: 1=Normal, 2=Text
    l_rick = doc.ArtLayers.Add()
    l_rick.Kind = 2 # Text
    t_rick = l_rick.TextItem
    t_rick.Contents = "RICK"
    t_rick.Size = 250
    t_rick.Font = "Arial-Black" # Safe font, user likely has it
    t_rick.Justification = 2 # Center
    
    # Color White
    js_color_white = """
    var c=new SolidColor(); c.rgb.hexValue='FFFFFF';
    app.activeDocument.activeLayer.textItem.color = c;
    """
    ps.DoJavaScript(js_color_white)
    
    # Position
    # Note: TextItem.Position is [x, y] of baseline
    t_rick.Position = [540, 1100] # Center X, Lower Y
    l_rick.Name = "Text: RICK"

    # 4. Typography: "SANCHEZ"
    l_sanchez = doc.ArtLayers.Add()
    l_sanchez.Kind = 2
    t_sanchez = l_sanchez.TextItem
    t_sanchez.Contents = "SANCHEZ"
    t_sanchez.Size = 120
    t_sanchez.Font = "Arial-BoldMT"
    t_sanchez.Justification = 2
    
    # Color Neon Green
    js_color_green = """
    var c=new SolidColor(); c.rgb.hexValue='39FF14'; // Neon Green
    app.activeDocument.activeLayer.textItem.color = c;
    """
    ps.DoJavaScript(js_color_green)
    
    t_sanchez.Position = [540, 1220]
    l_sanchez.Name = "Text: SANCHEZ"
    
    # 5. Typography: "VILEPROJETOS"
    l_vile = doc.ArtLayers.Add()
    l_vile.Kind = 2
    t_vile = l_vile.TextItem
    t_vile.Contents = "VILEPROJETOS"
    t_vile.Size = 40
    t_vile.Font = "CourierNewPS-BoldMT" # Techy mono
    t_vile.Tracking = 300 # Wide spacing
    t_vile.Justification = 2
    
    # Color Grey
    js_color_grey = """
    var c=new SolidColor(); c.rgb.hexValue='888888';
    app.activeDocument.activeLayer.textItem.color = c;
    """
    ps.DoJavaScript(js_color_grey)
    
    t_vile.Position = [540, 1300]
    l_vile.Name = "Branding"

    # 6. Apply Styles (Outer Glow on Rick)
    # We select the "Rick Source" layer and apply a style via JS Action
    ps.DoJavaScript("""
    try {
        var doc = app.activeDocument;
        var l = doc.artLayers.getByName("Rick Source");
        doc.activeLayer = l;
        
        // Add Outer Glow (Green)
        var idsetd = charIDToTypeID( "setd" );
        var desc2 = new ActionDescriptor();
        var idnull = charIDToTypeID( "null" );
            var ref1 = new ActionReference();
            var idPrpr = charIDToTypeID( "Prpr" );
            var idLefx = charIDToTypeID( "Lefx" );
            ref1.putProperty( idPrpr, idLefx );
            var idLyr = charIDToTypeID( "Lyr " );
            var idOrdn = charIDToTypeID( "Ordn" );
            var idTrgt = charIDToTypeID( "Trgt" );
            ref1.putEnumerated( idLyr, idOrdn, idTrgt );
        desc2.putReference( idnull, ref1 );
        var idT = charIDToTypeID( "T   " );
            var desc3 = new ActionDescriptor();
            var idScl = charIDToTypeID( "Scl " );
            var idPrc = charIDToTypeID( "#Prc" );
            desc3.putUnitDouble( idScl, idPrc, 100.000000 );
            var idOrGl = charIDToTypeID( "OrGl" );
                var desc4 = new ActionDescriptor();
                var idenab = charIDToTypeID( "enab" );
                desc4.putBoolean( idenab, true );
                var idMd = charIDToTypeID( "Md  " );
                var idBlnM = charIDToTypeID( "BlnM" );
                var idScrn = charIDToTypeID( "Scrn" );
                desc4.putEnumerated( idMd, idBlnM, idScrn );
                var idClr = charIDToTypeID( "Clr " );
                    var desc5 = new ActionDescriptor();
                    var idRd = charIDToTypeID( "Rd  " );
                    desc5.putDouble( idRd, 57.0 );
                    var idGrn = charIDToTypeID( "Grn " );
                    desc5.putDouble( idGrn, 255.0 );
                    var idBl = charIDToTypeID( "Bl  " );
                    desc5.putDouble( idBl, 20.0 );
                var idRGBC = charIDToTypeID( "RGBC" );
                desc4.putObject( idClr, idRGBC, desc5 );
                var idOpct = charIDToTypeID( "Opct" );
                var idPrc = charIDToTypeID( "#Prc" );
                desc4.putUnitDouble( idOpct, idPrc, 60.000000 );
                var idSz = charIDToTypeID( "Sz  " );
                var idPxl = charIDToTypeID( "#Pxl" );
                desc4.putUnitDouble( idSz, idPxl, 50.000000 );
            var idOrGl = charIDToTypeID( "OrGl" );
            desc3.putObject( idOrGl, idOrGl, desc4 );
        var idLefx = charIDToTypeID( "Lefx" );
        desc2.putObject( idT, idLefx, desc3 );
        executeAction( idsetd, desc2, DialogModes.NO );
    } catch(e) { 
        // Ignore style errors 
    }
    """)

    print("✅ Poster Created Successfully!")

if __name__ == "__main__":
    create_poster()
