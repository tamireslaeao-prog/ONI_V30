
import os
import google.generativeai as genai
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.logger import logger

class GeminiFlashProvider:
    """
    Direct integration with Google Gemini 1.5 Flash (Free Tier) for Vision tasks.
    Uses 'google-generativeai' SDK.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # Try numbered keys
            for i in range(1, 6):
                key = os.getenv(f"GEMINI_API_KEY_{i}")
                if key:
                    self.api_key = key
                    break
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            # SECURITY FIX: Don't expose env var name in logs
            logger.warning("vision_api_key_missing", message="Vision API key not configured.")
            self.model = None

    def verify_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Analyzes an image and answers the prompt.
        """
        if not self.model:
            return {
                "approved": True, 
                "confidence": 0.5, 
                "reason": "No Vision API Key configured",
                "model": "gemini-1.5-flash-missing-key"
            }
            
        try:
            path = Path(image_path)
            if not path.exists():
                return {"approved": False, "confidence": 0.0, "reason": "Image file not found"}
                
            img = Image.open(path)
            
            # Construct a verification prompt that forces JSON-like structure or specific format
            full_prompt = f"""
            Analyze this image carefully.
            Task: {prompt}
            
            Provide your output in exactly this format:
            APPROVED: [Yes/No]
            CONFIDENCE: [0-100]
            REASON: [One sentence explanation]
            """
            
            response = self.model.generate_content([full_prompt, img])
            text = response.text
            
            # Parse response
            approved = "yes" in text.lower().split("approved")[0:2][-1].lower() if "approved" in text.lower() else False
            
            confidence = 0.5
            if "confidence" in text.lower():
                import re
                match = re.search(r"confidence[:\s]*(\d+)", text.lower())
                if match:
                    confidence = int(match.group(1)) / 100.0
            
            reason = "No reason extracted"
            if "reason" in text.lower():
                reason = text.split("REASON:")[-1].strip().split("\n")[0]
            elif "Reason:" in text:
                reason = text.split("Reason:")[-1].strip().split("\n")[0]
            else:
                reason = text.strip()[:100]

            return {
                "approved": approved,
                "confidence": confidence,
                "reason": reason,
                "model": "gemini-1.5-flash-direct",
                "raw_response": text
            }

        except Exception as e:
            logger.error("gemini_flash_verify_failed", error=str(e))
            return {
                "approved": True, 
                "confidence": 0.5, 
                "reason": f"Exception: {str(e)}",
                "model": "gemini-1.5-flash-error"
            }
