bl_info = {
    "name": "ONI Bridge Server",
    "author": "ONI System",
    "version": (2, 0, 0),
    "blender": (3, 0, 0),
    "location": "Window > Toggle ONI Bridge",
    "description": "Real-time Socket Bridge for AI Control (Port 8081)",
    "category": "System",
}

import bpy
import socket
import threading
import json
import queue
import traceback
import sys
import io
from contextlib import redirect_stdout

# GLOBAL STATE
PORT = 8081
HOST = '127.0.0.1'
command_queue = queue.Queue()
server_thread = None
server_socket = None
is_running = False

def handle_client(conn, addr):
    print(f"[ONI] Connected by {addr}")
    buffer = ""
    with conn:
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                buffer += data.decode('utf-8')
                
                # Split by newline (simple protocol)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line.strip(): continue
                    
                    try:
                        payload = json.loads(line)
                        command_queue.put((conn, payload))
                    except json.JSONDecodeError:
                        print(f"[ONI] Invalid JSON: {line}")
                        
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"[ONI] Connection Error: {e}")
                break
    print(f"[ONI] Disconnected {addr}")

def server_loop():
    global server_socket, is_running
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow reuse address
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[ONI] Bridge Server listening on {HOST}:{PORT}")
        
        while is_running:
            try:
                server_socket.settimeout(1.0) # Check is_running periodically
                conn, addr = server_socket.accept()
                t = threading.Thread(target=handle_client, args=(conn, addr))
                t.daemon = True
                t.start()
            except socket.timeout:
                continue
            except Exception as e:
                if is_running: print(f"[ONI] Accept Error: {e}")
                
    except Exception as e:
        print(f"[ONI] Server Bind Error: {e}")
    finally:
        if server_socket:
            server_socket.close()
        print("[ONI] Server Stopped")

# BLENDER MAIN THREAD TIMER
def process_queue():
    while not command_queue.empty():
        conn, payload = command_queue.get()
        response = {"status": "success", "output": ""}
        
        type_ = payload.get("type", "code")
        content = payload.get("content", "")
        
        print(f"[ONI] Executing: {type_}")
        
        try:
            # Capture stdout
            f = io.StringIO()
            with redirect_stdout(f):
                if type_ == "code":
                    # EXECUTE RAW PYTHON
                    exec(content, globals(), locals())
                    
                elif type_ == "operator":
                    # EXECUTE BPY OP
                    # Expect content to be "bpy.ops.mesh.primitive_cube_add(size=2)"
                    eval(content)
                    
            response["output"] = f.getvalue()
            
            # Send Response? (Ideally yes, but conn might be busy receiving usually)
            # If protocol is sync (Request-Response), we send back.
            # Assuming Sync for now.
            try:
                conn.sendall((json.dumps(response) + "\n").encode('utf-8'))
            except:
                pass

        except Exception as e:
            traceback.print_exc()
            response["status"] = "error"
            response["error"] = str(e)
            try:
                conn.sendall((json.dumps(response) + "\n").encode('utf-8'))
            except:
                pass
                
    return 0.1 # Run every 0.1 seconds

# OPERATORS
class ONI_OT_StartBridge(bpy.types.Operator):
    """Start the ONI Socket Server"""
    bl_idname = "oni.start_bridge"
    bl_label = "Start ONI Bridge"
    
    def execute(self, context):
        global is_running, server_thread
        if is_running:
            self.report({'WARNING'}, "Bridge already running")
            return {'CANCELLED'}
            
        is_running = True
        server_thread = threading.Thread(target=server_loop)
        server_thread.daemon = True
        server_thread.start()
        
        # Register Timer
        bpy.app.timers.register(process_queue)
        
        self.report({'INFO'}, f"ONI Bridge Started on Port {PORT}")
        return {'FINISHED'}

class ONI_OT_StopBridge(bpy.types.Operator):
    """Stop the ONI Socket Server"""
    bl_idname = "oni.stop_bridge"
    bl_label = "Stop ONI Bridge"
    
    def execute(self, context):
        global is_running
        is_running = False
        if bpy.app.timers.is_registered(process_queue):
            bpy.app.timers.unregister(process_queue)
        self.report({'INFO'}, "ONI Bridge Stopping (wait for timeout)...")
        return {'FINISHED'}

class ONI_PT_Panel(bpy.types.Panel):
    bl_label = "ONI Bridge"
    bl_idname = "ONI_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ONI'
    
    def draw(self, context):
        layout = self.layout
        if is_running:
            layout.label(text=f"Running on :{PORT}", icon='WIFI')
            layout.operator("oni.stop_bridge", icon='CANCEL')
        else:
            layout.label(text="Stopped", icon='OFF')
            layout.operator("oni.start_bridge", icon='PLAY')

# REGISTRATION
classes = (ONI_OT_StartBridge, ONI_OT_StopBridge, ONI_PT_Panel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Auto-start?
    # bpy.ops.oni.start_bridge() 

def unregister():
    global is_running
    is_running = False
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    try:
        register()
        # If running from CLI or Script Editor, auto start
        bpy.ops.oni.start_bridge()
    except:
        pass
