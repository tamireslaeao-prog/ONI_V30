import json
from pathlib import Path
import structlog

logger = structlog.get_logger()

def get_routines_loader():
    """
    Load automation routines from the centralized Modules knowledge base.
    Restored after V24.1 refactor.
    """
    try:
        # Resolve path to Modules/Core/Knowledge/advanced_automation_routines.json
        # app/infrastructure/knowledge/routines_loader.py -> ../../../Modules/...
        
        current_file = Path(__file__).resolve()
        # root is 3 levels up: knowledge -> infrastructure -> app -> ONIV24
        project_root = current_file.parent.parent.parent.parent
        
        json_path = project_root / "Modules" / "Core" / "Knowledge" / "advanced_automation_routines.json"
        
        if not json_path.exists():
            logger.warning(f"Routines JSON not found at {json_path}")
            return {}

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return data

    except Exception as e:
        logger.error(f"Failed to load routines: {e}")
        return {}
