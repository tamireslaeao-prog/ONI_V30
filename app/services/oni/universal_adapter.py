"""
ONI Universal Adapter Service v1.0
Sistema Universal de Adaptação para Qualquer Aplicativo.

Aprende e armazena atalhos de qualquer software Windows.
"""

import sqlite3
import time
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class ActionSource(str, Enum):
    """Origem do conhecimento do atalho."""
    BUILTIN = "builtin"      # Pré-configurado
    WEB_SEARCH = "web"       # Buscado na web
    LEARNED = "learned"      # Aprendido observando usuário
    INFERRED = "inferred"    # Inferido por padrões


@dataclass
class AppShortcut:
    """Representa um atalho de aplicativo."""
    process_name: str
    action_name: str
    hotkey: Optional[str] = None
    menu_path: Optional[str] = None  # Fallback: "File > Save"
    confidence: float = 1.0
    source: ActionSource = ActionSource.BUILTIN


class KnowledgeBase:
    """
    Base de conhecimento de atalhos por aplicativo.
    Armazena em SQLite para persistência.
    """
    
    DB_FILE = "oni_knowledge_base.db"
    
    # Atalhos universais que funcionam em quase todo app Windows
    UNIVERSAL_SHORTCUTS = {
        "new": "ctrl+n",
        "open": "ctrl+o",
        "save": "ctrl+s",
        "save_as": "ctrl+shift+s",
        "close": "ctrl+w",
        "quit": "alt+f4",
        "undo": "ctrl+z",
        "redo": "ctrl+y",
        "copy": "ctrl+c",
        "paste": "ctrl+v",
        "cut": "ctrl+x",
        "select_all": "ctrl+a",
        "find": "ctrl+f",
        "print": "ctrl+p",
    }
    
    # Atalhos específicos por app (built-in)
    APP_SHORTCUTS = {
        # Adobe Photoshop
        "Photoshop.exe": {
            "brush": "b",
            "eraser": "e",
            "rectangle": "u",
            "ellipse": "u",
            "line": "u",
            "text": "t",
            "move": "v",
            "zoom": "z",
            "fill": "g",
            "gradient": "g",
            "eyedropper": "i",
            "pen": "p",
            "selection": "m",
            "lasso": "l",
            "magic_wand": "w",
            "crop": "c",
        },
        # CorelDRAW
        "CorelDRW.exe": {
            "rectangle": "f6",
            "ellipse": "f7",
            "polygon": "y",
            "line": "f5",
            "bezier": "f5",
            "text": "f8",
            "pick": "space",
            "shape": "f10",
            "zoom": "z",
            "pan": "h",
            "fill": "f11",
            "outline": "f12",
        },
        # Adobe Illustrator
        "Illustrator.exe": {
            "rectangle": "m",
            "ellipse": "l",
            "line": "\\",
            "pen": "p",
            "text": "t",
            "selection": "v",
            "direct_selection": "a",
            "brush": "b",
            "pencil": "n",
            "eyedropper": "i",
        },
        # Microsoft Word
        "WINWORD.EXE": {
            "bold": "ctrl+b",
            "italic": "ctrl+i",
            "underline": "ctrl+u",
            "font": "ctrl+d",
            "align_left": "ctrl+l",
            "align_center": "ctrl+e",
            "align_right": "ctrl+r",
            "justify": "ctrl+j",
        },
        # Microsoft Excel
        "EXCEL.EXE": {
            "new_sheet": "shift+f11",
            "format_cells": "ctrl+1",
            "autosum": "alt+=",
            "insert_row": "ctrl++",
            "delete_row": "ctrl+-",
            "bold": "ctrl+b",
        },
        # Visual Studio Code
        "Code.exe": {
            "command_palette": "ctrl+shift+p",
            "quick_open": "ctrl+p",
            "terminal": "ctrl+`",
            "sidebar": "ctrl+b",
            "split": "ctrl+\\",
            "comment": "ctrl+/",
        },
        # Notepad
        "notepad.exe": {
            "goto": "ctrl+g",
            "time_date": "f5",
            "word_wrap": "alt+v,w",
        },
        # After Effects
        "AfterFX.exe": {
            "new_composition": "ctrl+n",
            "new_solid": "ctrl+y",
            "import": "ctrl+i",
            "ram_preview": "0",
            "play": "space",
        },
    }
    
    def __init__(self):
        self._init_db()
        self._load_builtins()
    
    def _init_db(self):
        """Inicializa o banco de dados."""
        try:
            conn = sqlite3.connect(self.DB_FILE)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS app_shortcuts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_name TEXT NOT NULL,
                    action_name TEXT NOT NULL,
                    hotkey TEXT,
                    menu_path TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'builtin',
                    created_at REAL,
                    verified_at REAL,
                    UNIQUE(process_name, action_name)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_synonyms (
                    action_name TEXT NOT NULL,
                    synonym TEXT NOT NULL,
                    UNIQUE(action_name, synonym)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_shortcuts_app ON app_shortcuts(process_name)")
            conn.commit()
            conn.close()
            logger.info("knowledge_base_initialized")
        except Exception as e:
            logger.error("knowledge_base_init_failed", error=str(e))
    
    def _load_builtins(self):
        """Carrega atalhos built-in no banco."""
        try:
            conn = sqlite3.connect(self.DB_FILE)
            now = time.time()
            
            # Universal shortcuts para todos os apps
            for action, hotkey in self.UNIVERSAL_SHORTCUTS.items():
                conn.execute("""
                    INSERT OR IGNORE INTO app_shortcuts 
                    (process_name, action_name, hotkey, confidence, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, ("*", action, hotkey, 1.0, "builtin", now))
            
            # App-specific shortcuts
            for app, shortcuts in self.APP_SHORTCUTS.items():
                for action, hotkey in shortcuts.items():
                    conn.execute("""
                        INSERT OR IGNORE INTO app_shortcuts 
                        (process_name, action_name, hotkey, confidence, source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (app, action, hotkey, 1.0, "builtin", now))
            
            conn.commit()
            conn.close()
            logger.info("builtins_loaded", apps=len(self.APP_SHORTCUTS))
        except Exception as e:
            logger.error("builtins_load_failed", error=str(e))
    
    def get_shortcut(self, process_name: str, action: str) -> Optional[AppShortcut]:
        """
        Busca atalho para uma ação em um app específico.
        Fallback para atalhos universais se não encontrar.
        """
        try:
            conn = sqlite3.connect(self.DB_FILE)
            conn.row_factory = sqlite3.Row
            
            # 1. Buscar específico do app
            cursor = conn.execute("""
                SELECT * FROM app_shortcuts 
                WHERE process_name = ? AND action_name = ?
            """, (process_name, action))
            row = cursor.fetchone()
            
            # 2. Fallback para universal
            if not row:
                cursor = conn.execute("""
                    SELECT * FROM app_shortcuts 
                    WHERE process_name = '*' AND action_name = ?
                """, (action,))
                row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return AppShortcut(
                    process_name=row["process_name"],
                    action_name=row["action_name"],
                    hotkey=row["hotkey"],
                    menu_path=row["menu_path"],
                    confidence=row["confidence"],
                    source=ActionSource(row["source"])
                )
            return None
            
        except Exception as e:
            logger.error("get_shortcut_failed", error=str(e))
            return None
    
    def store_shortcut(self, shortcut: AppShortcut):
        """Armazena um novo atalho aprendido."""
        try:
            conn = sqlite3.connect(self.DB_FILE)
            conn.execute("""
                INSERT OR REPLACE INTO app_shortcuts 
                (process_name, action_name, hotkey, menu_path, confidence, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                shortcut.process_name,
                shortcut.action_name,
                shortcut.hotkey,
                shortcut.menu_path,
                shortcut.confidence,
                shortcut.source.value,
                time.time()
            ))
            conn.commit()
            conn.close()
            logger.info("shortcut_stored", app=shortcut.process_name, action=shortcut.action_name)
        except Exception as e:
            logger.error("store_shortcut_failed", error=str(e))
    
    def list_app_shortcuts(self, process_name: str) -> List[AppShortcut]:
        """Lista todos os atalhos conhecidos de um app."""
        try:
            conn = sqlite3.connect(self.DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM app_shortcuts 
                WHERE process_name = ? OR process_name = '*'
                ORDER BY source
            """, (process_name,))
            
            shortcuts = []
            for row in cursor:
                shortcuts.append(AppShortcut(
                    process_name=row["process_name"],
                    action_name=row["action_name"],
                    hotkey=row["hotkey"],
                    menu_path=row["menu_path"],
                    confidence=row["confidence"],
                    source=ActionSource(row["source"])
                ))
            
            conn.close()
            return shortcuts
        except Exception as e:
            logger.error("list_shortcuts_failed", error=str(e))
            return []
    
    def list_supported_apps(self) -> List[str]:
        """Lista apps com atalhos conhecidos."""
        try:
            conn = sqlite3.connect(self.DB_FILE)
            cursor = conn.execute("""
                SELECT DISTINCT process_name FROM app_shortcuts 
                WHERE process_name != '*'
            """)
            apps = [row[0] for row in cursor]
            conn.close()
            return apps
        except Exception as e:
            return []


class UniversalAdapterService:
    """
    Serviço principal de adaptação universal.
    Resolve atalhos para qualquer aplicativo.
    """
    
    _knowledge_base: KnowledgeBase = None
    
    @classmethod
    def _get_kb(cls) -> KnowledgeBase:
        if cls._knowledge_base is None:
            cls._knowledge_base = KnowledgeBase()
        return cls._knowledge_base
    
    @classmethod
    async def resolve_action(
        cls, 
        process_name: str, 
        action: str
    ) -> Optional[AppShortcut]:
        """
        Resolve uma ação para um atalho específico do app.
        
        Args:
            process_name: Nome do processo (ex: "Photoshop.exe")
            action: Nome da ação (ex: "new", "brush", "save")
        
        Returns:
            AppShortcut ou None se não encontrar
        """
        kb = cls._get_kb()
        
        # 1. Buscar no knowledge base
        shortcut = kb.get_shortcut(process_name, action)
        
        if shortcut:
            logger.info("shortcut_resolved", 
                       app=process_name, 
                       action=action, 
                       hotkey=shortcut.hotkey,
                       source=shortcut.source.value)
            return shortcut
        
        # 2. Buscar na web se não encontrar
        shortcut = await cls._web_search_shortcut(process_name, action)
        if shortcut:
            # Armazenar para uso futuro
            kb.store_shortcut(shortcut)
            logger.info("shortcut_learned_from_web",
                       app=process_name,
                       action=action,
                       hotkey=shortcut.hotkey)
            return shortcut
        
        logger.warning("shortcut_not_found", app=process_name, action=action)
        return None
    
    @classmethod
    async def _web_search_shortcut(
        cls,
        process_name: str,
        action: str
    ) -> Optional[AppShortcut]:
        """
        Busca atalho na web quando não existe no knowledge base.
        Usa conhecimento embutido de padrões comuns.
        """
        import re
        import aiohttp
        
        # Mapear nome do processo para nome amigável
        app_name = cls._get_friendly_name(process_name)
        
        logger.info("web_search_starting", app=app_name, action=action)
        
        # Tentar buscar via conhecimento de padrões comuns
        # Muitos apps seguem convenções similares
        hotkey = cls._infer_from_patterns(app_name, action)
        
        if hotkey:
            return AppShortcut(
                process_name=process_name,
                action_name=action,
                hotkey=hotkey,
                confidence=0.7,
                source=ActionSource.INFERRED
            )
        
        # TODO: Integração futura com Bing/Google Custom Search API
        # Atualmente, o sistema confia na inferência por padrões ou aprendizado via usuário
        # Se chegar aqui, retornamos None para que o agente pergunte ao usuário ou tente outro método
        
        return None
    
    @classmethod
    def _get_friendly_name(cls, process_name: str) -> str:
        """Converte nome de processo para nome amigável."""
        name_map = {
            "Photoshop.exe": "Photoshop",
            "CorelDRW.exe": "CorelDRAW",
            "Illustrator.exe": "Illustrator",
            "WINWORD.EXE": "Word",
            "EXCEL.EXE": "Excel",
            "Code.exe": "VS Code",
            "AfterFX.exe": "After Effects",
            "chrome.exe": "Chrome",
            "firefox.exe": "Firefox",
            "GIMP-2.10.exe": "GIMP",
            "inkscape.exe": "Inkscape",
            "blender.exe": "Blender",
            "figma.exe": "Figma",
        }
        return name_map.get(process_name, process_name.replace(".exe", ""))
    
    @classmethod
    def _infer_from_patterns(cls, app_name: str, action: str) -> Optional[str]:
        """
        Infere atalho baseado em padrões comuns entre apps.
        """
        # Padrões universais que a maioria dos apps segue
        universal_patterns = {
            # Arquivo
            "new": "ctrl+n", "novo": "ctrl+n",
            "open": "ctrl+o", "abrir": "ctrl+o",
            "save": "ctrl+s", "salvar": "ctrl+s",
            "save_as": "ctrl+shift+s", "salvar_como": "ctrl+shift+s",
            "close": "ctrl+w", "fechar": "ctrl+w",
            "quit": "alt+f4", "sair": "alt+f4",
            "print": "ctrl+p", "imprimir": "ctrl+p",
            
            # Edição
            "undo": "ctrl+z", "desfazer": "ctrl+z",
            "redo": "ctrl+y", "refazer": "ctrl+y",
            "copy": "ctrl+c", "copiar": "ctrl+c",
            "paste": "ctrl+v", "colar": "ctrl+v",
            "cut": "ctrl+x", "recortar": "ctrl+x",
            "select_all": "ctrl+a", "selecionar_tudo": "ctrl+a",
            "find": "ctrl+f", "buscar": "ctrl+f",
            "replace": "ctrl+h", "substituir": "ctrl+h",
            "delete": "delete", "deletar": "delete",
            
            # Formatação (apps de texto/design)
            "bold": "ctrl+b", "negrito": "ctrl+b",
            "italic": "ctrl+i", "italico": "ctrl+i",
            "underline": "ctrl+u", "sublinhado": "ctrl+u",
            
            # Navegação
            "zoom_in": "ctrl++", "aumentar_zoom": "ctrl++",
            "zoom_out": "ctrl+-", "diminuir_zoom": "ctrl+-",
            "zoom_fit": "ctrl+0", "ajustar_zoom": "ctrl+0",
            "fullscreen": "f11", "tela_cheia": "f11",
        }
        
        # Apps de design geralmente usam letra única para ferramentas
        design_apps = ["photoshop", "illustrator", "gimp", "inkscape", "figma", "sketch"]
        if any(app.lower() in app_name.lower() for app in design_apps):
            tool_patterns = {
                "brush": "b", "pincel": "b",
                "eraser": "e", "borracha": "e",
                "pen": "p", "caneta": "p",
                "text": "t", "texto": "t",
                "move": "v", "mover": "v",
                "selection": "m", "selecao": "m",
                "zoom": "z",
                "hand": "h", "mao": "h",
                "eyedropper": "i", "conta_gotas": "i",
                "gradient": "g", "gradiente": "g",
                "crop": "c", "recorte": "c",
                "lasso": "l", "laco": "l",
            }
            if action.lower() in tool_patterns:
                return tool_patterns[action.lower()]
        
        # Buscar em padrões universais
        action_lower = action.lower().replace(" ", "_").replace("-", "_")
        if action_lower in universal_patterns:
            return universal_patterns[action_lower]
        
        return None
    
    @classmethod
    async def execute_action(
        cls,
        process_name: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Resolve e executa uma ação com verificação visual obrigatória.
        """
        import pyautogui
        import asyncio
        from app.services.oni.desktop_hybrid_service import desktop_vision_v2
        
        shortcut = await cls.resolve_action(process_name, action)
        
        if not shortcut or not shortcut.hotkey:
            return {
                "success": False,
                "error": f"No shortcut found for '{action}' in {process_name}"
            }
        
        try:
            # 1. PRE-ACTION SCAN (MANDATORY)
            logger.info("adapter_pre_action_scan")
            pre_scan = await desktop_vision_v2.scan_active_window()
            
            # Parsear hotkey (ex: "ctrl+n" -> ["ctrl", "n"])
            keys = shortcut.hotkey.lower().split("+")
            pyautogui.hotkey(*keys)
            
            # 2. POST-ACTION SCAN (MANDATORY)
            await asyncio.sleep(0.5)
            post_scan = await desktop_vision_v2.scan_active_window()
            
            return {
                "success": True,
                "action": action,
                "hotkey": shortcut.hotkey,
                "source": shortcut.source.value,
                "verification_pre": pre_scan.to_dict(),
                "verification_post": post_scan.to_dict()
            }
        except Exception as e:
            logger.error("execute_action_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    @classmethod
    def list_apps(cls) -> List[str]:
        """Lista apps suportados."""
        return cls._get_kb().list_supported_apps()
    
    @classmethod
    def list_actions(cls, process_name: str) -> List[Dict]:
        """Lista ações disponíveis para um app."""
        shortcuts = cls._get_kb().list_app_shortcuts(process_name)
        return [
            {"action": s.action_name, "hotkey": s.hotkey, "source": s.source.value}
            for s in shortcuts
        ]
    
    @classmethod
    def learn_shortcut(
        cls,
        process_name: str,
        action: str,
        hotkey: str,
        source: ActionSource = ActionSource.LEARNED
    ):
        """Ensina um novo atalho ao sistema."""
        shortcut = AppShortcut(
            process_name=process_name,
            action_name=action,
            hotkey=hotkey,
            confidence=0.8,  # Learned tem confiança menor
            source=source
        )
        cls._get_kb().store_shortcut(shortcut)
        logger.info("shortcut_learned", app=process_name, action=action, hotkey=hotkey)
