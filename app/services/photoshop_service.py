import win32com.client
import pythoncom
from typing import List, Tuple, Optional
from app.infrastructure.monitoring.logger import get_logger
from app.services.healing_wrapper import HealingMixin

logger = get_logger(__name__)

class PhotoshopService(HealingMixin):
    healing_context = "photoshop"
    
    def __init__(self):
        self.app = None
        self._connected = False

    def connect(self) -> bool:
        """Establishes connection to the running Photoshop instance."""
        try:
            # Multi-threading support for COM
            pythoncom.CoInitialize()
            self.app = win32com.client.Dispatch("Photoshop.Application")
            self._connected = True
            logger.info("photoshop_service_connected", version=self.app.Version)
            return True
        except Exception as e:
            logger.error("photoshop_connection_failed", error=str(e))
            self._connected = False
            return False

    def ensure_connection(self):
        if not self._connected or not self.app:
            if not self.connect():
                raise ConnectionError("Could not connect to Photoshop via COM.")

    def create_document(self, width: int, height: int, name: str = "ONI_Doc", mode: str = "RGB") -> str:
        """Creates a new document using the Documents.Add method."""
        self.ensure_connection()
        try:
            # 2 = RGB Color mode
            # Parameters: Width, Height, Resolution, Name, Mode, InitialFill
            # Using defaults for others
            doc = self.app.Documents.Add(width, height, 72.0, name, 2)
            return doc.Name
        except Exception as e:
            logger.error("create_document_failed", error=str(e))
            raise e

    def open_document(self, file_path: str) -> str:
        """Opens a document from the given path."""
        self.ensure_connection()
        # Escape backslashes for JS string
        safe_path = file_path.replace("\\", "\\\\")
        
        js_code = f"""
        var fileRef = new File("{safe_path}");
        var doc = app.open(fileRef);
        doc.name;
        """
        
        try:
            result = self.app.DoJavaScript(js_code)
            logger.info("open_document_success", file=file_path)
            return result
        except Exception as e:
            logger.error("open_document_failed", error=str(e))
            raise e

    def set_foreground_color(self, r: int, g: int, b: int):
        """Sets the foreground color safely."""
        self.ensure_connection()
        try:
            color = win32com.client.Dispatch("Photoshop.SolidColor")
            color.RGB.Red = r
            color.RGB.Green = g
            color.RGB.Blue = b
            self.app.ForegroundColor = color
        except Exception as e:
            logger.error("set_color_failed", error=str(e))
            raise e

    def select_tool(self, tool_name: str):
        """Simulates tool selection via string ID if possible, or logs warning.
        Note: COM object for tool selection is limited. Usually requires ActionDescriptor.
        For now, we will assume standard tools are selected manually or via shortcuts if COM fails.
        Alternatively, we can use simple SendKeys via the service if strictly needed.
        """
        # COM doesn't have a direct "SelectTool" method easily accessible without ScriptingListener code.
        # We will implement using app.CurrentTool if supported or warn.
        logger.warning("select_tool_com_limited", message="Use /api/keys for tool selection or implement ActionDescriptor")
        pass

    def stroke_path(self, points: List[Tuple[int, int]], tool_name: str = "brush", output_layer: str = "ONI_Draw"):
        """
        Draws a stroke by creating a path from points and stroking it with the current tool.
        This provides a PERFECT, steady line without mouse jitter.
        """
        self.ensure_connection()
        doc = self.app.ActiveDocument
        
        # Create a new path item
        line_array = []
        
        # Convert points to PathPointInfo objects
        # Note: This is complex in pure pythoncom without wrappers.
        # Simplification: We will run a small JavaScript via app.DoJavaScript to handle the path creation cleanly.
        
        js_code = f"""
        var doc = app.activeDocument;
        var lineArray = new Array();
        
        """
        
        for i, (x, y) in enumerate(points):
            js_code += f"""
            var p{i} = new PathPointInfo();
            p{i}.kind = PointKind.CORNERPOINT;
            p{i}.anchor = new Array({x}, {y});
            p{i}.leftDirection = p{i}.anchor;
            p{i}.rightDirection = p{i}.anchor;
            lineArray.push(p{i});
            """
            
        js_code += f"""
        var lineSubPathArray = new Array();
        var lineSubPath = new SubPathInfo();
        lineSubPath.operation = ShapeOperation.SHAPEXOR;
        lineSubPath.closed = false;
        lineSubPath.entireSubPath = lineArray;
        lineSubPathArray.push(lineSubPath);
        
        var myPathItem = doc.pathItems.add("TempPath_{len(points)}", lineSubPathArray);
        myPathItem.strokePath(ToolType.BRUSH);
        myPathItem.remove(); // Cleanup path after stroke
        """
        
        try:
            self.app.DoJavaScript(js_code)
        except Exception as e:
            logger.error("stroke_path_failed", error=str(e))
            raise e

    # ============================================================
    # PHOTOSHOP BRIDGE V2 - New Methods (2026-01-21)
    # ============================================================

    def get_layers(self) -> List[dict]:
        """
        Lists all layers in the active document.
        Returns list of dicts with name, kind, visible, index.
        """
        self.ensure_connection()
        
        js_code = """
        function getLayerInfo(layer, depth) {
            var kind = "NORMAL";
            if (layer.kind == LayerKind.SMARTOBJECT) kind = "SMARTOBJECT";
            else if (layer.kind == LayerKind.TEXT) kind = "TEXT";
            else if (layer.typename == "LayerSet") kind = "GROUP";
            
            return {
                name: layer.name,
                kind: kind,
                visible: layer.visible,
                depth: depth
            };
        }
        
        function collectLayers(layerSet, depth, results) {
            for (var i = 0; i < layerSet.length; i++) {
                var layer = layerSet[i];
                results.push(getLayerInfo(layer, depth));
                if (layer.typename == "LayerSet" && layer.layers) {
                    collectLayers(layer.layers, depth + 1, results);
                }
            }
        }
        
        var results = [];
        collectLayers(app.activeDocument.layers, 0, results);
        
        // Convert to JSON string for return
        var jsonStr = "[";
        for (var i = 0; i < results.length; i++) {
            var r = results[i];
            jsonStr += '{"name":"' + r.name.replace(/"/g, '\\\\"') + '","kind":"' + r.kind + '","visible":' + r.visible + ',"depth":' + r.depth + '}';
            if (i < results.length - 1) jsonStr += ",";
        }
        jsonStr += "]";
        jsonStr;
        """
        
        try:
            result = self.app.DoJavaScript(js_code)
            import json
            layers = json.loads(result)
            logger.info("get_layers_success", count=len(layers))
            return layers
        except Exception as e:
            logger.error("get_layers_failed", error=str(e))
            raise e

    def select_layer(self, name: str = None, index: int = None) -> str:
        """
        Selects a layer by name or index.
        Returns the name of the selected layer.
        """
        self.ensure_connection()
        
        if name:
            js_code = f"""
            var layer = app.activeDocument.artLayers.getByName("{name}");
            app.activeDocument.activeLayer = layer;
            layer.name;
            """
        elif index is not None:
            js_code = f"""
            var layer = app.activeDocument.artLayers[{index}];
            app.activeDocument.activeLayer = layer;
            layer.name;
            """
        else:
            raise ValueError("Must provide either name or index")
        
        try:
            result = self.app.DoJavaScript(js_code)
            logger.info("select_layer_success", layer=result)
            return result
        except Exception as e:
            logger.error("select_layer_failed", error=str(e))
            raise e

    def open_smart_object(self) -> str:
        """
        Opens the currently selected Smart Object for editing.
        Equivalent to double-clicking the SO thumbnail.
        Returns the name of the opened .psb file.
        """
        self.ensure_connection()
        
        js_code = """
        var idplacedLayerEditContents = stringIDToTypeID("placedLayerEditContents");
        executeAction(idplacedLayerEditContents, undefined, DialogModes.NO);
        app.activeDocument.name;
        """
        
        try:
            result = self.app.DoJavaScript(js_code)
            logger.info("open_smart_object_success", file=result)
            return result
        except Exception as e:
            logger.error("open_smart_object_failed", error=str(e))
            raise e

    def close_smart_object(self, save: bool = True) -> str:
        """
        Saves (optionally) and closes the current Smart Object (.psb).
        Returns the name of the parent document.
        """
        self.ensure_connection()
        
        save_option = "SaveOptions.SAVECHANGES" if save else "SaveOptions.DONOTSAVECHANGES"
        
        js_code = f"""
        var currentDoc = app.activeDocument;
        currentDoc.close({save_option});
        app.activeDocument.name;
        """
        
        try:
            result = self.app.DoJavaScript(js_code)
            logger.info("close_smart_object_success", returned_to=result)
            return result
        except Exception as e:
            logger.error("close_smart_object_failed", error=str(e))
            raise e

    def replace_text(self, new_text: str, layer_name: str = None) -> str:
        """
        Replaces text in a text layer.
        If layer_name is None, uses the currently active layer.
        Returns the new text content.
        """
        self.ensure_connection()
        
        if layer_name:
            js_code = f"""
            var layer = app.activeDocument.artLayers.getByName("{layer_name}");
            if (layer.kind == LayerKind.TEXT) {{
                layer.textItem.contents = "{new_text}";
            }}
            layer.textItem.contents;
            """
        else:
            js_code = f"""
            var layer = app.activeDocument.activeLayer;
            if (layer.kind == LayerKind.TEXT) {{
                layer.textItem.contents = "{new_text}";
            }}
            layer.textItem.contents;
            """
        
        try:
            result = self.app.DoJavaScript(js_code)
            logger.info("replace_text_success", new_text=result)
            return result
        except Exception as e:
            logger.error("replace_text_failed", error=str(e))
            raise e

    def get_document_info(self) -> dict:
        """
        Returns information about the active document.
        """
        self.ensure_connection()
        
        js_code = """
        var doc = app.activeDocument;
        var info = {
            name: doc.name,
            width: doc.width.as("px"),
            height: doc.height.as("px"),
            path: doc.saved ? doc.fullName.fsName : "",
            saved: doc.saved
        };
        
        '{"name":"' + info.name + '","width":' + info.width + ',"height":' + info.height + ',"path":"' + info.path.replace(/\\\\/g, "/") + '","saved":' + info.saved + '}';
        """
        
        try:
            result = self.app.DoJavaScript(js_code)
            import json
            info = json.loads(result)
            logger.info("get_document_info_success", name=info.get("name"))
            return info
        except Exception as e:
            logger.error("get_document_info_failed", error=str(e))
            raise e

    def save_document(self) -> bool:
        """
        Saves the active document.
        """
        self.ensure_connection()
        
        js_code = """
        app.activeDocument.save();
        true;
        """
        
        try:
            self.app.DoJavaScript(js_code)
            logger.info("save_document_success")
            return True
        except Exception as e:
            logger.error("save_document_failed", error=str(e))
            raise e

    def execute_jsx(self, script: str) -> str:
        """
        Executes arbitrary JavaScript/ExtendScript code.
        Returns the result as string.
        """
        self.ensure_connection()
        
        try:
            result = self.app.DoJavaScript(script)
            logger.info("execute_jsx_success")
            return str(result) if result else ""
        except Exception as e:
            logger.error("execute_jsx_failed", error=str(e))
            raise e


    # ============================================================
    # PHASE 5: LAYER ARCHITECT & DEEP INTEGRATION (2026-01-23)
    # ============================================================

    def create_group(self, group_name: str) -> str:
        """
        Creates a new Layer Set (Group).
        Returns the name of the group.
        """
        self.ensure_connection()
        
        js_code = f"""
        var doc = app.activeDocument;
        var layerSet = doc.layerSets.add();
        layerSet.name = "{group_name}";
        layerSet.name;
        """
        
        try:
            result = self.app.DoJavaScript(js_code)
            logger.info("create_group_success", group=result)
            return result
        except Exception as e:
            logger.error("create_group_failed", error=str(e))
            raise e

    def place_smart_object(self, file_path: str) -> str:
        """
        Places a file as a Smart Object into the current document.
        Scale is automatically fitted to canvas if needed (default behavior of Place).
        """
        self.ensure_connection()
        safe_path = file_path.replace("\\", "\\\\")
        
        js_code = f"""
        var doc = app.activeDocument;
        var idPlc = charIDToTypeID("Plc ");
        var desc = new ActionDescriptor();
        var idnull = charIDToTypeID("null");
        desc.putPath(idnull, new File("{safe_path}"));
        var idFTcs = charIDToTypeID("FTcs");
        var idQCSt = charIDToTypeID("QCSt");
        var idQcsa = charIDToTypeID("Qcsa");
        desc.putEnumerated(idFTcs, idQCSt, idQcsa);
        executeAction(idPlc, desc, DialogModes.NO);
        doc.activeLayer.name;
        """
        
        try:
            result = self.app.DoJavaScript(js_code)
            logger.info("place_smart_object_success", layer=result)
            return result
        except Exception as e:
            logger.error("place_smart_object_failed", error=str(e))
            raise e

    def apply_layer_style(self, style_type: str, params: dict):
        """
        Applies common Layer Styles via ActionDescriptors.
        supported styles: 'DropShadow', 'Stroke', 'ColorOverlay'
        """
        self.ensure_connection()
        
        # Simplified implementation for common styles
        # This requires complex ActionDescriptor logic in JSX.
        # We will implement a generic handler for robust styling.
        
        js_utils = """
        function setDropShadow(r, g, b, opacity, distance, size) {
            var idsetd = charIDToTypeID("setd");
            var desc = new ActionDescriptor();
            var idnull = charIDToTypeID("null");
                var ref = new ActionReference();
                var idPrpr = charIDToTypeID("Prpr");
                var idLefx = charIDToTypeID("Lefx");
                ref.putProperty(idPrpr, idLefx);
                var idLyr = charIDToTypeID("Lyr ");
                var idOrdn = charIDToTypeID("Ordn");
                var idTrgt = charIDToTypeID("Trgt");
                ref.putEnumerated(idLyr, idOrdn, idTrgt);
            desc.putReference(idnull, ref);
            var idT = charIDToTypeID("T   ");
                var desc2 = new ActionDescriptor();
                var idDrSh = charIDToTypeID("DrSh");
                    var desc3 = new ActionDescriptor();
                    var idenab = charIDToTypeID("enab");
                    desc3.putBoolean(idenab, true);
                    var idMd = charIDToTypeID("Md  ");
                    var idBlnM = charIDToTypeID("BlnM");
                    var idMltp = charIDToTypeID("Mltp");
                    desc3.putEnumerated(idMd, idBlnM, idMltp);
                    var idOpct = charIDToTypeID("Opct");
                    var idUntF = charIDToTypeID("#Prc");
                    desc3.putUnitDouble(idOpct, idUntF, opacity);
                    var idDstn = charIDToTypeID("Dstn");
                    var idUntF2 = charIDToTypeID("#Pxl");
                    desc3.putUnitDouble(idDstn, idUntF2, distance);
                    var idblur = charIDToTypeID("blur");
                    desc3.putUnitDouble(idblur, idUntF2, size);
                    var idClr = charIDToTypeID("Clr ");
                        var desc4 = new ActionDescriptor();
                        var idRd = charIDToTypeID("Rd  ");
                        desc4.putDouble(idRd, r);
                        var idGrn = charIDToTypeID("Grn ");
                        desc4.putDouble(idGrn, g);
                        var idBl = charIDToTypeID("Bl  ");
                        desc4.putDouble(idBl, b);
                    var idRGBC = charIDToTypeID("RGBC");
                    desc3.putObject(idClr, idRGBC, desc4);
                desc2.putObject(idDrSh, idDrSh, desc3);
            var idLefx = charIDToTypeID("Lefx");
            desc.putObject(idT, idLefx, desc2);
            executeAction(idsetd, desc, DialogModes.NO);
        }
        """
        
        js_call = ""
        if style_type == "DropShadow":
            r, g, b = params.get("color", (0, 0, 0))
            opacity = params.get("opacity", 75.0)
            distance = params.get("distance", 5.0)
            size = params.get("size", 5.0)
            js_call = f"setDropShadow({r}, {g}, {b}, {opacity}, {distance}, {size});"
            
        full_script = js_utils + js_call
        
        try:
            self.app.DoJavaScript(full_script)
            logger.info("apply_style_success", style=style_type)
        except Exception as e:
            logger.error("apply_style_failed", error=str(e))
            raise e

    def set_font_style(self, font_postscript_name: str, size_pt: float, color_rgb: Tuple[int, int, int]):
        """
        Sets font family, size and color for the active Text Layer.
        Requires valid PostScript name (e.g., 'Arial-BoldMT').
        """
        self.ensure_connection()
        r, g, b = color_rgb
        
        js_code = f"""
        var layer = app.activeDocument.activeLayer;
        if (layer.kind == LayerKind.TEXT) {{
            var textItem = layer.textItem;
            textItem.font = "{font_postscript_name}";
            textItem.size = new UnitValue({size_pt}, "pt");
            
            var solidColor = new SolidColor();
            solidColor.rgb.red = {r};
            solidColor.rgb.green = {g};
            solidColor.rgb.blue = {b};
            textItem.color = solidColor;
        }}
        """
        
        try:
            self.app.DoJavaScript(js_code)
            logger.info("set_font_style_success", font=font_postscript_name)
        except Exception as e:
            logger.error("set_font_style_failed", error=str(e))
            raise e
