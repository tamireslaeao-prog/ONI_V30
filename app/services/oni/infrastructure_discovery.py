"""
ONI Infrastructure Discovery
Descobre automaticamente a infraestrutura do sistema.
"""

class InfrastructureDiscovery:
    """
    Descobre automaticamente a infraestrutura disponível.
    Resolve o problema de não usar bridges/adapters existentes.
    
    ATUALIZADO COM ANÁLISE COMPLETA DO WORKSPACE.
    """
    
    CACHE_FILE = "temp/infrastructure_cache.json"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BRIDGES NA PASTA Modules/ (DESCOBERTOS 2026-01-14)
    # ═══════════════════════════════════════════════════════════════════════════
    MODULES_BRIDGES = {
        # After Effects
        "after_effects": {
            "path": "Modules/AfterEffects/ONI_AfterEffects_Bridge.py",
            "alt_path": "Modules/AfterEffects/oni_ae_bridge.py",
            "type": "python",
            "capabilities": ["jsx_injection", "render", "composition"]
        },
        # AutoCAD
        "autocad": {
            "path": "Modules/AutoCAD/ONI_AutoCAD_Bridge.py",
            "type": "python",
            "capabilities": ["activex", "draw", "dimension", "export_dxf"]
        },
        "autocad_setup": {
            "path": "Modules/AutoCAD/Setup/Install-AutoCADShortcuts.ps1",
            "type": "powershell",
            "capabilities": ["pgp_injection", "alias_setup"]
        },
        # Blender (COM VRAY!)
        "blender": {
            "path": "Modules/Blender/ONI_Blender_Bridge.py",
            "type": "python",
            "capabilities": ["headless", "render", "procedural", "animation"]
        },
        "blender_vray": {
            "path": "Modules/Blender/ONI_VRay_Blender.py",
            "type": "python",
            "capabilities": ["vray_render", "gi", "light_cache", "caustics"]
        },
        # Chrome
        "chrome": {
            "path": "Modules/Chrome/",  # Múltiplos arquivos
            "type": "python",
            "capabilities": ["selenium", "web_automation", "scraping"]
        },
        # Corel
        "corel": {
            "path": "Modules/Corel/ONI_Corel_Bridge.py",
            "type": "python",
            "capabilities": ["com", "vector", "bezier", "export"]
        },
        "corel_designer": {
            "path": "Modules/Corel/Scripts/ONI_Corel_Designer.py",
            "type": "python",
            "capabilities": ["vectorize", "outline", "fit_page", "smart_group"]
        },
        "corel_clipboard": {
            "path": "Modules/Corel/Scripts/ONI_Clipboard_Bridge.py",
            "type": "python",
            "capabilities": ["pdf_injection", "ai_interop", "clipboard_bridge"]
        },
        # Corel Scripts (Automation) - From Master Reference
        "corel_scripts": {
            "path": "Modules/Corel/Scripts/",
            "type": "powershell",
            "scripts": {
                "focus": "force_focus.ps1",
                "import": "import_logo.ps1",
                "trace": "manual_trace_helper.ps1"
            },
            "capabilities": ["force_focus", "logo_injection", "manual_trace_assist"]
        },
        # Edge
        "edge": {
            "path": "Modules/Edge/",
            "type": "python",
            "capabilities": ["browser_automation"]
        },
        # Excel
        "excel": {
            "path": "Modules/Excel/ONI_Excel.py",
            "type": "python",
            "capabilities": ["com", "formulas", "charts", "data"]
        },
        # Foxit PDF
        "foxit": {
            "path": "Modules/Foxit/ONI_Foxit_Bridge.py",
            "alt_path": "Modules/Foxit/ONI_Foxit_Adapter.py",
            "type": "python",
            "capabilities": ["pdf_edit", "merge", "ocr", "forms", "signature"]
        },
        # Illustrator
        "illustrator": {
            "path": "Modules/Illustrator/ONI_Illustrator_Bridge.py",
            "type": "python",
            "capabilities": ["jsx", "vector", "svg", "eps"]
        },
        # Maya (COM VRAY!)
        "maya": {
            "path": "Modules/Maya/ONI_Maya_Bridge.py",
            "type": "python",
            "capabilities": ["mel", "vray", "render", "animation", "3d"]
        },
        # Photoshop
        "photoshop": {
            "path": "Modules/Photoshop/",
            "type": "python+jsx",
            "capabilities": ["jsx", "com", "styles", "effects", "psd"]
        },
        # Word
        "word": {
            "path": "Modules/Word/",
            "type": "python",
            "capabilities": ["com", "document", "docx"]
        },
        # Windows
        "windows": {
            "path": "Modules/Windows/",
            "type": "python",
            "capabilities": ["registry", "services", "explorer"]
        },
        # Asana (Task Management)
        "asana": {
            "path": "Modules/Asana/ONI.Asana.js",
            "type": "javascript",
            "capabilities": ["task_management", "project_sync", "automation"]
        },
        # Core (System Tools)
        "core": {
            "path": "Modules/Core/",
            "type": "mixed",
            "files": ["ONI_Master_Harvester.ps1", "oni_app_finder.py"],
            "capabilities": ["app_discovery", "process_harvesting", "system_scan"]
        },
        # Security (Sentinel)
        "security": {
            "path": "Modules/Security/ONI_Universal_Sentinel.ps1",
            "type": "powershell",
            "capabilities": ["monitoring", "protection", "watchdog"]
        },
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BRIDGES NA PASTA app/scripts/ (ADAPTERS POWERSHELL)
    # ═══════════════════════════════════════════════════════════════════════════
    APP_SCRIPTS_BRIDGES = {
        "blender_script": "Modules/Blender/ONI_Blender_Bridge.py",
        "chrome_script": "Modules/Oni_Engine/Scripts/ONI_Chrome_Bridge.py",
        "autocad_script": "Modules/AutoCAD/ONI_AutoCAD_Bridge.py",
        "photoshop_ps": "Modules/Core/Scripts/Photoshop_Adapter.psm1",
        "corel_ps": "Modules/Corel/Scripts/Corel_Adapter.psm1",
        "after_effects_ps": "Modules/Core/Scripts/AfterEffects_Adapter.psm1",
        "office_ps": "Modules/Core/Scripts/Office_Adapter.psm1",
        "windows_ps": "Modules/Core/Scripts/Windows_Adapter.psm1",
        "autocad_activex": "Modules/AutoCAD/Scripts/AutoCAD_Adapter.psm1",
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # APP SERVICES (app/services/) - Serviços de Alto Nível
    # ═══════════════════════════════════════════════════════════════════════════
    APP_SERVICES = {
        "deep_reasoning": {
            "path": "app/services/deep_reasoning.py",
            "size": "36KB",
            "capabilities": ["reasoning", "analysis", "decision_making"]
        },
        # Photoshop Hunter Protocol (Master Reference)
        "composer_service": {
            "path": "app/services/photoshop/composer_service.py",
            "type": "python",
            "capabilities": ["hunter_protocol", "photoshop_composer", "text_replacement"],
            "status": "CRITICAL_CORE"
        },
        "shape_executor": {
            "path": "app/services/shape_executor.py",
            "size": "32KB",
            "capabilities": ["shape_generation", "svg", "vector_drawing"]
        },
        "onihand_service": {
            "path": "app/services/onihand_service.py",
            "size": "18KB",
            "capabilities": ["hand_tracking", "gesture_control"]
        },
        "web_reasoning": {
            "path": "app/services/web_reasoning.py",
            "size": "16KB",
            "capabilities": ["web_analysis", "page_understanding"]
        },
        "canvas_bounds": {
            "path": "app/services/canvas_bounds.py",
            "size": "12KB",
            "capabilities": ["canvas_detection", "bounds_calculation"]
        },
        "quality_verification": {
            "path": "app/services/quality_verification.py",
            "size": "10KB",
            "capabilities": ["quality_check", "verification"]
        },
        "omniparser": {
            "path": "app/services/omniparser_service.py",
            "size": "11KB",
            "capabilities": ["ui_parsing", "element_detection"]
        },
        "inference_engine": {
            "path": "app/services/inference_engine.py",
            "size": "8KB",
            "capabilities": ["inference", "prediction"]
        },
        "neural_hand": {
            "path": "app/services/neural/neural_hand_service.py",
            "capabilities": ["neural_control", "hand_simulation"]
        },
        "vision_cache": {
            "path": "app/services/vision/vision_cache.py",
            "capabilities": ["screenshot_cache", "optimization"]
        },
        "gemini_flash": {
            "path": "app/services/vision/gemini_flash_provider.py",
            "capabilities": ["gemini_vision", "flash_inference"]
        },
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # APP TOOLS (app/tools/) - JSX Tools for Photoshop
    # ═══════════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════════
    # APP TOOLS (Modules/Photoshop/Tools/) - JSX Tools for Photoshop
    # ═══════════════════════════════════════════════════════════════════════════
    APP_TOOLS_JSX = {
        "style_extractor": {
            "path": "Modules/Photoshop/Tools/oni_style_extractor.jsx",
            "size": "26KB",
            "capabilities": ["style_extraction", "layer_styles"]
        },
        "style_applicator": {
            "path": "Modules/Photoshop/Tools/oni_style_applicator.jsx",
            "size": "17KB",
            "capabilities": ["style_application", "batch_apply"]
        },
        "diagnostic_tool": {
            "path": "Modules/Photoshop/Tools/oni_diagnostic_tool.jsx",
            "capabilities": ["diagnostics", "debugging"]
        },
        "deep_dump_fx": {
            "path": "Modules/Photoshop/Tools/deep_dump_fx.jsx",
            "capabilities": ["fx_extraction", "effect_dump"]
        },
        "extract_layer_styles": {
            "path": "Modules/Photoshop/Tools/extract_layer_styles.jsx",
            "capabilities": ["layer_style_export"]
        },
        "debug_layers": {
            "path": "Modules/Photoshop/Tools/oni_debug_layers.jsx",
            "capabilities": ["layer_debugging"]
        },
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # APP LIB (app/lib/) - Core Libraries
    # ═══════════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════════
    # APP LIB (Modules/Oni_Engine/Lib/) - Core Libraries
    # ═══════════════════════════════════════════════════════════════════════════
    APP_LIB = {
        "oni_fx_core": {
            "path": "Modules/Oni_Engine/Lib/oni_fx_core.jsx",
            "size": "14KB",
            "capabilities": ["fx_engine", "effect_processing"]
        },
        "ae_lib": {
            "path": "Modules/Oni_Engine/Lib/", # Based on findings
            "capabilities": ["after_effects_helpers"]
        },
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ONI ENGINE (MÓDULOS CORE)
    # ═══════════════════════════════════════════════════════════════════════════
    ONI_ENGINE = {
        "audio_transcriber": "Modules/Oni_Engine/audio_transcriber.py",
        "ebook_generator": "Modules/Oni_Engine/ebook_generator.py",
        "oni_dsp": "Modules/Oni_Engine/oni_dsp.py",
        "video_brain": "Modules/Oni_Engine/oni_video_brain.py",
        "video_gen": "Modules/Oni_Engine/oni_video_gen.py",
        "video_vision": "Modules/Oni_Engine/video_vision.py",
        "composition_guard": "Modules/Oni_Engine/oni_composition_guard.py",
        "foxit_wrapper": "Modules/Oni_Engine/foxit/foxit_wrapper.py",
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SUPER CEREBRO (IA INTERNA)
    # ═══════════════════════════════════════════════════════════════════════════
    SUPER_CEREBRO = {
        "auto_learn": "Modules/Super_Cerebro/auto_learn.py",
        "brain_core": "Modules/Super_Cerebro/brain_core.py",
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONFIGURAÇÕES DO SISTEMA
    # ═══════════════════════════════════════════════════════════════════════════
    SYSTEM_CONFIG = {
        "server_port": 8000,
        "server_host": "localhost",
        "run_script": "run.bat",
        "run_python": "run.py",
        "stop_script": "stop.bat",
        "backup_script": "backup.bat",
        "clean_script": "clean.bat",
        "install_script": "install.bat",
        "env_file": ".env",
        "requirements": "requirements.txt",
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONFIG FILES (JSON SHORTCUTS) - From Master Reference
    # ═══════════════════════════════════════════════════════════════════════════
    CONFIG_FILES = {
        "ps_shortcuts": "Modules/Photoshop/Config/ps_shortcuts.json",
        "ai_shortcuts": "Modules/Illustrator/Config/ai_shortcuts.json",
        "corel_shortcuts": "Modules/Corel/Config/corel_shortcuts.json",
        "ae_shortcuts": "Modules/AfterEffects/Config/ae_shortcuts.json",
        "maya_shortcuts": "Modules/Maya/Config/maya_shortcuts.json",
        "blender_shortcuts": "Modules/Blender/Config/blender_shortcuts.json",
        "pr_shortcuts": "Modules/Premiere/Config/pr_shortcuts.json",
        "autocad_shortcuts": "Modules/AutoCAD/Config/autocad_shortcuts.json",
        "word_shortcuts": "Modules/Word/Config/word_shortcuts.json",
        "excel_shortcuts": "Modules/Excel/Config/excel_shortcuts.json",
        "foxit_shortcuts": "Modules/Foxit/Config/foxit_shortcuts.json"
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # PHYSICAL ASSETS (DRIVES) - From Master Reference
    # ═══════════════════════════════════════════════════════════════════════════
    PHYSICAL_ASSETS = {
        "design_drive": "D:\\DESIGN",
        "psd_sources": "D:\\DESIGN\\psd_sources",
        "atom_drive": "D:\\ATOM",
        "render_drive": "D:\\RENDER"
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # API KEYS DISPONÍVEIS (DO .env)
    # ═══════════════════════════════════════════════════════════════════════════
    API_KEYS_AVAILABLE = [
        "GEMINI_API_KEY",
        "OPENROUTER_API_KEY", 
        "HUGGINGFACE_API_KEY",
        "MISTRAL_API_KEY",
        "ZAI_API_KEY",
        "MIRIX_API_KEY",
        "UNSTRUCTURED_API_KEY", # Added commonly used key
        "BRAVE_API_KEY"         # Added commonly used key
    ]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MODELS DISPONÍVEIS
    # ═══════════════════════════════════════════════════════════════════════════
    MODELS = {
        "yolov8n": "models/yolov8n.pt",
        "mistral_local": "models/Mistral-7B-Instruct-v0.3-Q8_0.gguf",
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RECURSOS EXTERNOS (ATOM)
    # ═══════════════════════════════════════════════════════════════════════════
    EXTERNAL_ASSETS = {
        "atom_master_index": "ATOM_MASTER_INDEX.json",
        "atom_location": "D:\\ATOM",
    }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AGENT SYSTEMS (app/agent/) - Sistema de Agentes Autônomos
    # ═══════════════════════════════════════════════════════════════════════════
    AGENT_SYSTEMS = {
        "hybrid_agent": {
            "path": "app/agent/hybrid_agent.py",
            "size": "31KB",
            "capabilities": ["autonomous_execution", "goal_parsing", "reflection"]
        },
        "hybrid_worker": {
            "path": "app/agent/hybrid_worker.py",
            "size": "28KB",
            "capabilities": ["action_execution", "grounding", "screen_analysis"]
        },
        "routines": {
            "path": "app/agent/routines.py",
            "size": "43KB",
            "capabilities": ["windows_routines", "corel_routines", "photoshop_routines"],
            "count": 211
        },
    }

    @classmethod
    def discover_all(cls):
        """
        Faz varredura completa e descobre toda infraestrutura disponível.
        """
        import os
        
        discovery = {
            "bridges": cls.MODULES_BRIDGES,
            "adapters": cls.APP_SCRIPTS_BRIDGES,
            "services": cls.APP_SERVICES,
            "tools": cls.APP_TOOLS_JSX,
            "libs": cls.APP_LIB,
            "engine": cls.ONI_ENGINE,
            "brain": cls.SUPER_CEREBRO,
            "config": cls.SYSTEM_CONFIG,
            "files": cls.CONFIG_FILES,       # New
            "physical": cls.PHYSICAL_ASSETS, # New
            "keys": cls.API_KEYS_AVAILABLE,
            "models": cls.MODELS,
            "assets": cls.EXTERNAL_ASSETS,
            "agents": cls.AGENT_SYSTEMS
        }
        
        # Verificar existência física
        stats = {k: {"total": len(v), "found": 0} for k, v in discovery.items() if isinstance(v, dict)}
        
        for category, items in discovery.items():
            if not isinstance(items, dict): continue
            
            for key, info in items.items():
                path = info.get("path") if isinstance(info, dict) else info
                if path and os.path.exists(path):
                    stats[category]["found"] += 1
                    
        return {
            "discovery": discovery,
            "stats": stats
        }
