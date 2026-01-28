
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.core.dependencies import container
from app.infrastructure.monitoring.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

class CommandRequest(BaseModel):
    action: str  # create_doc, select_tool, set_color
    params: Dict[str, Any] = {}

class StrokeRequest(BaseModel):
    points: List[List[int]]  # [[x1,y1], [x2,y2], ...]
    tool: str = "brush"
    layer: str = "ONI_Draw"

class AssetModel(BaseModel):
    path: str
    label: str = "Asset"
    y_offset: int = 0
    scale_target: int = 900

class ComposeRequest(BaseModel):
    assets: List[AssetModel]
    output_name: str = "COMPOSITION.psd"
    width: int = 2400
    height: int = 1600
    dark_mode: bool = True

@router.post("/connect")
async def connect_photoshop():
    """Force connection to Photoshop instance."""
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    success = service.connect()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to connect to Photoshop. Is it running?")
    
    return {"success": True, "message": "Connected to Photoshop via COM"}

@router.post("/open")
async def open_document(path: str = Query(..., description="Absolute path to the file")):
    """Open an existing Photoshop document."""
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        doc_name = service.open_document(path)
        return {"success": True, "opened": doc_name}
    except Exception as e:
        logger.error("open_document_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/command")
async def execute_command(request: CommandRequest):
    """Execute a generic command on Photoshop."""
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        result = None
        if request.action == "create_doc":
            # params: width, height, name
            w = request.params.get("width", 1920)
            h = request.params.get("height", 1080)
            name = request.params.get("name", "ONI_Doc")
            result = service.create_document(w, h, name)
            
        elif request.action == "set_color":
            # params: r, g, b
            r = request.params.get("r", 0)
            g = request.params.get("g", 0)
            b = request.params.get("b", 0)
            service.set_foreground_color(r, g, b)
            result = "Color set"
            
        elif request.action == "select_tool":
            # params: tool_name
            tool = request.params.get("tool_name")
            service.select_tool(tool)
            result = f"Tool selection requested: {tool}"
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
            
        return {"success": True, "action": request.action, "result": result}
        
    except Exception as e:
        logger.error("photoshop_command_failed", error=str(e))
        return {"success": False, "error": str(e)}

@router.post("/draw/stroke")
async def draw_stroke(request: StrokeRequest):
    """Draw a stroke using paths (no mouse jitter)."""
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        # Convert list of lists to list of tuples
        points_tuple = [(p[0], p[1]) for p in request.points]
        
        service.stroke_path(points_tuple, request.tool, request.layer)
        
        return {"success": True, "points_count": len(points_tuple)}
    except Exception as e:
        logger.error("photoshop_stroke_failed", error=str(e))
        return {"success": False, "error": str(e)}


# ============================================================
# PHOTOSHOP BRIDGE V2 - New Endpoints (2026-01-21)
# ============================================================

@router.get("/layers")
async def get_layers():
    """
    List all layers in the active document.
    Returns layer names, types (NORMAL, SMARTOBJECT, TEXT, GROUP), and visibility.
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        layers = service.get_layers()
        return {
            "success": True, 
            "document": service.get_document_info().get("name", "Unknown"),
            "layers": layers,
            "count": len(layers)
        }
    except Exception as e:
        logger.error("get_layers_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/layers/select")
async def select_layer(
    name: str = Query(None, description="Layer name to select"),
    index: int = Query(None, description="Layer index to select (0-based)")
):
    """
    Select a layer by name or index.
    After selection, the layer becomes the active layer for subsequent operations.
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    if not name and index is None:
        raise HTTPException(status_code=400, detail="Must provide 'name' or 'index' parameter")
    
    service = container.get("photoshop_service")
    try:
        selected_name = service.select_layer(name=name, index=index)
        return {"success": True, "selected_layer": selected_name}
    except Exception as e:
        logger.error("select_layer_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-object/open")
