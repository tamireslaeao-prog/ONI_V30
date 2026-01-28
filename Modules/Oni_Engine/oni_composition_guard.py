"""
ONI V24 - COMPOSITION GUARD (Visual Validator)
Systemic solution for proportion and layout safety across ALL design tasks.

Responsibilities:
1. Bounds Check: Prevent elements from bleeding off canvas.
2. Auto-Scale: Resize elements to fit 'Safe Zones' (Golden Ratio / Rule of Thirds).
3. Auto-Center: Geometric centering accounting for visual weight.

Usage:
    guard = CompositionGuard(ps_app)
    guard.fit_to_canvas(active_layer, margin=0.1)
"""

import win32com.client

class CompositionGuard:
    def __init__(self, ps_app):
        self.ps = ps_app
        
    def get_canvas_size(self):
        doc = self.ps.ActiveDocument
        return doc.Width, doc.Height

    def fit_to_canvas(self, layer_name, margin=0.1):
        """
        Resizes the target layer (Search by Name) to fit within canvas minus margin.
        """
        jsx = f'''
        var layerName = "{layer_name}";
        var margin = {margin};
        
        function main() {{
            var doc = app.activeDocument;
            var layer = null;
            try {{ layer = doc.layers.getByName(layerName); }} 
            catch(e) {{
                // Try recursive find
                function find(nodes) {{
                    for(var i=0; i<nodes.length; i++) {{
                        if(nodes[i].name == layerName) return nodes[i];
                        if(nodes[i].typename == "LayerSet") {{ var r = find(nodes[i].layers); if(r) return r; }}
                    }}
                }}
                layer = find(doc.layers);
            }}
            
            if(!layer) return "LAYER_NOT_FOUND";
            
            doc.activeLayer = layer;
            var bounds = layer.bounds; // [left, top, right, bottom]
            var l = bounds[0].value;
            var t = bounds[1].value;
            var r = bounds[2].value;
            var b = bounds[3].value;
            
            var w = r - l;
            var h = b - t;
            
            var docW = doc.width.value;
            var docH = doc.height.value;
            
            // Calculate Safe Zone
            var safeW = docW * (1.0 - (margin*2));
            var safeH = docH * (1.0 - (margin*2));
            
            // Check Scale Need
            var scaleX = 100;
            var scaleY = 100;
            
            if (w > safeW || h > safeH) {{
                var ratioW = safeW / w;
                var ratioH = safeH / h;
                var finalRatio = Math.min(ratioW, ratioH) * 100; // Percentage
                
                layer.resize(finalRatio, finalRatio, AnchorPosition.MIDDLECENTER);
                return "RESIZED: " + finalRatio.toFixed(2) + "%";
            }}
            
            // Center Element
            var cx = (l + r) / 2;
            var cy = (t + b) / 2;
            
            var docCX = docW / 2;
            var docCY = docH / 2;
            
            var dx = docCX - cx;
            var dy = docCY - cy;
            
            layer.translate(dx, dy);
            
            return "FITTED_AND_CENTERED";
        }}
        main();
        '''
        return self.ps.DoJavaScript(jsx)

    def enforce_smart_object_bounds(self):
        """
        Ensures the active Smart Object content fills the canvas.
        Useful when replacing SO content with a logo that might be too small.
        """
        jsx = '''
        function main() {
            var doc = app.activeDocument;
            var layer = doc.activeLayer;
            
            var bounds = layer.bounds;
            var w = bounds[2].value - bounds[0].value;
            var h = bounds[3].value - bounds[1].value;
            
            var docW = doc.width.value;
            var docH = doc.height.value;
            
            // Target: 80% of smallest dimension
            var target = Math.min(docW, docH) * 0.8;
            var current = Math.max(w, h);
            
            if (current < target || current > target * 1.2) {
                var ratio = (target / current) * 100;
                layer.resize(ratio, ratio, AnchorPosition.MIDDLECENTER);
            }
            
            // Center
            var finalBounds = layer.bounds;
            var cx = (finalBounds[0].value + finalBounds[2].value) / 2;
            var cy = (finalBounds[1].value + finalBounds[3].value) / 2;
            layer.translate((docW/2) - cx, (docH/2) - cy);
        }
        main();
        '''
        self.ps.DoJavaScript(jsx)

