"""
ONI V25 - MASTER REFERENCE & UNIVERSAL WORKFLOW
Version: 25.1 (Soul Binding Consolidado)
Date: 2026-01-22
Status: SISTEMA UNIFICADO & OPERACIONAL
"""

class ONIConfig:
    """Configuracao central do sistema ONI"""
    
    VERSION = "25.1"
    DATE = "2026-01-22"
    STATUS = "OPERACIONAL"
    SERVER_PORT = 8000
    BASE_URL = f"http://localhost:{SERVER_PORT}"
    
    # Paths do sistema
    DESIGN_PATH = "D:\\DESIGN"
    PSD_SOURCES_PATH = "D:\\DESIGN\\psd_sources"
    ATOM_PATH = "D:\\ATOM"
    RENDER_PATH = "D:\\RENDER"
    
    # Axiomas Inegociaveis
    AXIOMAS = {
        1: "read_terminal > command_status para esperar output",
        2: "write_to_file > abrir arquivo inexistente",
        3: "/api/hybrid-vision/ > acao visual cega",
        4: "Arquivo .jsx > JSX inline via PowerShell",
        5: "APIs REST ONI > criar scripts .py externos",
        6: "Coordenadas de canvas_limits > valores hardcoded",
        7: "Verificar apos Enter > assumir que dialogo fechou",
        8: "SafeToAutoRun: true > pedir permissao desnecessaria",
        9: "Tentar 3 estrategias (ToT) > desistir na primeira falha",
        10: "Registrar correcao do usuario em MEUS_ERROS.md > esquecer",
        11: "click > sem antes confirmar active-window"
    }
    
    # Erros Criticos Conhecidos
    ERROS_CRITICOS = {
        "ERR-001": {
            "problema": "Digitar sem Enter",
            "solucao": "SEMPRE enviar Enter apos campos"
        },
        "ERR-005": {
            "problema": "Get-Content retorna objeto",
            "solucao": "Usar [IO.File]::ReadAllText()"
        },
        "ERR-006": {
            "problema": "Executar sem Soul Binding",
            "solucao": "MANDATORY_STARTUP_CHECK acima"
        },
        "ERR-007": {
            "problema": "/api/type troca _ por espaco",
            "solucao": "Usar Clipboard ou renomear"
        }
    }


class ONIModules:
    """Gerenciador de modulos ONI"""
    
    CREATIVE_SUITE = {
        "ONI_VISUAL": {
            "app": "Photoshop",
            "path": "app/services/photoshop/composer_service.py",
            "protocol": "Hunter"
        },
        "ONI_VECTOR": {
            "app": "Illustrator",
            "path": "Modules/Photoshop/VectorFactory/",
            "protocol": "Neural-to-Vector"
        },
        "ONI_3D": {
            "app": "Blender",
            "path": "Modules/Blender/",
            "api": "Python API bpy"
        },
        "ONI_CAD": {
            "app": "AutoCAD",
            "path": "Modules/AutoCAD/",
            "automation": "ActiveX"
        },
        "ONI_FX": {
            "app": "After Effects",
            "path": "Modules/AfterEffects/"
        },
        "ONI_CUT": {
            "app": "Premiere",
            "path": "Modules/Premiere/"
        },
        "ONI_DRAW": {
            "app": "CorelDRAW",
            "path": "Modules/Corel/",
            "scripts": {
                "focus": "force_focus.ps1",
                "import": "import_logo.ps1",
                "trace": "manual_trace_helper.ps1"
            }
        },
        "ONI_MESH": {
            "app": "Maya",
            "path": "Modules/Maya/"
        }
    }
    
    OFFICE_PRODUCTIVITY = {
        "ONI_SHEETS": {"app": "Excel", "path": "Modules/Excel/"},
        "ONI_DOCS": {"app": "Word", "path": "Modules/Word/"},
        "ONI_PDF": {"app": "Foxit", "path": "Modules/Foxit/"},
        "ONI_TASKS": {"app": "Asana", "path": "Modules/Asana/"}
    }
    
    BROWSER_WEB = {
        "ONI_CHROME": {"path": "Modules/Chrome/"},
        "ONI_EDGE": {"path": "Modules/Edge/"}
    }
    
    SYSTEM_CORE = {
        "ONI_AUDIO": {"path": "Modules/Oni_Engine/oni_dsp.py"},
        "ONI_VIDEO": {"path": "Modules/Oni_Engine/oni_video_gen.py"},
        "ONI_OS": {"path": "Modules/Windows/"},
        "ONI_SECURITY": {"path": "Modules/Security/"},
        "SUPER_CEREBRO": {"path": "Modules/Super_Cerebro/"},
        "ONI_CORE": {"path": "Modules/Core/"}
    }


