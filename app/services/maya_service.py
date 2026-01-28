import sys
import os
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

logger = get_logger(__name__)

class MayaService(HealingMixin):
    healing_context = "maya"
    """
    ONIV24 Service Wrapper for Autodesk Maya.
    Delegates commands to the ONI_Maya_Bridge.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        try:
            from Modules.Maya.ONI_Maya_Bridge import MayaBridge
            self.bridge = MayaBridge()
            # Maya bridge likely uses socket or command port
            if self.bridge.connect():
                self._connected = True
                logger.info("maya_service_connected")
                return True
            return False
        except Exception as e:
            logger.error("maya_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge:
            if not self.connect():
                raise ConnectionError("Could not connect to Maya.")

    def run_python_command(self, cmd: str):
        self.ensure_connection()
        return self.bridge.execute(cmd)

    def run_mel_command(self, cmd: str):
        self.ensure_connection()
        # For MEL, we still use the socket directly or the bridge's send_command wrapped in MEL
        return self.bridge.send_command(f'mel.eval("{cmd}")')

    # ============================================================
    # PHASE 7.5: MAYA ARCHITECT (2026-01-23)
    # ============================================================

    def create_reference(self, file_path: str, namespace: str):
        """
        Creates a file reference (Standard for Animation/VFX pipelines).
        """
        safe_path = file_path.replace("\\", "/")
        py_cmd = f"cmds.file('{safe_path}', reference=True, namespace='{namespace}')"
        return self.run_python_command(py_cmd)

    def setup_arnold_render(self, width: int = 1920, height: int = 1080):
        """
        Sets up Arnold Renderer defaults.
        """
        py_cmd = f"""
import  maya.cmds as cmds
# Set Render Engine to Arnold
try:
    cmds.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')
except:
    pass # Arnold might not be loaded

# Set Resolution
cmds.setAttr('defaultResolution.width', {width})
cmds.setAttr('defaultResolution.height', {height})
cmds.setAttr('defaultResolution.deviceAspectRatio', {width}/{height})

# Basic AOV Setup (Beauty)
# Assuming mtoa is loaded
"""
        return self.run_python_command(py_cmd)

    def create_camera_rig(self, camera_name: str, focal_length: float = 35.0):
        """
        Creates a camera with specified focal length.
        """
        py_cmd = f"""
cam = cmds.camera(name='{camera_name}')[0]
cmds.setAttr(cam + '.focalLength', {focal_length})
cmds.setAttr(cam + '.locatorScale', 5)
"""
        return self.run_python_command(py_cmd)
