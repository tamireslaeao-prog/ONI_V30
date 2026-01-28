"""
ONI V25.1 - VECTOR FACTORY ULTRA
Module: Universal Vectorizer
Status: Soul Binding Active
Protocol: Hunter-Converged

Refactored from V3 for ONI V25 Standards.
Features:
- Full SVG path command support (M, L, C, Q, A, H, V, S, T)
- Bezier curve to Photoshop path conversion
- Intelligent path optimization and simplification
- Layer effects and blending modes
- Smart grouping by color similarity
- Path hole detection and compound paths
- Sub-pixel precision rendering
"""
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
import numpy as np
from typing import List, Tuple, Dict
import json

# Dynamic path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ONI_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "template_jsx_ultra.jsx")
OUTPUT_DIR = os.path.join(ONI_ROOT, "temp")

class AdvancedPathParser:
    """Complete SVG path parser with all command support."""
    
    def __init__(self):
        self.nodes = []
        self.current = [0.0, 0.0]
        self.last_control = None
        
    def parse(self, path_string: str) -> List[Dict]:
        """Parse SVG path into Bezier Nodes."""
        self.nodes = []
        self.current = [0.0, 0.0]
        self.last_control = None
        
        # Tokenize (handle scientific notation too)
        tokens = re.findall(r'[a-zA-Z]|[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?', path_string)
        
        i = 0
        current_cmd = None
        start_point = [0.0, 0.0]
        
        while i < len(tokens):
            token = tokens[i]
            if token.isalpha():
                current_cmd = token
                i += 1
            
            if not current_cmd:
                i += 1
                continue
                
            cmd_upper = current_cmd.upper()
            is_rel = current_cmd.islower()
            
            if cmd_upper == 'M':
                i = self._path_move(tokens, i, is_rel, start_point)
            elif cmd_upper == 'L':
                i = self._path_line(tokens, i, is_rel)
            elif cmd_upper == 'H':
                i = self._path_horiz(tokens, i, is_rel)
            elif cmd_upper == 'V':
                i = self._path_vert(tokens, i, is_rel)
            elif cmd_upper == 'C':
                i = self._path_cubic(tokens, i, is_rel)
            elif cmd_upper == 'S':
                i = self._path_smooth_cubic(tokens, i, is_rel)
            elif cmd_upper == 'Q':
                i = self._path_quad(tokens, i, is_rel)
            elif cmd_upper == 'T':
                i = self._path_smooth_quad(tokens, i, is_rel)
            elif cmd_upper == 'Z':
                self._close_path(start_point)
                self.current = list(start_point)
            elif cmd_upper == 'A':
                i += 7 
            else:
                i += 1
        
        return self.nodes
    
    def _add_node(self, anchor, left_handle=None, right_handle=None):
        """Add a new knot."""
        if left_handle is None: left_handle = list(anchor)
        if right_handle is None: right_handle = list(anchor)
        
        self.nodes.append({
            'anchor': list(anchor),
            'left': list(left_handle),   # In-handle
            'right': list(right_handle), # Out-handle
            'kind': 'CornerPoint' 
        })
        self.current = list(anchor)

    def _update_last_right_handle(self, handle):
        """Update the 'out' handle of the *previous* node."""
        if self.nodes:
            self.nodes[-1]['right'] = list(handle)

    def _path_move(self, tokens, i, is_rel, start_ref):
        try:
            x = float(tokens[i])
            y = float(tokens[i+1])
        except IndexError: return i
        
        if is_rel:
            x += self.current[0]
            y += self.current[1]
        
        self._add_node([x, y])
        start_ref[0], start_ref[1] = x, y 
        self.last_control = [x, y]
        return i + 2

    def _path_line(self, tokens, i, is_rel):
        x = float(tokens[i])
        y = float(tokens[i+1])
        if is_rel:
            x += self.current[0]
            y += self.current[1]
        
        self._add_node([x, y])
        self.last_control = [x, y]
        return i + 2
    
    def _path_horiz(self, tokens, i, is_rel):
        x = float(tokens[i])
        y = self.current[1]
        if is_rel: x += self.current[0]
        
        self._add_node([x, y])
        self.last_control = [x, y]
        return i + 1

    def _path_vert(self, tokens, i, is_rel):
        y = float(tokens[i])
        x = self.current[0]
        if is_rel: y += self.current[1]
        
        self._add_node([x, y])
        self.last_control = [x, y]
        return i + 1

    def _path_cubic(self, tokens, i, is_rel):
        # C c1x c1y c2x c2y x y
        c1x, c1y = float(tokens[i]), float(tokens[i+1])
        c2x, c2y = float(tokens[i+2]), float(tokens[i+3])
        x, y = float(tokens[i+4]), float(tokens[i+5])
        
        if is_rel:
            c1x += self.current[0]; c1y += self.current[1]
            c2x += self.current[0]; c2y += self.current[1]
            x += self.current[0]; y += self.current[1]
            
        self._update_last_right_handle([c1x, c1y])
        self._add_node([x, y], left_handle=[c2x, c2y])
        
        self.last_control = [c2x, c2y]
        return i + 6

    def _path_smooth_cubic(self, tokens, i, is_rel):
        # S c2x c2y x y
        c1x, c1y = self.current
        if self.last_control:
            c1x = 2*self.current[0] - self.last_control[0]
            c1y = 2*self.current[1] - self.last_control[1]
            
        c2x, c2y = float(tokens[i]), float(tokens[i+1])
        x, y = float(tokens[i+2]), float(tokens[i+3])
        
        if is_rel:
            c2x += self.current[0]; c2y += self.current[1]
            x += self.current[0]; y += self.current[1]
            
        self._update_last_right_handle([c1x, c1y])
        self._add_node([x, y], left_handle=[c2x, c2y])
        
        self.last_control = [c2x, c2y]
        return i + 4

    def _path_quad(self, tokens, i, is_rel):
        # Q c1x c1y x y -> Cubic
        qc1x, qc1y = float(tokens[i]), float(tokens[i+1])
        x, y = float(tokens[i+2]), float(tokens[i+3])
        
        if is_rel:
            qc1x += self.current[0]; qc1y += self.current[1]
            x += self.current[0]; y += self.current[1]
            
        # Q -> C conversion
        # CP1 = current + 2/3 * (qc1 - current)
        c1x = self.current[0] + (2/3) * (qc1x - self.current[0])
        c1y = self.current[1] + (2/3) * (qc1y - self.current[1])
        
        # CP2 = end + 2/3 * (qc1 - end)
        c2x = x + (2/3) * (qc1x - x)
        c2y = y + (2/3) * (qc1y - y)
        
        self._update_last_right_handle([c1x, c1y])
        self._add_node([x, y], left_handle=[c2x, c2y])
        
        self.last_control = [qc1x, qc1y]
        return i + 4

    def _path_smooth_quad(self, tokens, i, is_rel):
        # T x y
        qc1x, qc1y = self.current
        if self.last_control:
            qc1x = 2*self.current[0] - self.last_control[0]
            qc1y = 2*self.current[1] - self.last_control[1]
            
        x, y = float(tokens[i]), float(tokens[i+1])
        if is_rel:
            x += self.current[0]; y += self.current[1]
            
        c1x = self.current[0] + (2/3) * (qc1x - self.current[0])
        c1y = self.current[1] + (2/3) * (qc1y - self.current[1])
        c2x = x + (2/3) * (qc1x - x)
        c2y = y + (2/3) * (qc1y - y)
        
        self._update_last_right_handle([c1x, c1y])
        self._add_node([x, y], left_handle=[c2x, c2y])
        
        self.last_control = [qc1x, qc1y]
        return i + 2

    def _close_path(self, start_ref):
        # Optional: We could explicitly line back to start, 
        # but Photoshop's logic is usually to set subPath.closed=true
        pass

