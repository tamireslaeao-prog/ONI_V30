from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from app.services.oni.hybrid_vision_service import HybridVisionService

router = APIRouter(prefix="/hybrid", tags=["hybrid-vision"])

class HybridAnalyzeResponse(BaseModel):
    url: str
    title: str
    element_count: int
    clickable_count: int
    editable_count: int
    scene_description: str
    elements: List[Dict[str, Any]]
    action_suggestion: str

@router.post("/analyze", response_model=HybridAnalyzeResponse)
async def analyze_url(
    url: str = Query(..., description="URL to analyze"),
    headless: bool = Query(True, description="Run browser in headless mode")
):
    """
    Perform Hybrid Vision analysis on a URL using local Selenium.
    Returns DOM + Accessibility Tree + visual context.
    """
    service = HybridVisionService(headless=headless)
    try:
        result = service.analyze(url)
        
        # Simplify response for API
        return HybridAnalyzeResponse(
            url=result.url,
            title=result.title,
            element_count=len(result.elements),
            clickable_count=len(result.clickable_elements),
            editable_count=len(result.editable_elements),
            scene_description=result.scene_description,
            elements=[asdict(e) for e in result.elements[:50]], # Limit output for API safety
            action_suggestion=f"Found {len(result.clickable_elements)} interactive elements. Use 'elements' list to interact."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()