class ONIEndpoints:
    """Endpoints da API REST ONI"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    # Vision & Input
    VISION = {
        "desktop": "/api/hybrid-vision/desktop",
        "web": "/api/hybrid-vision/web",
        "active_window": "/api/active-window",
        "list_windows": "/api/list"
    }
    
    MOUSE = {
        "click": "/api/click",
        "double_click": "/api/mouse/double-click",
        "safe_drag": "/api/mouse/safe-drag"
    }
    
    KEYBOARD = {
        "keys": "/api/keys",
        "type": "/api/type"
    }
    
    WINDOW = {
        "focus": "/api/focus",
        "open": "/api/open",
        "windows": "/api/windows"
    }
    
    # Photoshop Deep Integration
    PHOTOSHOP = {
        "connect": "/api/photoshop/connect",
        "open": "/api/photoshop/open",
        "command": "/api/photoshop/command",
        "draw_stroke": "/api/photoshop/draw/stroke",
        "compose": "/api/photoshop/compose",
        "text_replace": "/api/photoshop/text/replace",
        "layers": "/api/photoshop/layers",
        "smart_object_open": "/api/photoshop/smart-object/open"
    }
    
    # Blender & 3D
    BLENDER = {
        "execute": "/api/blender/execute",
        "render": "/api/blender/render"
    }
    
    # Agent & Cognition
    AGENT = {
        "execute": "/api/v1/agent/execute",
        "status": "/api/v1/agent/status",
        "onihand_draw": "/api/v1/onihand/draw",
        "segment_analyze": "/api/segment/analyze"
    }
    
    # System & Utils
    SYSTEM = {
        "health": "/api/v1/health",
        "startup": "/api/autonomous/startup",
        "adapter_execute": "/api/adapter/execute",
        "adapter_resolve": "/api/adapter/resolve",
        "adapter_apps": "/api/adapter/apps",
        "adapter_actions": "/api/adapter/actions",
        "adapter_learn": "/api/adapter/learn"
    }
    
    # ArtMaster
    ARTMASTER = {
        "tool_select": "/api/artmaster/tool/select",
        "draw_line": "/api/artmaster/draw/line",
        "draw_rectangle": "/api/artmaster/draw/rectangle",
        "draw_circle": "/api/artmaster/draw/circle",
        "artistic_spiral": "/api/artmaster/artistic/spiral",
        "artistic_pointillism": "/api/artmaster/artistic/pointillism",
        "keyboard_hotkey": "/api/artmaster/keyboard/hotkey"
    }
    
    def get_url(self, category, endpoint_key):
        """Retorna URL completa do endpoint"""
        category_dict = getattr(self, category.upper(), {})
        endpoint = category_dict.get(endpoint_key, "")
        return f"{self.base_url}{endpoint}"


class ONIShortcuts:
    """Gerenciador de atalhos adaptadores"""
    
    SHORTCUTS_CONFIG = {
        "Photoshop": {
            "file": "Modules/Photoshop/Config/ps_shortcuts.json",
            "status": "ATIVO"
        },
        "Illustrator": {
            "file": "Modules/Illustrator/Config/ai_shortcuts.json",
            "status": "PRONTO"
        },
        "CorelDRAW": {
            "file": "Modules/Corel/Config/corel_shortcuts.json",
            "status": "PRONTO"
        },
        "After Effects": {
            "file": "Modules/AfterEffects/Config/ae_shortcuts.json",
            "status": "PRONTO"
        },
        "Maya": {
            "file": "Modules/Maya/Config/maya_shortcuts.json",
            "status": "PRONTO"
        },
        "Blender": {
            "file": "Modules/Blender/Config/blender_shortcuts.json",
            "status": "PRONTO"
        },
        "Premiere": {
            "file": "Modules/Premiere/Config/pr_shortcuts.json",
            "status": "PRONTO"
        },
        "AutoCAD": {
            "file": "Modules/AutoCAD/Config/autocad_shortcuts.json",
            "status": "PRONTO"
        },
        "Word": {
            "file": "Modules/Word/Config/word_shortcuts.json",
            "status": "PADRAO"
        },
        "Excel": {
            "file": "Modules/Excel/Config/excel_shortcuts.json",
            "status": "PADRAO"
        },
        "Foxit": {
            "file": "Modules/Foxit/Config/foxit_shortcuts.json",
            "status": "MANUAL"
        }
    }
    
    # Atalhos Universais Windows
    UNIVERSAL_SHORTCUTS = {
        "alt_tab": {"keys": "alt,tab", "action": "Alternar janelas"},
        "win_d": {"keys": "win,d", "action": "Mostrar desktop"},
        "alt_f4": {"keys": "alt,f4", "action": "Fechar janela"},
        "ctrl_w": {"keys": "ctrl,w", "action": "Fechar aba/documento"},
        "ctrl_z": {"keys": "ctrl,z", "action": "Desfazer"},
        "ctrl_y": {"keys": "ctrl,y", "action": "Refazer"},
        "ctrl_s": {"keys": "ctrl,s", "action": "Salvar"},
        "ctrl_n": {"keys": "ctrl,n", "action": "Novo"},
        "ctrl_o": {"keys": "ctrl,o", "action": "Abrir"},
        "escape": {"keys": "escape", "action": "Cancelar/Fechar"},
        "enter": {"keys": "enter", "action": "Confirmar"},
        "f5": {"keys": "f5", "action": "Atualizar"}
    }
    
    # Atalhos de Navegador
    BROWSER_SHORTCUTS = {
        "ctrl_l": {"keys": "ctrl,l", "action": "Focar barra de endereco"},
        "ctrl_t": {"keys": "ctrl,t", "action": "Nova aba"},
        "ctrl_w": {"keys": "ctrl,w", "action": "Fechar aba"},
        "ctrl_tab": {"keys": "ctrl,tab", "action": "Proxima aba"},
        "ctrl_shift_tab": {"keys": "ctrl,shift,tab", "action": "Aba anterior"},
        "f5": {"keys": "f5", "action": "Atualizar pagina"},
        "ctrl_f": {"keys": "ctrl,f", "action": "Buscar na pagina"},
        "escape": {"keys": "escape", "action": "Parar carregamento"},
        "alt_left": {"keys": "alt,left", "action": "Voltar"},
        "alt_right": {"keys": "alt,right", "action": "Avancar"}
    }
    
    # Atalhos Explorer
    EXPLORER_SHORTCUTS = {
        "win_e": {"keys": "win,e", "action": "Abrir Explorer"},
        "ctrl_l": {"keys": "ctrl,l", "action": "Focar barra endereco"},
        "ctrl_f": {"keys": "ctrl,f", "action": "Focar busca"},
        "f2": {"keys": "f2", "action": "Renomear"},
        "ctrl_shift_n": {"keys": "ctrl,shift,n", "action": "Nova pasta"}
    }


class ONIWorkflow:
    """Gerenciador do workflow universal ONI"""
    
    # As 27 Regras de Ouro
    REGRAS_DE_OURO = [
        "MISE EN PLACE PRIMEIRO - Nunca comecar sem planejar",
        "TREE OF THOUGHTS - Sempre ter 3 estrategias por acao",
        "HYBRID VISION SEMPRE - Antes E depois de cada acao",
        "ANNOTATED E VERDADE - JSON pode enganar, imagem nao",
        "VERIFICAR NAO E OPCIONAL - E obrigatorio",
        "TIMEOUT != ERRO - Verificar visualmente apos timeout",
        "ASTERISCO = MODIFICACAO - * no titulo confirma mudanca",
        "NUNCA ASSUMIR - Sempre confirmar com dados",
        "FALLBACK PRONTO - Ter plano B e C antes de executar",
        "TESTAR ANTES - Area segura antes de area critica",
        "ROLLBACK DISPONIVEL - Saber como desfazer antes de fazer",
        "JANELA CERTA - Verificar window_title antes de agir",
        "COORDENADAS FRESCAS - Re-escanear se UI pode ter mudado",
        "ENTER DEPOIS DE DIGITAR - Campos precisam confirmacao",
        "ZERO SCRIPTS EXTERNOS - Apenas APIs REST do ONI",
        "DIALOGO = ENTER - Apos Ctrl+N/O/S, SEMPRE confirmar com Enter",
        "CANVAS_LIMITS PRIMEIRO - NUNCA usar coordenadas arbitrarias",
        "VERIFICAR ENTRE CADA ACAO - Nao acumular acoes sem verificar",
        "CALCULAR, NAO CHUTAR - Coordenadas = formulas baseadas em canvas",
        "SCAN -> ACAO -> SCAN - Este e o ritmo obrigatorio",
        "WEB != DESKTOP - Navegador = /hybrid-vision/web, apps = /desktop",
        "FOCAR ANTES DE DIGITAR - Em browsers: /focus + Ctrl+L antes de URL",
        "CLICAR NO CAMPO - Em formularios: clicar no campo antes de digitar",
        "MULTI-APP = FOCO - Ao trocar de app: open -> verify -> focus -> verify -> agir",
        "LOOPS ESTRUTURADOS - Repeticoes devem ter lista, acao, verificacao, armazenamento",
        "COORDENADAS DO ANNOTATED - NUNCA usar coordenadas exemplo",
        "EXTENSOES CORRETAS - .xlsx (nao .xls), .docx (nao .doc), .psd"
    ]
    
    # Proibicoes Absolutas
    PROIBICOES = [
        "NUNCA criar scripts Python externos (.py)",
        "NUNCA usar subprocess/os.system",
        "NUNCA usar browser_subagent",
        "NUNCA agir sem antes escanear com Hybrid Vision",
        "NUNCA ignorar o annotated_path",
        "NUNCA confiar que um dialogo fechou sem verificar",
        "NUNCA usar Save As para criar arquivos novos (usar write_to_file primeiro)",
        "SEMPRE definir SafeToAutoRun: true em run_command",
        "SEMPRE usar APIs REST do ONI via read_url_content"
    ]
    
    @staticmethod
    def mandatory_startup_check():
        """Checklist obrigatorio antes de iniciar"""
        checklist = {
            "axiomas_conhecidos": "Sei os 10 axiomas?",
            "servidor_rodando": "Servidor ONI rodando?",
            "heartbeats_planejados": "Vou emitir Heartbeats?"
        }
        return checklist
    
    @staticmethod
    def heartbeat_check():
        """Verificacao de conformidade a cada ~10 tool calls"""
        checks = {
            "axioma_aplicavel": "Axioma aplicavel agora? Qual?",
            "read_terminal_ok": "read_terminal antes de command_status? OK",
            "hybrid_vision_ok": "hybrid-vision antes de acao visual? OK"
        }
        return checks
    
    @staticmethod
    def pre_execution_checklist():
        """Checklist antes de executar qualquer acao de desenho/modificacao"""
        checklist = [
            "Fiz scan inicial com Hybrid Vision?",
            "Verifiquei window_title = app correto?",
            "Verifiquei canvas_limits != null?",
            "Calculei coordenadas baseado em canvas_limits?",
            "Coordenadas estao DENTRO da area do canvas?",
            "Tenho 3 estrategias no ToT?",
            "Sei como verificar se a acao funcionou?",
            "Sei como fazer rollback se falhar?"
        ]
        return checklist
    
    @staticmethod
    def auto_perguntas_nivel1():
        """Auto-perguntas nivel 1: Contexto"""
        return [
            "Este e o aplicativo correto (window_title)?",
            "A janela esta em FOCO?",
            "Existe algum dialogo modal bloqueando a acao?"
        ]
    
    @staticmethod
    def auto_perguntas_nivel2():
        """Auto-perguntas nivel 2: Precisao"""
        return [
            "Esta coordenada (x,y) e fruto de um scan feito HA MENOS DE 30 SEGUNDOS?",
            "Se for desenho, os pontos estao dentro do canvas_limits?",
            "Eu tenho uma estrategia de Rollback (Ctrl+Z) se isso falhar?"
        ]
    
    @staticmethod
    def auto_perguntas_nivel3():
        """Auto-perguntas nivel 3: Execucao Automatica"""
        return [
            "O comando esta configurado com SafeToAutoRun: true?",
            "Eu previ a necessidade de pressionar ENTER apos este comando?",
            "Este comando e uma transacao? Gravei o estado inicial?"
        ]


class ONIProtocols:
    """Protocolos de robustez e fail-safe"""
    
    @staticmethod
    def pad_protocol():
        """PAD - Protocolo Anti-Dialogo"""
        return {
            "regra": "E ESTRITAMENTE PROIBIDO usar Dialogos de Arquivo",
            "substituicoes": {
                "salvar_novo_arquivo": {
                    "antigo": "Ctrl+S -> Digitar Caminho -> Enter",
                    "novo": "write_to_file (criar esqueleto) -> Start-Process (abrir) -> Ctrl+S (salvar direto)"
                },
                "inserir_imagem": {
                    "antigo": "Menu Inserir -> Navegar no Explorer",
                    "novo": "Abrir Imagem no Paint -> Ctrl+C -> Voltar ao App -> Ctrl+V"
                }
            }
        }
    
    @staticmethod
    def pwf_protocol():
        """PWF - Principio Write-First"""
        return {
            "principio": "O arquivo deve existir antes de ser aberto",
            "fluxo": [
                "CRIAR: Use write_to_file para criar o arquivo no disco (mesmo vazio)",
                "ABRIR: Use Start-Process para abrir esse arquivo especifico",
                "EDITAR: Faca as edicoes visuais necessarias",
                "SALVAR: Use Ctrl+S (o dialogo Salvar Como NAO aparecera)"
            ]
        }
    
    @staticmethod
    def vfj_protocol():
        """VFJ - Verificacao de Fechamento de Janela"""
        return {
            "regra": "Enter nao garante nada",
            "acao_obrigatoria": "Executar scan imediato (hybrid-vision) para confirmar",
            "fallbacks": [
                "Tentar Escape",
                "Tentar clicar em Cancelar",
                "Pivotar estrategia (Abortar via UI e tentar via Sistema)"
            ]
        }
    
    @staticmethod
    def sistema_transacional():
        """Sistema Transacional com Rollback"""
        return {
            "conceito": "Operacoes complexas sao tratadas como transacoes",
            "fluxo": [
                "Captura estado antes da acao (Hybrid Vision)",
                "Executa acao (API ONI)",
                "Verifica resultado (Hybrid Vision + annotated)",
                "Se falhar: rollback automatico + proximo fallback",
                "Se sucesso: proxima etapa"
            ],
            "checkpoints": [
                "Apos abrir aplicativo",
                "Apos criar/carregar documento",
                "Antes de operacoes destrutivas",
                "Antes de salvar",
                "Apos cada desenho/modificacao"
            ]
        }


class ONITreeOfThoughts:
    """Implementacao do Tree of Thoughts (ToT)"""
    
    @staticmethod
    def generate_strategies(action_name, strategies_list):
        """Gera template de ToT para uma acao"""
        tot = {
            "action": action_name,
            "strategies": []
        }
        
        for i, strategy in enumerate(strategies_list, 1):
            tot["strategies"].append({
                "number": i,
                "method": strategy.get("method", ""),
                "endpoint": strategy.get("endpoint", ""),
                "confidence": strategy.get("confidence", 0.0),
                "risk": strategy.get("risk", "Medium")
            })
        
        return tot
    
    @staticmethod
    def execute_with_fallback(strategies):
        """Executa estrategias com fallback automatico"""
        execution_plan = []
        
        for i, strategy in enumerate(strategies, 1):
            step = {
                "step": i,
                "execute": strategy["method"],
                "verify": "Hybrid Vision",
                "on_success": "Proxima acao do plano" if i == len(strategies) else None,
                "on_failure": f"Tentar estrategia #{i+1}" if i < len(strategies) else "Reportar falha"
            }
            execution_plan.append(step)
        
        return execution_plan
    
    @staticmethod
    def example_open_file_photoshop():
        """Exemplo: ToT para abrir arquivo no Photoshop"""
        strategies = [
            {
                "method": "Ctrl+O",
                "endpoint": "/api/keys?keys=ctrl,o",
                "confidence": 0.95,
                "risk": "Low"
            },
            {
                "method": "Menu Arquivo > Abrir",
                "endpoint": "/api/click em coordenadas",
                "confidence": 0.6,
                "risk": "Medium"
            },
            {
                "method": "Drag & Drop",
                "endpoint": "/api/mouse/safe-drag",
                "confidence": 0.4,
                "risk": "High"
            }
        ]
        return ONITreeOfThoughts.generate_strategies("Abrir arquivo no Photoshop", strategies)
    
    @staticmethod
    def example_type_path():
        """Exemplo: ToT para digitar caminho do arquivo"""
        strategies = [
            {
                "method": "Digitar + Enter",
                "endpoint": "/api/type + /api/keys?keys=enter",
                "confidence": 0.95,
                "risk": "Low"
            },
            {
                "method": "Colar do clipboard",
                "endpoint": "/api/keys?keys=ctrl,v",
                "confidence": 0.85,
                "risk": "Low"
            },
            {
                "method": "Navegar pelo Explorer",
                "endpoint": "Multiplos clicks",
                "confidence": 0.3,
                "risk": "High"
            }
        ]
        return ONITreeOfThoughts.generate_strategies("Digitar caminho do arquivo", strategies)


class ONICoordinates:
    """Gerenciador de coordenadas baseado em canvas_limits"""
    
    @staticmethod
    def calculate_center(canvas_limits):
        """Calcula centro do canvas"""
        return {
            "x": canvas_limits.get("center_x"),
            "y": canvas_limits.get("center_y")
        }
    
    @staticmethod
    def calculate_corner_top_left(canvas_limits, margin=50):
        """Calcula canto superior esquerdo com margem"""
        return {
            "x": canvas_limits["x"] + margin,
            "y": canvas_limits["y"] + margin
        }
    
    @staticmethod
    def calculate_corner_bottom_right(canvas_limits, margin=50):
        """Calcula canto inferior direito com margem"""
        return {
            "x": canvas_limits["x"] + canvas_limits["width"] - margin,
            "y": canvas_limits["y"] + canvas_limits["height"] - margin
        }
    
    @staticmethod
    def calculate_half_left(canvas_limits):
        """Calcula metade esquerda do canvas"""
        return {
            "x": canvas_limits["x"] + canvas_limits["width"] * 0.25,
            "y": canvas_limits.get("center_y")
        }
    
    @staticmethod
    def calculate_half_right(canvas_limits):
        """Calcula metade direita do canvas"""
        return {
            "x": canvas_limits["x"] + canvas_limits["width"] * 0.75,
            "y": canvas_limits.get("center_y")
        }
    
    @staticmethod
    def validate_coordinates(x, y, canvas_limits):
        """Valida se coordenadas estao dentro do canvas"""
        x_min = canvas_limits["x"]
        x_max = canvas_limits["x"] + canvas_limits["width"]
        y_min = canvas_limits["y"]
        y_max = canvas_limits["y"] + canvas_limits["height"]
        
        is_valid = (x_min <= x <= x_max) and (y_min <= y <= y_max)
        
        return {
            "valid": is_valid,
            "x": x,
            "y": y,
            "bounds": {
                "x_min": x_min,
                "x_max": x_max,
                "y_min": y_min,
                "y_max": y_max
            }
        }
    
    @staticmethod
    def example_bicycle_wheels(canvas_limits):
        """Exemplo pratico: Coordenadas para desenhar rodas de bicicleta"""
        rear_wheel = {
            "center_x": canvas_limits["x"] + canvas_limits["width"] * 0.25,
            "center_y": canvas_limits.get("center_y", 560) + 100,
            "radius": 80
        }
        
        front_wheel = {
            "center_x": canvas_limits["x"] + canvas_limits["width"] * 0.75,
            "center_y": canvas_limits.get("center_y", 560) + 100,
            "radius": 80
        }
        
        return {
            "rear_wheel": rear_wheel,
            "front_wheel": front_wheel
        }


class ONITelemetry:
    """Sistema de telemetria e aprendizado"""
    
    TELEMETRY_SIGNALS = {
        "title_modification": {
            "weight": "High",
            "meaning": "Documento alterado",
            "detection": "* no window_title"
        },
        "canvas_ui_change": {
            "weight": "High",
            "meaning": "Desenho realizado",
            "detection": "Diferenca de pixels no annotated_path"
        },
        "process_load": {
            "weight": "Medium",
            "meaning": "App iniciou",
            "detection": "CPU/Memory spike + window list"
        },
        "wait_cursor": {
            "weight": "Low",
            "meaning": "App ocupado",
            "detection": "Mouse cursor icon change"
        },
        "new_dialog": {
            "weight": "High",
            "meaning": "Interrupcao",
            "detection": "Nova janela modal detectada"
        }
    }
    
    @staticmethod
    def record_action(action_data):
        """Grava acao para aprendizado posterior"""
        record = {
            "initial_state": action_data.get("screenshot"),
            "ui_tree": action_data.get("ui_tree"),
            "command_sent": action_data.get("command"),
            "api_endpoint": action_data.get("endpoint"),
            "latency": action_data.get("latency_ms"),
            "response": action_data.get("response"),
            "final_state": action_data.get("final_screenshot"),
            "hybrid_vision": action_data.get("hybrid_scan"),
            "success": action_data.get("success", False)
        }
        return record
    
    @staticmethod
    def analyze_latency_zone(zone_data):
        """Analisa zonas de alta latencia"""
        if zone_data.get("response_time_ms", 0) > 2000:
            return {
                "zone": zone_data.get("screen_area"),
                "marked_as": "High Latency Zone",
                "action": "Incrementar wait_ms automaticamente",
                "recommendation": "Priorizar atalhos de teclado (keys) em vez de clicks"
            }
        return None


class ONIAdapter:
    """Sistema Universal de Atalhos (Adapter)"""
    
    @staticmethod
    def resolve_shortcut(app_name, action):
        """Resolve atalho correto para app e acao especificos"""
        shortcuts_db = {
            "Photoshop": {
                "save": "ctrl,s",
                "new": "ctrl,n",
                "open": "ctrl,o",
                "close": "ctrl,w"
            },
            "Notepad": {
                "save": "ctrl,s",
                "new": "ctrl,n",
                "open": "ctrl,o"
            },
            "Excel": {
                "save": "ctrl,s",
                "new": "ctrl,n"
            }
        }
        
        app_shortcuts = shortcuts_db.get(app_name, {})
        shortcut = app_shortcuts.get(action)
        
        if shortcut:
            return {
                "app": app_name,
                "action": action,
                "shortcut": shortcut,
                "endpoint": f"/api/keys?keys={shortcut}"
            }
        else:
            return {
                "app": app_name,
                "action": action,
                "shortcut": None,
                "status": "Unknown - Enter Discovery Mode"
            }
    
    @staticmethod
    def discovery_mode(app_name, action):
        """Modo Discovery para aprender novos atalhos"""
        steps = [
            "Tentar atalhos universais Windows (Ctrl+S, Ctrl+O)",
            "Se falhar, analisar menus via Hybrid Vision",
            "Ao encontrar, memorizar via /api/adapter/learn"
        ]
        return {
            "app": app_name,
            "action": action,
            "mode": "Discovery",
            "steps": steps
        }


class ONIDecisionTree:
    """Arvore de Decisao Estruturada"""
    
    PRIORITY_MATRIX = {
        1: {
            "method": "adapter",
            "when": "Acoes padrao (Save, New)",
            "why": "Resolve atalhos app-especificos"
        },
        2: {
            "method": "keys",
            "when": "Dialogos, Menus, Navegacao",
            "why": "Resposta instantanea, sem erro de mira"
        },
        3: {
            "method": "type",
            "when": "Campos de texto, Busca",
            "why": "Mais rapido que clicar letra por letra"
        },
        4: {
            "method": "click",
            "when": "Botoes UI, Icones",
            "why": "Requer scan fresco para precisao"
        },
        5: {
            "method": "safe-drag",
            "when": "Desenho manual, Sliders",
            "why": "Alto risco de desvio visual"
        }
    }
    
    @staticmethod
    def recognize_phase(context):
        """Fase de Reconhecimento"""
        recommendations = []
        
        if context.get("window_title_changed"):
            recommendations.append("Priorizar Teclado (keys: Enter/Escape)")
        
        if context.get("canvas_limits") is not None:
            recommendations.append("Priorizar ArtMaster/Desenho")
        
        if context.get("ui_elements_detected"):
            recommendations.append("Priorizar Click via Coordenadas do Annotated")
        
        if context.get("url_required"):
            recommendations.append("Priorizar focus -> ctrl+l -> type")
        
        return recommendations
    
    @staticmethod
    def click_decision_flow():
        """Fluxo de decisao para clique"""
        flow = {
            "question": "Preciso clicar em algo?",
            "options": {
                "has_keyboard_shortcut": {
                    "yes": "Usar /api/adapter ou /api/keys",
                    "no": {
                        "element_detected_in_json": {
                            "yes": "Usar coords do JSON rect",
                            "no": [
                                "Analisar annotated_path manualmente",
                                "Obter coordenadas X,Y da imagem",
                                "Executar /api/click"
                            ]
                        }
                    }
                }
            }
        }
        return flow


class ONIErrorHandling:
    """Tratamento de erros"""
    
    ERROR_TYPES = {
        "timeout": {
            "cause": "Operacao lenta (ex: desenho artistico, app abrindo)",
            "action": "Ignorar timeout, verificar com Hybrid Vision depois",
            "note": "Nao significa erro! Timeouts em operacoes lentas sao normais"
        },
        "404_422": {
            "cause": "Endpoint errado ou parametros invalidos",
            "action": "Verificar sintaxe do endpoint e parametros"
        },
        "wrong_app": {
            "cause": "window_title nao era o esperado",
            "action": "SEMPRE verificar janela ativa antes de agir"
        },
        "wrong_coordinates": {
            "cause": "UI mudou ou canvas_limits desatualizado",
            "action": "Re-escanear com Hybrid Vision e recalcular"
        },
        "element_not_found": {
            "cause": "UI diferente do esperado",
            "action": "Analisar annotated, ajustar estrategia (usar ToT fallbacks)"
        }
    }
    
    @staticmethod
    def handle_error(error_type, context=None):
        """Retorna estrategia de tratamento para erro especifico"""
        error_info = ONIErrorHandling.ERROR_TYPES.get(error_type)
        
        if error_info:
            return {
                "error_type": error_type,
                "cause": error_info["cause"],
                "recommended_action": error_info["action"],
                "context": context
            }
        else:
            return {
                "error_type": error_type,
                "status": "Unknown error type",
                "recommended_action": "Check documentation"
            }


class ONIWorkflowSteps:
    """Etapas do Workflow Universal"""
    
    @staticmethod
    def step0_mise_en_place(task_name, objective, target_app, expected_result):
        """ETAPA 0: Mise en Place (Obrigatorio)"""
        return {
            "task": task_name,
            "definition": {
                "objective": objective,
                "target_app": target_app,
                "expected_result": expected_result
            },
            "planned_steps": [],
            "weak_points": {}
        }
    
    @staticmethod
    def step1_initial_scan(timestamp):
        """ETAPA 1: Scan Inicial"""
        return {
            "action": "GET http://localhost:8000/api/hybrid-vision/desktop",
            "params": f"?nocache={timestamp}",
            "analyze": [
                "window_title",
                "canvas_limits",
                "elements",
                "annotated_path"
            ]
        }
    
    @staticmethod
    def step2_verify_app(expected_app):
        """ETAPA 2: Verificar App"""
        return {
            "check": "Is correct app?",
            "expected": expected_app,
            "if_correct": "Continue",
            "if_wrong": "Use /api/focus or /api/open"
        }
    
    @staticmethod
    def step3_prepare_environment():
        """ETAPA 3: Preparar Ambiente"""
        return {
            "tasks": [
                "Criar documento se necessario",
                "Fechar dialogos indesejados",
                "Verificar com Hybrid Vision"
            ]
        }
    
    @staticmethod
    def step4_identify_coordinates(canvas_limits, elements):
        """ETAPA 4: Identificar Coordenadas"""
        return {
            "canvas_area": canvas_limits,
            "ui_elements": elements,
            "calculate": "Safe positions based on canvas_limits"
        }
    
    @staticmethod
    def step5_execute_with_tot(actions):
        """ETAPA 5: Executar (com ToT)"""
        execution_steps = []
        
        for action in actions:
            step = {
                "generate_tot": "3 strategies",
                "execute": "Strategy #1",
                "verify": "Hybrid Vision",
                "on_failure": "Try Strategy #2",
                "on_success": "Next action"
            }
            execution_steps.append(step)
        
        return execution_steps
    
    @staticmethod
    def step6_verify_result():
        """ETAPA 6: Verificar Resultado"""
        return {
            "final_scan": "Hybrid Vision",
            "confirm": "Expected state",
            "document": "Result"
        }


class ONIExamples:
    """Exemplos completos de uso"""
    
    @staticmethod
    def example_open_file_in_photoshop():
        """Exemplo: Abrir D:\\99.png no Photoshop"""
        workflow = {
            "task": "Abrir D:\\99.png no Photoshop",
            "steps": [
                {
                    "tot_1": "Abrir Photoshop",
                    "strategies": [
                        {"priority": 1, "method": "API open", "endpoint": "/api/open?name=photoshop", "confidence": 0.9},
                        {"priority": 2, "method": "Win+R", "endpoint": "/api/keys sequence", "confidence": 0.7},
                        {"priority": 3, "method": "Desktop icon", "endpoint": "/api/click coords", "confidence": 0.5}
                    ],
                    "execute": "Strategy #1",
                    "verify": "Hybrid Vision",
                    "result": "Success"
                },
                {
                    "tot_2": "Abrir dialogo de arquivo",
                    "strategies": [
                        {"priority": 1, "method": "Ctrl+O", "endpoint": "/api/keys?keys=ctrl,o", "confidence": 0.95},
                        {"priority": 2, "method": "Menu Arquivo", "endpoint": "Sequential clicks", "confidence": 0.6}
                    ],
                    "execute": "Strategy #1",
                    "verify": "Hybrid Vision",
                    "result": "Success"
                },
                {
                    "tot_3": "Digitar caminho",
                    "strategies": [
                        {"priority": 1, "method": "Type + Enter", "endpoint": "/api/type + /api/keys?keys=enter", "confidence": 0.95},
                        {"priority": 2, "method": "Navigate folders", "endpoint": "Multiple clicks", "confidence": 0.3}
                    ],
                    "execute": "Strategy #1",
                    "verify": "Hybrid Vision",
                    "result": "Success"
                }
            ]
        }
        return workflow
    
    @staticmethod
    def example_browser_search():
        """Exemplo: Busca em site (Mercado Livre)"""
        workflow = {
            "task": "Pesquisar iPhone 10 no Mercado Livre",
            "steps": [
                {"action": "Focus browser", "endpoint": "/api/focus?title=Firefox"},
                {"action": "Focus address bar", "endpoint": "/api/keys?keys=ctrl,l"},
                {"action": "Type URL", "endpoint": "/api/type?text=https://www.mercadolivre.com.br"},
                {"action": "Confirm", "endpoint": "/api/keys?keys=enter"},
                {"action": "Scan page", "endpoint": "/api/hybrid-vision/web?nocache=site_loaded"},
                {"action": "Identify search field", "method": "Analyze annotated"},
                {"action": "Click field", "endpoint": "/api/click?x=[coord]&y=[coord]"},
                {"action": "Type search", "endpoint": "/api/type?text=iphone 10"},
                {"action": "Confirm search", "endpoint": "/api/keys?keys=enter"},
                {"action": "Scan results", "endpoint": "/api/hybrid-vision/web?nocache=results"}
            ]
        }
        return workflow
    
    @staticmethod
    def example_multi_app_task():
        """Exemplo: Tarefa Multi-App (Firefox -> Excel -> Photoshop)"""
        workflow = {
            "task": "Coletar dados do Firefox, processar no Excel, criar visual no Photoshop",
            "phases": [
                {
                    "phase": "FASE 1: App A (Firefox)",
                    "steps": [
                        {"action": "Open", "endpoint": "/api/open?name=firefox"},
                        {"action": "Verify", "endpoint": "/api/hybrid-vision/desktop"},
                        {"action": "Focus", "endpoint": "/api/focus?title=Firefox"},
                        {"action": "Execute actions", "details": "Collect data"},
                        {"action": "Store data", "format": "JSON/Dict"}
                    ]
                },
                {
                    "phase": "FASE 2: App B (Excel)",
                    "steps": [
                        {"action": "Open", "endpoint": "/api/open?name=excel"},
                        {"action": "Verify", "endpoint": "/api/hybrid-vision/desktop"},
                        {"action": "Focus", "endpoint": "/api/focus?title=Excel"},
                        {"action": "Execute actions", "details": "Process collected data"}
                    ]
                },
                {
                    "phase": "FASE 3: App C (Photoshop)",
                    "steps": [
                        {"action": "Open", "endpoint": "/api/open?name=photoshop"},
                        {"action": "Verify", "endpoint": "/api/hybrid-vision/desktop"},
                        {"action": "Focus", "endpoint": "/api/focus?title=Photoshop"},
                        {"action": "Execute actions", "details": "Create visual output"}
                    ]
                }
            ]
        }
        return workflow


class ONIProtocolWeb:
    """Protocolo de Navegacao Web"""
    
    @staticmethod
    def anti_redirect_strategy():
        """Estrategia Anti-Redirecionamento (Loop Infinito)"""
        return {
            "symptom": "Browser insiste em redirecionar para homepage",
            "cause": "Cache viciado, Cookies persistentes ou Extensoes interferindo",
            "solution": {
                "command": "/oni_turbo",
                "why": "Workflow possui permissao turbo-all para executar correcoes agressivas (Kill/Restart)"
            }
        }
    
    @staticmethod
    def os_command_security():
        """Seguranca de Comandos OS (PowerShell)"""
        return {
            "rule": "Comandos de sistema (Start-Process, Stop-Process) sao de ALTO RISCO",
            "restrictions": {
                "auto_run_denied": "Sistema ignorara SafeToAutoRun: true para esses comandos",
                "human_interaction": "Usuario SEMPRE precisara aprovar",
                "silent_failure": "Se usuario nao aprovar rapido ou cancelar, comando falha"
            },
            "mitigation": "Avisar o usuario ANTES de rodar: 'Vou executar um comando de sistema que requer sua aprovacao manual.'"
        }


# ============================================================================
# FUNCOES PRINCIPAIS DE EXECUCAO
# ============================================================================

def oni_startup_sequence():
    """Sequencia de startup do ONI"""
    print("=" * 80)
    print("ONI V25 - STARTUP SEQUENCE")
    print("=" * 80)
    
    # Passo 1: Ler documentacao
    print("\n[PASSO 1] Lendo documentacao MASTER...")
    print("  - MASTER.md")
    print("  - ONI_TRIGGERS_AND_PROTOCOLS.md")
    
    # Passo 2: Ler erros conhecidos
    print("\n[PASSO 2] Lendo erros conhecidos...")
    print("  - MEUS_ERROS.md")
    
    # Passo 3: Verificar servidor
    print("\n[PASSO 3] Verificando servidor ONI (Porta 8000)...")
    config = ONIConfig()
    print(f"  - URL: {config.BASE_URL}/api/autonomous/startup")
    
    # Passo 4: Confirmar status
    print("\n[PASSO 4] Status do sistema...")
    print("  - ONI ONLINE E PRONTO PARA TAREFA")
    
    print("\n" + "=" * 80)
    print("SISTEMA OPERACIONAL")
    print("=" * 80)


def ant_startup_sequence():
    """Sequencia de startup do ANT (Modo Dev)"""
    print("=" * 80)
    print("ANT (ANTIGRAVITY) - DEV MODE")
    print("=" * 80)
    
    print("\n[MODO DEV] Engenheiro de Software Senior")
    print("[FOCO] Codigo-Fonte (./app ou raiz do workspace)")
    print("[OBJETIVO] Implementacao, Refatoracao e Arquitetura do Sistema ONI")
    
    print("\n" + "=" * 80)
    print("ANTIGRAVITY ATIVO: PRONTO PARA CODAR")
    print("=" * 80)


def display_regras_de_ouro():
    """Exibe as 27 Regras de Ouro"""
    print("\n" + "=" * 80)
    print("AS 27 REGRAS DE OURO")
    print("=" * 80)
    
    workflow = ONIWorkflow()
    for i, regra in enumerate(workflow.REGRAS_DE_OURO, 1):
        print(f"{i:2d}. {regra}")
    
    print("=" * 80)


def display_axiomas():
    """Exibe os 10 Axiomas Inegociaveis"""
    print("\n" + "=" * 80)
    print("OS 10 AXIOMAS INEGOCIAVEIS")
    print("=" * 80)
    
    config = ONIConfig()
    for num, axioma in config.AXIOMAS.items():
        print(f"{num:2d}. {axioma}")
    
    print("=" * 80)


def display_endpoints():
    """Exibe referencia de endpoints"""
    print("\n" + "=" * 80)
    print("REFERENCIA DE ENDPOINTS ONI")
    print("=" * 80)
    
    endpoints = ONIEndpoints()
    
    print("\n[VISION & INPUT]")
    for key, value in endpoints.VISION.items():
        print(f"  {key:20s} : {value}")
    
    print("\n[MOUSE]")
    for key, value in endpoints.MOUSE.items():
        print(f"  {key:20s} : {value}")
    
    print("\n[KEYBOARD]")
    for key, value in endpoints.KEYBOARD.items():
        print(f"  {key:20s} : {value}")
    
    print("\n[PHOTOSHOP]")
    for key, value in endpoints.PHOTOSHOP.items():
        print(f"  {key:20s} : {value}")
    
    print("\n[ARTMASTER]")
    for key, value in endpoints.ARTMASTER.items():
        print(f"  {key:20s} : {value}")
    
    print("=" * 80)


def display_shortcuts():
    """Exibe atalhos universais"""
    print("\n" + "=" * 80)
    print("ATALHOS UNIVERSAIS WINDOWS")
    print("=" * 80)
    
    shortcuts = ONIShortcuts()
    
    print("\n[UNIVERSAL]")
    for key, value in shortcuts.UNIVERSAL_SHORTCUTS.items():
        print(f"  {value['keys']:20s} -> {value['action']}")
    
    print("\n[BROWSER]")
    for key, value in shortcuts.BROWSER_SHORTCUTS.items():
        print(f"  {value['keys']:20s} -> {value['action']}")
    
    print("\n[EXPLORER]")
    for key, value in shortcuts.EXPLORER_SHORTCUTS.items():
        print(f"  {value['keys']:20s} -> {value['action']}")
    
    print("=" * 80)


def demonstrate_tot():
    """Demonstra Tree of Thoughts"""
    print("\n" + "=" * 80)
    print("TREE OF THOUGHTS (ToT) - EXEMPLO")
    print("=" * 80)
    
    tot = ONITreeOfThoughts()
    
    print("\n[EXEMPLO 1: Abrir arquivo no Photoshop]")
    example1 = tot.example_open_file_photoshop()
    print(f"Acao: {example1['action']}")
    for strategy in example1['strategies']:
        print(f"  #{strategy['number']} - {strategy['method']:30s} | Confianca: {strategy['confidence']} | Risco: {strategy['risk']}")
    
    print("\n[EXEMPLO 2: Digitar caminho do arquivo]")
    example2 = tot.example_type_path()
    print(f"Acao: {example2['action']}")
    for strategy in example2['strategies']:
        print(f"  #{strategy['number']} - {strategy['method']:30s} | Confianca: {strategy['confidence']} | Risco: {strategy['risk']}")
    
    print("=" * 80)


def demonstrate_coordinates():
    """Demonstra calculo de coordenadas"""
    print("\n" + "=" * 80)
    print("CALCULO DE COORDENADAS (canvas_limits)")
    print("=" * 80)
    
    # Canvas example
    canvas_limits = {
        "x": 150,
        "y": 200,
        "width": 1280,
        "height": 720,
        "center_x": 790,
        "center_y": 560
    }
    
    coords = ONICoordinates()
    
    print("\n[CANVAS LIMITS]")
    for key, value in canvas_limits.items():
        print(f"  {key:15s} : {value}")
    
    print("\n[CALCULOS]")
    center = coords.calculate_center(canvas_limits)
    print(f"  Centro           : ({center['x']}, {center['y']})")
    
    top_left = coords.calculate_corner_top_left(canvas_limits)
    print(f"  Canto Sup. Esq.  : ({top_left['x']}, {top_left['y']})")
    
    bottom_right = coords.calculate_corner_bottom_right(canvas_limits)
    print(f"  Canto Inf. Dir.  : ({bottom_right['x']}, {bottom_right['y']})")
    
    half_left = coords.calculate_half_left(canvas_limits)
    print(f"  Metade Esquerda  : ({half_left['x']}, {half_left['y']})")
    
    half_right = coords.calculate_half_right(canvas_limits)
    print(f"  Metade Direita   : ({half_right['x']}, {half_right['y']})")
    
    print("\n[EXEMPLO: Rodas de Bicicleta]")
    bicycle = coords.example_bicycle_wheels(canvas_limits)
    print(f"  Roda Traseira : Centro ({bicycle['rear_wheel']['center_x']}, {bicycle['rear_wheel']['center_y']}) | Raio: {bicycle['rear_wheel']['radius']}")
    print(f"  Roda Dianteira: Centro ({bicycle['front_wheel']['center_x']}, {bicycle['front_wheel']['center_y']}) | Raio: {bicycle['front_wheel']['radius']}")
    
    print("=" * 80)


def main():
    """Funcao principal - Demonstracao completa do sistema ONI"""
    print("\n")
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + " " * 20 + "ONI V25 - MASTER REFERENCE" + " " * 32 + "#")
    print("#" + " " * 15 + "SISTEMA UNIFICADO & OPERACIONAL" + " " * 32 + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    # Exibir informacoes do sistema
    config = ONIConfig()
    print(f"\nVersao: {config.VERSION}")
    print(f"Data: {config.DATE}")
    print(f"Status: {config.STATUS}")
    print(f"Servidor: {config.BASE_URL}")
    
    # Menu interativo
    while True:
        print("\n" + "=" * 80)
        print("MENU PRINCIPAL")
        print("=" * 80)
        print("1. ONI Startup (Modo Autonomo)")
        print("2. ANT Startup (Modo Dev)")
        print("3. Exibir 27 Regras de Ouro")
        print("4. Exibir 10 Axiomas Inegociaveis")
        print("5. Exibir Endpoints API")
        print("6. Exibir Atalhos Universais")
        print("7. Demonstrar Tree of Thoughts (ToT)")
        print("8. Demonstrar Calculo de Coordenadas")
        print("9. Exibir Exemplo Completo (Abrir arquivo Photoshop)")
        print("0. Sair")
        print("=" * 80)
        
        choice = input("\nEscolha uma opcao: ")
        
        if choice == "1":
            oni_startup_sequence()
        elif choice == "2":
            ant_startup_sequence()
        elif choice == "3":
            display_regras_de_ouro()
        elif choice == "4":
            display_axiomas()
        elif choice == "5":
            display_endpoints()
        elif choice == "6":
            display_shortcuts()
        elif choice == "7":
            demonstrate_tot()
        elif choice == "8":
            demonstrate_coordinates()
        elif choice == "9":
            examples = ONIExamples()
            workflow = examples.example_open_file_in_photoshop()
            print("\n" + "=" * 80)
            print("EXEMPLO COMPLETO: Abrir D:\\99.png no Photoshop")
            print("=" * 80)
            print(f"\nTarefa: {workflow['task']}\n")
            for i, step in enumerate(workflow['steps'], 1):
                print(f"[PASSO {i}] {list(step.keys())[0]}")
                for strategy in step['strategies']:
                    print(f"  Prioridade {strategy['priority']}: {strategy['method']} | {strategy['endpoint']} | Conf: {strategy['confidence']}")
                print(f"  Executar: {step['execute']}")
                print(f"  Verificar: {step['verify']}")
                print(f"  Resultado: {step['result']}\n")
            print("=" * 80)
        elif choice == "0":
            print("\nEncerrando ONI V25...")
            break
        else:
            print("\nOpcao invalida! Tente novamente.")
        
        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    main()