
import os
import re

class SVGToPhotoshopJSX:
    """
    Parses a simple SVG (M/L/Z commands) and generates a Photoshop JSX script
    that reconstructs the vector paths as NATIVE Shape Layers.
    """
    
    def __init__(self, svg_path):
        self.svg_path = svg_path
        self.layers = [] # List of {color: hex, paths: [list of points]}
        
    def parse(self):
        """
        Naive SVG parser tailored for ONI TraceReactor output (PolyLines).
        Does NOT support curves (C/S/Q) yet, assuming TraceReactor outputs L-only approximations 
        (TraceReactor typically uses approxPolyDP -> Lines).
        """
        if not os.path.exists(self.svg_path):
            raise FileNotFoundError(f"SVG not found: {self.svg_path}")
            
        with open(self.svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find Groups (Layers)
        # <g id="..." fill="#123456" ...> ... </g>
        # This regex is simple and works on the constrained output of SVGComposer
        
        g_pattern = re.compile(r'<g[^>]*fill="([^"]+)"[^>]*>(.*?)</g>', re.DOTALL)
        path_pattern = re.compile(r'<path d="([^"]+)"')
        
        matches = g_pattern.findall(content)
        
        for color, inner_content in matches:
            paths_data = path_pattern.findall(inner_content)
            parsed_paths = []
            
            for d in paths_data:
                # Parse 'M x y L x y ... Z'
                # Remove letters and split
                # Assuming output is like "M 10 20 L 30 40 L 50 60 Z"
                
                # Normalize
                d = d.replace('M', ' M ').replace('L', ' L ').replace('Z', ' Z ')
                tokens = d.split()
                
                points = []
                cmd = None
                i = 0
                while i < len(tokens):
                    t = tokens[i]
                    if t in ['M', 'L']:
                        cmd = t
                        x = float(tokens[i+1])
                        y = float(tokens[i+2])
                        points.append((x, y))
                        i += 3
                    elif t == 'Z':
                        # Close path (optional logic)
                        i += 1
                    else:
                        # Should not happen in strict M/L output
                        i += 1
                        
                if points:
                    parsed_paths.append(points)
            
            if parsed_paths:
                self.layers.append({"color": color, "paths": parsed_paths})
                
    def generate_jsx(self, output_jsx_path):
        """
        Writes the JSX file.
        Uses 'PathPointInfo' to create paths and 'makeFillLayer' to color them.
        """
        
        jsx = [
            "// ONI NATIVE VECTOR RESTRUCTOR (GENERATED)",
            "app.preferences.rulerUnits = Units.PIXELS;",
            "var doc = app.activeDocument;",
            "",
            "function hexToRgb(hex) {",
            "    var r = parseInt(hex.substring(1,3), 16);",
            "    var g = parseInt(hex.substring(3,5), 16);",
            "    var b = parseInt(hex.substring(5,7), 16);",
            "    var c = new SolidColor();",
            "    c.rgb.red = r; c.rgb.green = g; c.rgb.blue = b;",
            "    return c;",
            "}",
            "",
            "function drawShape(points, colorHex) {",
            "    var lineArray = new Array();",
            "    for (var i = 0; i < points.length; i++) {",
            "        var p = new PathPointInfo();",
            "        p.kind = PointKind.CORNERPOINT;",
            "        p.anchor = points[i];",
            "        p.leftDirection = points[i];",
            "        p.rightDirection = points[i];",
            "        lineArray.push(p);",
            "    }",
            "    var subPath = new SubPathInfo();",
            "    subPath.operation = ShapeOperation.SHAPEXOR;",
            "    subPath.closed = true;",
            "    subPath.entireSubPath = lineArray;",
            "",
            "    return subPath;",
            "}",
            "",
            "// --- LAYERS ---"
        ]
        
        # We iterate in reverse to stack correctly (or normal? SVG is Paint Order).
        # SVGComposer: Layer 0 (Bottom) -> Layer N (Top).
        # PS: Adding layer puts it on top. So we verify order.
        
        for i, layer in enumerate(self.layers):
            color = layer['color']
            paths = layer['paths']
            
            jsx.append(f"// Layer {i} - {color}")
            jsx.append("var subPaths = new Array();")
            
            # Optimization: If too many paths, PS crashes. Chunking might be needed.
            # But for simple logos/text (Universal Vector target), it's fine.
            
            for points in paths:
                # Convert py points to js array of [x, y]
                pts_str = ", ".join([f"[{p[0]},{p[1]}]" for p in points])
                jsx.append(f"subPaths.push(drawShape([{pts_str}], '{color}'));")
                
            jsx.append("var myPathItem = doc.pathItems.add('TempPath_" + str(i) + "', subPaths);")
            
            # Convert Path to Shape Layer
            # This is the tricky part. 'makeFillLayer' uses current path.
            
            jsx.append(f"var layerColor = hexToRgb('{color}');")
            
            # Action Manager code to create Solid Fill Layer from Current Path
            # This is robust.
            
            jsx.append("""
            var idMk = charIDToTypeID( "Mk  " );
            var desc = new ActionDescriptor();
            var idnull = charIDToTypeID( "null" );
                var ref = new ActionReference();
                var idcontentLayer = stringIDToTypeID( "contentLayer" );
                ref.putClass( idcontentLayer );
            desc.putReference( idnull, ref );
            var idUsng = charIDToTypeID( "Usng" );
                var desc2 = new ActionDescriptor();
                var idType = charIDToTypeID( "Type" );
                    var desc3 = new ActionDescriptor();
                    var idClr = charIDToTypeID( "Clr " );
                        var desc4 = new ActionDescriptor();
                        var idRd = charIDToTypeID( "Rd  " );
                        desc4.putDouble( idRd, layerColor.rgb.red );
                        var idGrn = charIDToTypeID( "Grn " );
                        desc4.putDouble( idGrn, layerColor.rgb.green );
                        var idBl = charIDToTypeID( "Bl  " );
                        desc4.putDouble( idBl, layerColor.rgb.blue );
                    var idRGBC = charIDToTypeID( "RGBC" );
                    desc3.putObject( idClr, idRGBC, desc4 );
                var idsolidColorLayer = stringIDToTypeID( "solidColorLayer" );
                desc2.putObject( idType, idsolidColorLayer, desc3 );
            desc.putObject( idUsng, idcontentLayer, desc2 );
            executeAction( idMk, desc, DialogModes.NO );
            """)
            
            # Cleanup Path
            jsx.append("myPathItem.remove();")
            jsx.append("")
            
        with open(output_jsx_path, 'w') as f:
            f.write("\n".join(jsx))

if __name__ == "__main__":
    # Test
    pass
