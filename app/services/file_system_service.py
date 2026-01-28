from pathlib import Path
from typing import Optional, Any
import structlog
import os

from app.infrastructure.safety.flash_backup import backup_file

logger = structlog.get_logger()

class FileSystemService:
    """
    Soul-Compliant File System Access.
    Enforces Axiom 2 (Write-First) and integrates Flash Backup (Guardian Lite).
    """

    def __init__(self):
        logger.info("file_system_service_initialized")

    def write_text(self, path: str, content: str, encoding: str = "utf-8", overwrite: bool = False) -> bool:
        """
        Write text to file with automatic backup.
        """
        target = Path(path)
        
        # 1. TRIGGER FLASH BACKUP (Guardian Lite)
        if target.exists():
            if not overwrite:
                raise FileExistsError(f"File exists and overwrite=False: {path}")
            # Identify heuristic: only backup if file is > 0 bytes? 
            # No, always backup modifications.
            backup_file(str(target))
        
        # 2. Safety Check (Axiom 2 part b - Directory existence)
        target.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            target.write_text(content, encoding=encoding)
            logger.info("file_written", path=str(target))
            return True
        except Exception as e:
            logger.error("file_write_failed", path=str(target), error=str(e))
            raise e

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """Safe read."""
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return target.read_text(encoding=encoding)

    def ensure_empty_file(self, path: str) -> bool:
        """Creates an empty file if not exists (Protocol PWF)."""
        target = Path(path)
        if target.exists():
            return False
        
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
        return True