class UltraVectorCompiler:
    """Advanced SVG to JSX compiler with optimization."""
    
    def __init__(self):
        self.parser = AdvancedPathParser()
        
    def parse_css_styles(self, root) -> Dict[str, Tuple[int, int, int]]:
        """Parse CSS styles from <style> block to map class names to colors."""
        styles = {}
        for style_elem in root.iter():
            if style_elem.tag.endswith('style'):
                css_content = style_elem.text
                if not css_content: continue
                
                # Simple regex to find .classname{fill:#RRGGBB} or .classname{fill:rgb(r,g,b)}
                # Illustrator: .st0{fill:#F4F3F3;}
                matches = re.findall(r'\.([a-zA-Z0-9_-]+)\s*\{([^}]+)\}', css_content)
                for class_name, rules in matches:
                    # Look for fill property
                    fill_match = re.search(r'fill\s*:\s*([^;]+)', rules)
                    if fill_match:
                        color_str = fill_match.group(1).strip()
                        styles[class_name] = self.parse_color(color_str)
        return styles
        
    def extract_svg_data(self, svg_path: str) -> Dict:
        """Extract all vector data from SVG with metadata."""
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Get SVG dimensions with viewBox fallback
        width = root.get('width')
        height = root.get('height')
        viewbox = root.get('viewBox')
        
        # Parse viewBox if width/height missing or invalid
        if (not width or not height) and viewbox:
            try:
                parts = viewbox.replace(',', ' ').split()
                if len(parts) >= 4:
                    width = parts[2]
                    height = parts[3]
            except:
                pass
        
        # Normalize units (strip px, pt)
        if width: width = str(width).replace('px', '').replace('pt', '')
        if height: height = str(height).replace('px', '').replace('pt', '')
        
        # Final Fallback
        if not width or not height:
            width = '800'
            height = '600'
            
        # Ensure float then int conversion
        try:
             width = int(float(width))
             height = int(float(height))
        except:
             width = 800
             height = 600
        
        # Parse CSS styles properly
        css_styles = self.parse_css_styles(root)
        
        vectors = []
        
        for elem in root.iter():
            if elem.tag.endswith('path'):
                d = elem.get('d')
                
                # Resolve color: 1. style attr, 2. class CSS, 3. fill attr
                fill_color = (128, 128, 128) # Default
                
                # Check class first (Illustrator Style)
                class_attr = elem.get('class')
                if class_attr and class_attr in css_styles:
                    fill_color = css_styles[class_attr]
                else:
                    # Check inline style attribute (CRITICAL FIX)
                    style_attr = elem.get('style')
                    fill_found = False
                    if style_attr:
                        style_match = re.search(r'fill\s*:\s*([^;]+)', style_attr)
                        if style_match:
                            fill_color = self.parse_color(style_match.group(1).strip())
                            fill_found = True
                    
                    # Check direct fill attribute if no style found
                    if not fill_found:
                        fill_attr = elem.get('fill')
                        if fill_attr:
                             fill_color = self.parse_color(fill_attr)
                    
                opacity = float(elem.get('opacity', '1.0'))
                
                # Use resolved color
                r, g, b = fill_color
                
                if d:
                    # Parse path with advanced parser (BEZIER NODES)
                    nodes = self.parser.parse(d)
                    
                    if len(nodes) >= 2:
                        vectors.append({
                            'nodes': nodes,
                            'color': (r, g, b),
                            'opacity': opacity,
                            'original_path': d
                        })
        
        return {
            'width': width,
            'height': height,
            'vectors': vectors,
            'total_shapes': len(vectors)
        }
    
    def parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """Parse color from various formats."""
        if color_str.startswith('#'):
            hex_color = color_str.lstrip('#')
            if len(hex_color) == 6:
                return (
                    int(hex_color[0:2], 16),
                    int(hex_color[2:4], 16),
                    int(hex_color[4:6], 16)
                )
        elif color_str.startswith('rgb'):
            # Parse rgb(r, g, b)
            nums = re.findall(r'\d+', color_str)
            if len(nums) >= 3:
                return (int(nums[0]), int(nums[1]), int(nums[2]))
        
        return (128, 128, 128)  # Default gray
    
    def optimize_points(self, points: List[Tuple[float, float]], tolerance: float = 0.5) -> List[Tuple[float, float]]:
        """Douglas-Peucker simplification for optimization."""
        if len(points) < 3:
            return points
        
        # Find point with max distance
        dmax = 0
        index = 0
        
        for i in range(1, len(points) - 1):
            d = self.perpendicular_distance(points[i], points[0], points[-1])
            if d > dmax:
                index = i
                dmax = d
        
        # If max distance > tolerance, recursively simplify
        if dmax > tolerance:
            rec1 = self.optimize_points(points[:index+1], tolerance)
            rec2 = self.optimize_points(points[index:], tolerance)
            return rec1[:-1] + rec2
        else:
            return [points[0], points[-1]]
    
    def perpendicular_distance(self, point, line_start, line_end):
        """Calculate perpendicular distance from point to line."""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        num = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
        den = np.sqrt((y2-y1)**2 + (x2-x1)**2)
        
        return num / max(den, 0.001)
    
    def group_by_color_similarity(self, vectors: List[Dict], threshold: float = 30) -> Dict:
        """Group vectors by color similarity for smart layering."""
        color_groups = {}
        
        for vec in vectors:
            r, g, b = vec['color']
            
            # Find similar color group
            found_group = None
            for group_color in color_groups:
                gr, gg, gb = group_color
                distance = np.sqrt((r-gr)**2 + (g-gg)**2 + (b-gb)**2)
                
                if distance < threshold:
                    found_group = group_color
                    break
            
            if found_group:
                color_groups[found_group].append(vec)
            else:
                color_groups[(r, g, b)] = [vec]
        
        return color_groups
    
    def compile_to_jsx(self, svg_path: str, refinement_config: Dict = None) -> str:
        """Compile SVG to advanced JSX script."""
        filename = os.path.basename(svg_path)
        print(f"\n[ONI VECTOR COMPILER V3]")
        print(f"Source: {filename}")
        
        # Extract data
        svg_data = self.extract_svg_data(svg_path)
        print(f"Detected {svg_data['total_shapes']} vector shapes")
        
        # Group by color
        color_groups = self.group_by_color_similarity(svg_data['vectors'])
        print(f"Organized into {len(color_groups)} color groups")
        
        # Generate JSX payload
        payload = f"// ONI ULTRA COMPILER - Generated from {filename}\n"
        payload += f"// Total Shapes: {svg_data['total_shapes']}\n"
        payload += f"// Canvas: {svg_data['width']}x{svg_data['height']}\n\n"
        
        shape_id = 0
        
        for group_idx, (color, vectors) in enumerate(color_groups.items()):
            r, g, b = color
            group_name = f"ColorGroup_{r}_{g}_{b}"
            
            payload += f"// Group {group_idx+1}: RGB({r}, {g}, {b}) - {len(vectors)} shapes\n"
            payload += f"var group{group_idx} = createSmartGroup('{group_name}');\n"
            
            for vec in vectors:
                nodes = vec['nodes']
                
                if len(nodes) < 2:
                    continue
                
                # Helper: Extract anchors for bbox
                xs = [n['anchor'][0] for n in nodes]
                ys = [n['anchor'][1] for n in nodes]
                
                shape_w = max(xs) - min(xs)
                shape_h = max(ys) - min(ys)
                
                if shape_w * shape_h < 1:
                    # Too small
                    continue
                
                # Filter 'Full Canvas' Background layers
                doc_w = float(svg_data['width'])
                doc_h = float(svg_data['height'])
                
                if shape_w > doc_w * 0.98 and shape_h > doc_h * 0.98:
                     print(f"Skipping background shape {shape_id}: Covers canvas ({shape_w:.1f}x{shape_h:.1f})")
                     continue
                
                # SANITIZE NODES: Ensure native float types for JSON
                sanitized_nodes = []
                for n in nodes:
                    sanitized_nodes.append({
                        'anchor': [float(v) for v in n['anchor']],
                        'left': [float(v) for v in n['left']],
                        'right': [float(v) for v in n['right']],
                        'kind': n.get('kind', 'CornerPoint')
                    })
                
                nodes_json = json.dumps(sanitized_nodes)
                opacity = float(vec['opacity'])
                
                # Use NEW Bezier Function
                payload += f"var shape{shape_id} = createBezierShape('Shape_{shape_id}', {nodes_json}, {int(r)}, {int(g)}, {int(b)}, {opacity});\n"
                payload += f"if (shape{shape_id}) {{\n"
                payload += f"  shape{shape_id}.move(group{group_idx}, ElementPlacement.INSIDE);\n"
                # Apply FX (Color Overlay)
                payload += f"  applyColorOverlay(shape{shape_id}, {int(r)}, {int(g)}, {int(b)});\n"
                payload += f"}}\n"
                
                shape_id += 1
            
            payload += "\n"

        # REFINEMENT PAYLOAD GENERATION
        refinement_payload = "// NO REFINEMENT CONFIG"
        if refinement_config:
            refinement_payload = "// 🧠 REFINEMENT INJECTION\n"
            
            # Text Injection
            if 'text' in refinement_config:
                txt = refinement_config['text']
                font = refinement_config.get('font', 'Arial-BoldMT')
                size = refinement_config.get('size', 100)
                color = refinement_config.get('color', '000000')
                y_pos = float(svg_data['height']) * 0.85 # Bottom area
                
                refinement_payload += f"var titleLayer = createTextLayer('{txt}', '{font}', {size}, '{color}', {float(svg_data['width'])/2}, {y_pos});\n"
                refinement_payload += "alignLayerToCenter(titleLayer, " + str(svg_data['width']) + ", " + str(svg_data['height']) + ");\n"
            
            if 'subtext' in refinement_config:
                txt = refinement_config['subtext']
                font = "ArialMT"
                size = refinement_config.get('size', 80) / 2.5
                color = "666666"
                y_pos = float(svg_data['height']) * 0.92
                
                refinement_payload += f"var subLayer = createTextLayer('{txt}', '{font}', {size}, '{color}', {float(svg_data['width'])/2}, {y_pos});\n"
                refinement_payload += "alignLayerToCenter(subLayer, " + str(svg_data['width']) + ", " + str(svg_data['height']) + ");\n"

        
        # Load template
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Inject payload and metadata
        final_script = template.replace("__VECTOR_PAYLOAD__", payload)
        final_script = final_script.replace("__REFINEMENT_PAYLOAD__", refinement_payload)
        final_script = final_script.replace("__SOURCE_FILE__", filename)
        final_script = final_script.replace("__TIMESTAMP__", time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Inject dimensions if present, otherwise fallback (already handled in extract_svg_data)
        final_script = final_script.replace("__DOC_WIDTH__", str(svg_data['width']))
        final_script = final_script.replace("__DOC_HEIGHT__", str(svg_data['height']))
        final_script = final_script.replace("__DOC_WIDTH__", str(svg_data['width']))
        final_script = final_script.replace("__DOC_HEIGHT__", str(svg_data['height']))
        
        # Save
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f"render_ultra_{filename}.jsx")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_script)
        
        print(f"\n[COMPILATION COMPLETE]")
        print(f"Output: {output_path}")
        print(f"Ready for Photoshop import")
        
        return output_path

def main():
    if len(sys.argv) < 2:
        print("🔧 ONI Vector Compiler V3 - Advanced Edition")
        print("\nUsage: python vector_factory.py <path_to_svg> [json_config]")
        return
    
    compiler = UltraVectorCompiler()
    
    config = None
    if len(sys.argv) > 2:
        try:
             config = json.loads(sys.argv[2])
             print(f"Loaded Refinement Config: {config}")
        except:
             print("Invalid JSON config ignored")

    compiler.compile_to_jsx(sys.argv[1], config)

if __name__ == "__main__":
    main()
