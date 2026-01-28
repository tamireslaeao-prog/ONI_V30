import sys
import os
from typing import Any
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

logger = get_logger(__name__)

class AfterEffectsService(HealingMixin):
    healing_context = "aftereffects"
    """
    ONIV24 Service Wrapper for After Effects.
    Delegates commands to the ONI_AfterEffects_Bridge.
    """
    def __init__(self):
        self.bridge = None
        self._connected = False

    def connect(self) -> bool:
        try:
            from Modules.AfterEffects.ONI_AfterEffects_Bridge import AfterEffectsBridge
            self.bridge = AfterEffectsBridge()
            if self.bridge.connect():
                self._connected = True
                logger.info("ae_service_connected")
                return True
            return False
        except Exception as e:
            logger.error("ae_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.bridge:
            if not self.connect():
                raise ConnectionError("Could not connect to After Effects.")

    # WRAPPERS
    def run_jsx(self, jsx_code: str):
        self.ensure_connection()
        return self.bridge.run_jsx(jsx_code)

    def create_composition(self, name, width, height, duration):
        self.ensure_connection()
        # Using a helper method if exists in bridge or raw JSX
        script = f'app.project.items.addComp("{name}", {width}, {height}, 1.0, {duration}, 30);'
        return self.run_jsx(script)

    # ============================================================
    # PHASE 7: MOTION ARCHITECT (2026-01-23)
    # ============================================================

    def import_footage(self, file_path: str):
        """
        Imports a file into the project bin.
        """
        safe_path = file_path.replace("\\", "\\\\")
        jsx = f"""
        var io = new ImportOptions(new File("{safe_path}"));
        var item = app.project.importFile(io);
        item.name;
        """
        return self.run_jsx(jsx)

    def add_to_comp(self, comp_name: str, footage_name: str):
        """
        Adds a footage item to a composition by name matching.
        """
        jsx = f"""
        var comp = null;
        var footage = null;
        for (var i = 1; i <= app.project.numItems; i++) {{
            if (app.project.item(i).name == "{comp_name}" && app.project.item(i) instanceof CompItem) {{
                comp = app.project.item(i);
            }}
            if (app.project.item(i).name == "{footage_name}") {{
                footage = app.project.item(i);
            }}
        }}
        if (comp && footage) {{
            comp.layers.add(footage);
        }}
        """
        return self.run_jsx(jsx)

    def set_keyframe(self, layer_index: int, property_name: str, time: float, value: Any):
        """
        Sets a keyframe.
        property_name example: "Opacity", "Position", "Scale"
        """
        # Value formatting needs to handle arrays (Position) vs scalars (Opacity)
        val_str = str(value)
        if isinstance(value, (list, tuple)):
            val_str = f"[{', '.join(map(str, value))}]"

        jsx = f"""
        var comp = app.project.activeItem;
        if (comp && comp instanceof CompItem) {{
            var layer = comp.layer({layer_index});
            var prop = layer.property("{property_name}");
            if (prop) {{
                prop.setValueAtTime({time}, {val_str});
            }}
        }}
        """
        return self.run_jsx(jsx)