async def open_smart_object():
    """
    Open the currently selected Smart Object for editing.
    Equivalent to double-clicking the Smart Object thumbnail in Photoshop.
    The Smart Object's .psb file will become the active document.
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        opened_file = service.open_smart_object()
        return {"success": True, "opened_file": opened_file, "message": "Smart Object opened for editing"}
    except Exception as e:
        logger.error("open_smart_object_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/smart-object/close")
async def close_smart_object(
    save: bool = Query(True, description="Save changes before closing")
):
    """
    Close the current Smart Object (.psb) and return to parent document.
    Changes will be saved if 'save' is True (default).
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        returned_to = service.close_smart_object(save=save)
        return {"success": True, "returned_to": returned_to, "saved": save}
    except Exception as e:
        logger.error("close_smart_object_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text/replace")
async def replace_text(
    new_text: str = Query(..., description="New text to set"),
    layer_name: str = Query(None, description="Optional: specific text layer name")
):
    """
    Replace text in a text layer.
    If layer_name is not provided, uses the currently active layer.
    The layer must be of type TEXT.
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        result = service.replace_text(new_text=new_text, layer_name=layer_name)
        return {"success": True, "new_text": result}
    except Exception as e:
        logger.error("replace_text_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/info")
async def get_document_info():
    """
    Get information about the active document.
    Returns name, dimensions, path, and saved status.
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        info = service.get_document_info()
        return {"success": True, **info}
    except Exception as e:
        logger.error("get_document_info_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/document/save")
async def save_document():
    """
    Save the active document.
    Equivalent to Ctrl+S in Photoshop.
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        service.save_document()
        return {"success": True, "message": "Document saved"}
    except Exception as e:
        logger.error("save_document_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


class JSXRequest(BaseModel):
    script: str  # JavaScript/ExtendScript code to execute

@router.post("/execute-jsx")
async def execute_jsx(request: JSXRequest):
    """
    Execute arbitrary JavaScript/ExtendScript code in Photoshop.
    Use with caution - this has full access to Photoshop DOM.
    """
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    service = container.get("photoshop_service")
    try:
        result = service.execute_jsx(request.script)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error("execute_jsx_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-jsx-file")
async def execute_jsx_file(path: str = Query(..., description="Absolute path to .jsx file")):
    """
    Execute a JSX script from a file path.
    This avoids PowerShell JSON encoding issues with multi-line scripts.
    
    Usage: POST /api/photoshop/execute-jsx-file?path=C:/path/to/script.jsx
    """
    import os
    
    if not container.has("photoshop_service"):
        raise HTTPException(status_code=503, detail="Photoshop Service not initialized")
    
    # Validate file exists
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"JSX file not found: {path}")
    
    # Validate extension
    if not path.lower().endswith('.jsx'):
        raise HTTPException(status_code=400, detail="File must have .jsx extension")
    
    service = container.get("photoshop_service")
    try:
        # Read file content
        with open(path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        logger.info("execute_jsx_file", path=path, script_length=len(script_content))
        result = service.execute_jsx(script_content)
        return {"success": True, "path": path, "result": result}
    except Exception as e:
        logger.error("execute_jsx_file_failed", path=path, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# COMPOSER SERVICE (Multi-Asset Layout)
# ============================================================

@router.post("/compose")
async def compose_assets(request: ComposeRequest):
    """
    Compose multiple PSD assets into a single master document.
    Extracts 'Hero' elements (SmartObjects/Groups) from sources and arranges them.
    """
    if not container.has("composer_service"):
        raise HTTPException(status_code=503, detail="Composer Service not initialized")
    
    composer = container.get("composer_service")
    try:
        # Convert Pydantic models to dicts for the service
        assets_dicts = [a.dict() for a in request.assets]
        
        result = composer.compose_assets(
            assets=assets_dicts,
            output_name=request.output_name,
            width=request.width,
            height=request.height,
            dark_mode=request.dark_mode
        )
        return result
    except Exception as e:
        logger.error("compose_assets_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
