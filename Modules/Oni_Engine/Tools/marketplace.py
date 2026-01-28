"""
Skill Marketplace - NPM para automações ONI (Tier 2 Feature)
Permite instalar, gerenciar e executar skills compartilhadas.
"""

import requests
import json
import importlib.util
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Setup logging
logger = logging.getLogger("SkillMarketplace")

@dataclass
class Skill:
    """Representa uma skill instalável"""
    name: str
    version: str
    description: str
    author: str
    rating: float
    downloads: int
    dependencies: List[str]
    code_url: str

class SkillMarketplace:
    """
    Marketplace de skills ONI.
    Gerencia download, instalação e execução de módulos de automação.
    """
    
    def __init__(self, marketplace_url: str = "https://oni-skills.io/api", skills_dir: str = "oni_skills"):
        self.marketplace_url = marketplace_url
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Registry local
        self.installed_skills: Dict[str, Skill] = {}
        self._load_installed()
    
    def search(self, query: str) -> List[Skill]:
        """
        Busca skills no marketplace.
        Nota: Atualmente usa dados mockados pois a API real ainda não existe.
        """
        logger.info(f"Searching for skills with query: '{query}'")
        
        # Mock Response for prototype
        mock_db = [
            Skill("excel-pivot", "1.0.0", "Auto pivot tables", "oni-team", 4.8, 1500, [], "http://mock/code/excel-pivot"),
            Skill("gmail-send", "2.1.0", "Send emails via Gmail API", "google-fan", 4.5, 8000, [], "http://mock/code/gmail-send"),
            Skill("photoshop-remove-bg", "0.9.beta", "Remove background", "artist-bot", 4.9, 300, [], "http://mock/code/ps-bg")
        ]
        
        results = [s for s in mock_db if query.lower() in s.name.lower() or query.lower() in s.description.lower()]
        return results

    def install(self, skill_name: str, version: str = "latest") -> bool:
        """
        Instala uma skill (Simulado).
        Na versão real, faria download do .py e salvaria em oni_skills/.
        """
        logger.info(f"📦 Installing {skill_name}@{version}...")
        
        # Mock installation logic
        # In real world: fetch metadata -> download code -> resolve deps
        
        # Check if already installed
        if skill_name in self.installed_skills:
            logger.info(f"Skill {skill_name} is already installed.")
            return True
        
        # Simulate successful download
        skill_file = self.skills_dir / f"{skill_name}.py"
        
        if skill_name == "excel-pivot":
            code = """
def main(**kwargs):
    print("Creating Pivot Table in Excel...")
    return "Pivot Table Created"
"""
        elif skill_name == "gmail-send":
            code = """
def main(to, subject, body):
    print(f"Sending email to {to}: {subject}")
    return "Email Sent"
"""
        else:
            code = f"""
def main(**kwargs):
    print("Executing generic skill {skill_name}")
    return "Success"
"""
        
        try:
            with open(skill_file, "w") as f:
                f.write(code.strip())
            
            # Register
            new_skill = Skill(skill_name, "1.0.0", "Installed via ONI", "Unknown", 5.0, 0, [], "local")
            self.installed_skills[skill_name] = new_skill
            self._save_installed()
            
            logger.info(f"✓ Installed: {skill_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Installation failed: {e}")
            return False

    def uninstall(self, skill_name: str) -> bool:
        """Remove uma skill"""
        if skill_name not in self.installed_skills:
            logger.warning(f"⚠️ Skill '{skill_name}' not installed")
            return False
        
        skill_file = self.skills_dir / f"{skill_name}.py"
        if skill_file.exists():
            skill_file.unlink()
        
        del self.installed_skills[skill_name]
        self._save_installed()
        
        logger.info(f"✓ Uninstalled: {skill_name}")
        return True
    
    def list_installed(self) -> List[Skill]:
        """Lista skills instaladas"""
        return list(self.installed_skills.values())
    
    def execute_skill(self, skill_name: str, **kwargs) -> any:
        """
        Executa uma skill instalada carregando-a dinamicamente.
        """
        if skill_name not in self.installed_skills:
            # Try to auto-install?
            logger.info(f"Skill {skill_name} not found. Attempting auto-install...")
            if not self.install(skill_name):
                return f"Error: Skill {skill_name} not found and failed to install."
        
        skill_file = self.skills_dir / f"{skill_name}.py"
        if not skill_file.exists():
             return f"Error: Skill file for {skill_name} missing."

        try:
            # Import module dynamically
            spec = importlib.util.spec_from_file_location(skill_name, skill_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Execute main()
            if hasattr(module, 'main'):
                return module.main(**kwargs)
            else:
                return f"Error: Skill {skill_name} has no main() function"
        except Exception as e:
            return f"Error executing skill: {e}"

    def _save_installed(self):
        registry_file = self.skills_dir / "registry.json"
        data = {name: s.__dict__ for name, s in self.installed_skills.items()}
        with open(registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_installed(self):
        registry_file = self.skills_dir / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    self.installed_skills = {name: Skill(**d) for name, d in data.items()}
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")

# CLI Utility
def oni_cli():
    import sys
    marketplace = SkillMarketplace()
    
    if len(sys.argv) < 2:
        print("Usage: oni [command] [args]")
        return
        
    cmd = sys.argv[1]
    if cmd == "search":
        print(marketplace.search(sys.argv[2] if len(sys.argv)>2 else ""))
    elif cmd == "install":
        marketplace.install(sys.argv[2])
    elif cmd == "list":
        for s in marketplace.list_installed(): print(s.name)
    elif cmd == "execute":
        print(marketplace.execute_skill(sys.argv[2]))

if __name__ == "__main__":
    oni_cli()
