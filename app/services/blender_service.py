import socket
import json
import structlog
from typing import Dict, Any, Optional
from app.services.self_healing_executor import get_healing_engine

logger = structlog.get_logger(__name__)

class BlenderService:
    """
    Manages REAL-TIME communication with Blender via ONI Bridge Socket (Port 8081).
    """
    
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 8081
        self.timeout = 10.0

    async def send_command(self, type_: str, content: str) -> Dict[str, Any]:
        """
        Send command to Blender Bridge.
        
        Args:
            type_: "code" (Python block) or "operator" (Single bpy.ops string)
            content: The actual code/operator
            
        Returns:
            Dict response from Blender
        """
        payload = {
            "type": type_,
            "content": content
        }
        
        logger.info("blender_send", type=type_, content_preview=content[:50])
        
        try:
            # Connect
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.host, self.port))
                
                # Send (Newline delimited JSON)
                msg = json.dumps(payload) + "\n"
                s.sendall(msg.encode('utf-8'))
                
                # Receive
                # Read chunks until newline? Or just readall for simple sync?
                # The server sends: json + "\n"
                chunks = []
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    if b'\n' in chunk:
                        break
                
                response_raw = b"".join(chunks).decode('utf-8').strip()
                if not response_raw:
                     return {"success": False, "error": "Empty response from Blender"}

                response = json.loads(response_raw)
                
                if response.get("status") == "success":
                    logger.info("blender_success", output=response.get("output"))
                    return {"success": True, "output": response.get("output")}
                else:
                    logger.error("blender_error", error=response.get("error"))
                    return {"success": False, "error": response.get("error")}

        except ConnectionRefusedError:
            logger.error("blender_connection_refused", hint="Is ONI Bridge Addon running in Blender?")
            return {"success": False, "error": "Connection Refused. Is Blender running with ONI Bridge?"}
        except socket.timeout:
            return {"success": False, "error": "Socket Timeout"}
        except Exception as e:
            logger.error("blender_socket_error", error=str(e))
            return {"success": False, "error": str(e)}

    # CONVENIENCE METHODS
    async def run_script_code(self, code: str):
        """Execute code with AUTOMATIC SELF-HEALING."""
        engine = get_healing_engine()
        
        # Wrapper to make send_command sync-compatible for healing engine
        def executor(patched_code: str) -> Dict:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in async context, use nested
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.send_command("code", patched_code))
                    return future.result()
            else:
                return asyncio.run(self.send_command("code", patched_code))
        
        # USE HEALING ENGINE (Detects, Fixes, Retries)
        return engine.execute_with_healing(code, executor, app_context="blender")

    async def run_operator(self, op_id: str):
        return await self.send_command("operator", op_id)

    # ============================================================
    # PHASE 6: 3D ARCHITECT (2026-01-23)
    # ============================================================

    async def import_model(self, file_path: str):
        """
        Imports a 3D model (OBJ, FBX, GLB) based on extension.
        """
        # Determine import command based on extension
        lower_path = file_path.lower()
        safe_path = file_path.replace("\\", "/") # Blender prefers forward slashes or double backslash
        
        cmd = ""
        if lower_path.endswith(".obj"):
            cmd = f"bpy.ops.import_scene.obj(filepath='{safe_path}')"
        elif lower_path.endswith(".fbx"):
            cmd = f"bpy.ops.import_scene.fbx(filepath='{safe_path}')"
        elif lower_path.endswith(".glb") or lower_path.endswith(".gltf"):
            cmd = f"bpy.ops.import_scene.gltf(filepath='{safe_path}')"
        else:
            return {"success": False, "error": "Unsupported file format for auto-import"}
            
        return await self.run_script_code(cmd)

    async def setup_studio_lighting(self):
        """
        Clears existing lights and sets up a standard 3-point studio lighting.
        """
        script = """
import bpy

# Delete existing lights
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='LIGHT')
bpy.ops.object.delete()

# Key Light
bpy.ops.object.light_add(type='AREA', location=(5, -5, 5))
key = bpy.context.object
key.name = "Key Light"
key.data.energy = 500
key.rotation_euler = (0.785, 0, 0.785) # 45 deg

# Fill Light
bpy.ops.object.light_add(type='AREA', location=(-4, -2, 2))
fill = bpy.context.object
fill.name = "Fill Light"
fill.data.energy = 200
fill.rotation_euler = (1.0, 0, -1.0)

# Rim Light
bpy.ops.object.light_add(type='SPOT', location=(0, 5, 4))
rim = bpy.context.object
rim.name = "Rim Light"
rim.data.energy = 1000
rim.rotation_euler = (-2.3, 0, 0)
"""
        return await self.run_script_code(script)

