"""
ONI v12.0 - Skill Registry
Central repository for managing capabilities (Skills).
Supports both passive knowledge (guides) and active capabilities (workflows).
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
import zipfile
import shutil

logger = structlog.get_logger()

@dataclass
class SkillManifest:
    """Metadata for a skill."""
    name: str
    version: str
    description: str
    category: str
    author: str = "Unknown"
    dependencies: List[str] = field(default_factory=list)

@dataclass
class Skill:
    """A registered skill (capability)."""
    manifest: SkillManifest
    data: Dict[str, Any]  # The raw content (knowledge base or config)
    path: Path

class SkillRegistry:
    """
    Manages the lifecycle, discovery, and retrieval of skills.
    """
    
    def __init__(self, skill_dir: str = "app/skills"):
        self.skill_dir = Path(skill_dir)
        self.skills: Dict[str, Skill] = {}
        self._load_builtins()
        
    def _load_builtins(self):
        """Load skills from the skill directory."""
        if not self.skill_dir.exists():
            logger.warning("skill_dir_not_found", path=self.skill_dir)
            return

        for file_path in self.skill_dir.glob("*.json"):
            try:
                self._load_skill_file(file_path)
            except Exception as e:
                logger.error("failed_to_load_skill", file=file_path.name, error=str(e))

    def _load_skill_file(self, path: Path):
        """Load a single skill JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Basic inference of manifest from JSON
        # If specific manifest fields missing, use defaults
        manifest = SkillManifest(
            name=data.get("software", path.stem).lower().replace(" ", "_"),
            version=data.get("version", "1.0"),
            description=data.get("description", "No description provided"),
            category=data.get("category", "general"),
            author=data.get("author", "System")
        )
        
        skill = Skill(manifest=manifest, data=data, path=path)
        self.register(skill)

    def register(self, skill: Skill):
        """Register a skill."""
        if skill.manifest.name in self.skills:
            logger.warning("overwriting_skill", name=skill.manifest.name)
        
        self.skills[skill.manifest.name] = skill
        logger.info("skill_registered", name=skill.manifest.name, category=skill.manifest.category)

    def get_skill(self, name: str) -> Optional[Skill]:
        """Retrieve a skill by name."""
        return self.skills.get(name)

    def list_skills(self) -> List[SkillManifest]:
        """List all registered skills."""
        return [s.manifest for s in self.skills.values()]

    def search_skills(self, query: str) -> List[SkillManifest]:
        """Search skills by name or description."""
        query = query.lower()
        results = []
        for skill in self.skills.values():
            if (query in skill.manifest.name.lower() or 
                query in skill.manifest.description.lower()):
                results.append(skill.manifest)
        return results

    def export_skill(self, name: str, output_path: str) -> bool:
        """
        Export a skill to a .oni-skill (zip) file.
        """
        skill = self.get_skill(name)
        if not skill:
            logger.error("skill_not_found_for_export", name=name)
            return False
            
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add the main JSON file
                zf.write(skill.path, arcname=skill.path.name)
                # TODO: Add associated assets if we standardise folder structure
            logger.info("skill_exported", name=name, path=output_path)
            return True
        except Exception as e:
            logger.error("skill_export_failed", error=str(e))
            return False

    def import_skill(self, input_path: str) -> bool:
        """
        Import a skill from a .oni-skill (zip) file.
        """
        try:
            with zipfile.ZipFile(input_path, 'r') as zf:
                # Security check: only allow json/png files, no executable code for now
                for file in zf.namelist():
                    if not (file.endswith('.json') or file.endswith('.png')):
                        logger.warning("skipping_unsafe_file", file=file)
                        continue
                    zf.extract(file, self.skill_dir)
            
            # Reload to pick up new skill
            self._load_builtins()
            logger.info("skill_imported", path=input_path)
            return True
        except Exception as e:
            logger.error("skill_import_failed", error=str(e))
            return False

# Global registry instance
registry = SkillRegistry()
