"""
ONI Maya Bridge
Direct communication with Autodesk Maya via Python/MEL.

Usage:
    from ONI_Maya_Bridge import MayaBridge
    
    bridge = MayaBridge()
    bridge.execute("cmds.polyCube()")
    bridge.render(output="render.png")

Version: 1.0.0
"""

import subprocess
import os
import json
import tempfile
import socket
from typing import Optional, Dict, Any, List
from pathlib import Path


class MayaBridge:
    """
    Bridge for controlling Maya via mayapy or command port.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, maya_path: Optional[str] = None, command_port: int = 7001):
        """
        Initialize Maya Bridge.
        
        Args:
            maya_path: Path to Maya installation
            command_port: Port for Maya command port communication
        """
        self.maya_path = maya_path or self._find_maya()
        self.command_port = command_port
        self.temp_dir = tempfile.mkdtemp(prefix="oni_maya_")
        
        if not self.maya_path:
            raise RuntimeError("Maya not found. Please install or specify path.")
        
        self.mayapy = os.path.join(self.maya_path, "bin", "mayapy.exe")
        self.maya_exe = os.path.join(self.maya_path, "bin", "maya.exe")
    
    def _find_maya(self) -> Optional[str]:
        """Auto-detect Maya installation."""
        import glob
        
        base = r"C:\Program Files\Autodesk"
        folders = glob.glob(os.path.join(base, "Maya*"))
        
        if folders:
            folders.sort(reverse=True)  # Latest first
            for folder in folders:
                if os.path.exists(os.path.join(folder, "bin", "maya.exe")):
                    return folder
        return None
    
    def _create_script(self, code: str, script_name: str = "oni_script.py") -> str:
        """Create a temporary Python script."""
        script_path = os.path.join(self.temp_dir, script_name)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(code)
        return script_path
    
    # =========================================================================
    # EXECUTION METHODS
    # =========================================================================
    
    def execute(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute Python code. Prioritizes the LIVE session (GUI).
        Falls back to standalone only if absolutely necessary.
        """
        # Try Live Session first
        live_response = self.send_command(code)
        if "Error:" not in live_response:
            return {"success": True, "output": live_response, "error": ""}
            
        # Fallback to standalone if it's a batch-type task or Live failed
        return self.execute_mayapy(code, timeout)

    def send_command(self, command: str) -> str:
        """
        Send command to Maya's command port (Live GUI session).
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect(('localhost', self.command_port))
            # Ensure Python execution mode
            escaped_cmd = command.replace("\\", "\\\\").replace("\"", "\\\"")
            py_cmd = f'python("{escaped_cmd}")'
            sock.send(py_cmd.encode() + b'\n')
            response = sock.recv(4096).decode()
            sock.close()
            return response
        except Exception as e:
            return f"Error: Command Port (Live Session) not responsive on port {self.command_port}. {e}"

    def execute_mayapy(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute Python code using mayapy (headless)."""
        
        # Wrap code to catch errors and print output
        wrapped_code = f'''
import sys
import traceback
try:
    import maya.standalone
    maya.standalone.initialize(name='python')
    import maya.cmds as cmds
    
    {code}
    
except Exception as e:
    print("FATAL ERROR:")
    traceback.print_exc()
finally:
    # maya.standalone.uninitialize() # Often crashes in script mode
    pass
'''
        script = self._create_script(wrapped_code, "oni_exec.py")
        
        try:
            cmd = [self.mayapy, script]
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                timeout=timeout
            )
            
            success = result.returncode == 0
            return {
                "success": success, 
                "output": result.stdout, 
                "error": result.stderr if not success else ""
            }
            
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    # =========================================================================
    # REFACTORED FILE OPERATIONS (Targeting Live GUI)
    # =========================================================================
    
    def new_scene(self) -> Dict[str, Any]:
        return self.execute('cmds.file(new=True, force=True)')
    
    def open_file(self, filepath: str) -> Dict[str, Any]:
        safe_path = filepath.replace("\\", "/")
        return self.execute(f'cmds.file("{safe_path}", open=True, force=True)')
    
    def create_object(self, obj_type: str, name: str = None) -> Dict[str, Any]:
        primitives = {
            "cube": "polyCube", "sphere": "polySphere", "cylinder": "polyCylinder",
            "plane": "polyPlane", "cone": "polyCone", "torus": "polyTorus",
        }
        cmd = primitives.get(obj_type.lower(), "polyCube")
        code = f'obj = cmds.{cmd}()[0]\n'
        if name: code += f'cmds.rename(obj, "{name}")'
        return self.execute(code)
    
    def list_objects(self, obj_type: str = "transform") -> Dict[str, Any]:
        code = f'import json; print(json.dumps(cmds.ls(type="{obj_type}")))'
        return self.execute(code)
    
    def delete_object(self, name: str) -> Dict[str, Any]:
        return self.execute(f'cmds.delete("{name}")')
    
    def move_object(self, name: str, x: float, y: float, z: float) -> Dict[str, Any]:
        return self.execute(f'cmds.move({x}, {y}, {z}, "{name}")')
    
    def rotate_object(self, name: str, x: float, y: float, z: float) -> Dict[str, Any]:
        """Rotate object."""
        return self.execute_mayapy(f'cmds.rotate({x}, {y}, {z}, "{name}")')
    
    def scale_object(self, name: str, x: float, y: float, z: float) -> Dict[str, Any]:
        """Scale object."""
        return self.execute_mayapy(f'cmds.scale({x}, {y}, {z}, "{name}")')
    
    # =========================================================================
    # RENDERING
    # =========================================================================
    
    def render(self, output: str, width: int = 1920, height: int = 1080,
               renderer: str = "vray") -> Dict[str, Any]:
        """Render current scene."""
        code = f'''
# Set renderer
cmds.setAttr("defaultRenderGlobals.currentRenderer", "{renderer}", type="string")

# Resolution
cmds.setAttr("defaultResolution.width", {width})
cmds.setAttr("defaultResolution.height", {height})

# Output
cmds.setAttr("defaultRenderGlobals.imageFilePrefix", r"{output}", type="string")

# Render
cmds.render()
print(f"Rendered to: {output}")
'''
        return self.execute_batch(code)
    
    def setup_vray(self, quality: str = "production") -> Dict[str, Any]:
        presets = {"ultra": {"subdivs": 64, "threshold": 0.001},"production": {"subdivs": 24, "threshold": 0.005},"preview": {"subdivs": 4, "threshold": 0.05}}
        s = presets.get(quality, presets["production"])
        code = f'if not cmds.pluginInfo("vrayformaya", q=True, l=True): cmds.loadPlugin("vrayformaya")\n'
        code += 'cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")\n'
        code += f'cmds.setAttr("vraySettings.dmcMaxSubdivs", {s["subdivs"]})\n'
        return self.execute(code)

    def create_material(self, name: str, color: tuple = (0.5, 0.5, 0.5), mat_type: str = "lambert") -> Dict[str, Any]:
        code = f'mat = cmds.shadingNode("{mat_type}", asShader=True, name="{name}")\n'
        code += f'sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat+"SG")\n'
        code += f'cmds.connectAttr(mat+".outColor", sg+".surfaceShader")\n'
        code += f'cmds.setAttr(mat+".color", {color[0]}, {color[1]}, {color[2]}, type="double3")'
        return self.execute(code)

    def create_camera(self, name: str = "renderCam", position: tuple = (10, 10, 10)) -> Dict[str, Any]:
        code = f'cam = cmds.camera(name="{name}")[0]\ncmds.move({position[0]}, {position[1]}, {position[2]}, cam)\ncmds.viewFit(cam, all=True)'
        return self.execute(code)
    
    def create_light(self, light_type: str = "directional", name: str = None,
                     intensity: float = 1.0) -> Dict[str, Any]:
        """Create a light."""
        light_types = {
            "directional": "directionalLight",
            "point": "pointLight",
            "spot": "spotLight",
            "area": "areaLight",
        }
        
        lt = light_types.get(light_type, "directionalLight")
        code = f'''
light = cmds.{lt}()
cmds.setAttr(f"{{light}}.intensity", {intensity})
{f'cmds.rename(light, "{name}")' if name else ''}
print(f"Created light: {{light}}")
'''
        return self.execute_mayapy(code)


# ==============================================================================
# STANDALONE TEST
# ==============================================================================

if __name__ == "__main__":
    try:
        bridge = MayaBridge()
        print(f"Maya found at: {bridge.maya_path}")
        print(f"Mayapy: {bridge.mayapy}")
    except Exception as e:
        print(f"Maya not found: {e}")
