"""
CorelDRAW API Routes
Endpoints for CorelDRAW automation and vectorization
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import base64
import cv2
import numpy as np

from app.core.dependencies import container
from app.infrastructure.monitoring.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ============================================================
# Models
# ============================================================

class BezierPointsRequest(BaseModel):
    points: List[List[float]]  # [[x, y], [x, y], ...]
    smooth: bool = True
    closed: bool = False
    outline_color: Optional[List[int]] = None  # [R, G, B]
    fill_color: Optional[List[int]] = None  # [R, G, B]
    use_pixels: bool = True  # If True, points are pixel coords; if False, page coords


class VectorizeRequest(BaseModel):
    threshold: int = 127
    min_area: int = 100
    epsilon_factor: float = 0.005


# ============================================================
# Endpoints
# ============================================================

@router.get("/connect")
async def connect_corel():
    """
    Conecta ao CorelDRAW (inicia se necessário).
    """
    try:
        service = container.get("corel_service")
        success = service.connect()
        
        if success:
            return {
                "status": "connected",
                "version": service.version,
                "document": service.doc.Name if service.doc else None
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to connect to CorelDRAW")
    except Exception as e:
        logger.error("corel_connect_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """
    Retorna status da conexão com CorelDRAW.
    """
    try:
        service = container.get("corel_service")
        return {
            "connected": service._connected,
            "version": service.version,
            "document": service.doc.Name if service.doc else None,
            "page_size": (service.page.SizeWidth, service.page.SizeHeight) if service.page else None
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}


@router.get("/capture")
async def capture_page(dpi: int = 150):
    """
    Captura a página atual como imagem.
    Retorna base64 encoded PNG e metadados.
    """
    try:
        service = container.get("corel_service")
        ai_interface = container.get("corel_ai_interface")
        
        result = ai_interface.load_page_image(dpi=dpi)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        # Encode image as base64
        img_rgb = ai_interface.current_image
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.png', img_bgr)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "status": "success",
            "image_base64": img_base64,
            "shape": result["shape"],
            "page_size": result["page_size"],
            "dpi": dpi,
            "metadata": ai_interface.current_metadata
        }
    except Exception as e:
        logger.error("corel_capture_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draw/bezier")
async def draw_bezier(request: BezierPointsRequest):
    """
    Desenha uma curva Bezier no CorelDRAW.
    """
    try:
        service = container.get("corel_service")
        ai_interface = container.get("corel_ai_interface")
        
        if request.use_pixels:
            # Precisa de metadados para conversão
            if ai_interface.current_metadata is None:
                ai_interface.load_page_image()
            
            result = ai_interface.create_bezier_from_pixels(
                pixel_points=request.points,
                smooth=request.smooth,
                closed=request.closed,
                outline_color=request.outline_color,
                fill_color=request.fill_color
            )
        else:
            # Usa coordenadas de página diretamente
            points_tuple = [(p[0], p[1]) for p in request.points]
            
            if request.smooth:
                curve = service.create_smooth_bezier(points_tuple, closed=request.closed)
            else:
                curve = service.create_bezier_curve(points_tuple, closed=request.closed)
            
            service.set_curve_properties(
                curve,
                outline_color=tuple(request.outline_color) if request.outline_color else (0, 0, 0),
                fill_color=tuple(request.fill_color) if request.fill_color else None
            )
            
            result = {
                "status": "success",
                "points_count": len(request.points)
            }
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error("corel_bezier_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vectorize")
async def auto_vectorize(request: VectorizeRequest):
    """
    Vetoriza automaticamente a imagem atual da página.
    Detecta contornos e cria curvas Bezier.
    """
    try:
        ai_interface = container.get("corel_ai_interface")
        
        result = ai_interface.auto_vectorize(
            threshold=request.threshold,
            min_area=request.min_area,
            epsilon_factor=request.epsilon_factor
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error("corel_vectorize_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze")
async def analyze_page():
    """
    Analisa a página atual para a IA decidir estratégia de vetorização.
    """
    try:
        ai_interface = container.get("corel_ai_interface")
        result = ai_interface.get_image_analysis()
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error("corel_analyze_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_page():
    """
    Limpa todos os objetos da página atual.
    """
    try:
        ai_interface = container.get("corel_ai_interface")
        result = ai_interface.clear_and_reset()
        return result
    except Exception as e:
        logger.error("corel_clear_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_document(file_path: str):
    """
    Salva o documento atual.
    """
    try:
        service = container.get("corel_service")
        service.save_document(file_path)
        return {"status": "saved", "path": file_path}
    except Exception as e:
        logger.error("corel_save_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
