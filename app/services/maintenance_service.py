"""
ONI Maintenance Service
Handles automated cleanup and health checks.
Phase 4: Optimization (Memory Manager).
"""
import os
import time
import shutil
from pathlib import Path
from typing import List
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class MaintenanceService:
    """
    Background service for system hygiene.
    """
    
    def __init__(self):
        self.render_dir = Path("D:/RENDER")
        
    def run_maintenance(self) -> dict:
        """Run all maintenance tasks."""
        results = {
            "render_cleanup": self.cleanup_assets(
                self.render_dir, 
                max_age_hours=settings.memory.render_retention_hours
            )
        }
        logger.info("maintenance_completed", results=results)
        return results

    def cleanup_assets(self, directory: Path, max_age_hours: int) -> int:
        """
        Delete files older than max_age_hours in directory.
        Returns count of deleted files.
        """
        if not directory.exists():
            return 0
            
        deleted_count = 0
        now = time.time()
        cutoff = now - (max_age_hours * 3600)
        
        try:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    # Check modification time
                    if stat.st_mtime < cutoff:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            logger.warning("cleanup_failed_file", file=str(file_path), error=str(e))
                            
            if deleted_count > 0:
                logger.info("assets_cleaned", path=str(directory), count=deleted_count)
                
        except Exception as e:
            logger.error("cleanup_error", path=str(directory), error=str(e))
            
        return deleted_count
