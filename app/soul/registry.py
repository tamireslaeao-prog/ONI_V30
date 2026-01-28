from enum import Enum
from typing import Dict, List, NamedTuple

# -------------------------------------------------------------------------
# 🐛 ERROS CRÍTICOS CONHECIDOS (Reference: MASTER.md lines 66-74)
# -------------------------------------------------------------------------
class ErrorDefinition(NamedTuple):
    id: str
    problem: str
    solution: str

KNOWN_ERRORS: Dict[str, ErrorDefinition] = {
    "ERR-001": ErrorDefinition("ERR-001", "Digitar sem Enter", "SEMPRE enviar Enter após campos"),
    "ERR-005": ErrorDefinition("ERR-005", "Get-Content retorna objeto", "Usar [IO.File]::ReadAllText()"),
    "ERR-006": ErrorDefinition("ERR-006", "Executar sem Soul Binding", "MANDATORY_STARTUP_CHECK (Manual)"),
    "ERR-007": ErrorDefinition("ERR-007", "/api/type troca _ por espaço", "Usar Clipboard ou renomear"),
}

# -------------------------------------------------------------------------
# 🛡️ PROTOCOLOS DE ROBUSTEZ (Reference: MASTER.md lines 255-288)
# -------------------------------------------------------------------------
class Protocol(NamedTuple):
    acronym: str
    name: str
    rule: str
    solution: str

ROBUSTNESS_PROTOCOLS: List[Protocol] = [
    Protocol("PAD", "Protocolo Anti-Diálogo", "Janelas nativas são zonas de morte", "Usar write_to_file + Start-Process em vez de Save As"),
    Protocol("PWF", "Princípio Write-First", "O arquivo deve existir antes de ser aberto", "Criar arquivo vazio -> Abrir -> Editar -> Ctrl+S"),
    Protocol("VFJ", "Verificação de Fechamento de Janela", "Enter não garante nada", "Scan imediato (hybrid-vision) após qualquer ação que fecha janelas"),
]

# -------------------------------------------------------------------------
# ⌨️ ATALHOS UNIVERSAIS WINDOWS (Reference: MASTER.md lines 532-550)
# -------------------------------------------------------------------------
class Shortcut(NamedTuple):
    keys: str
    action: str
    endpoint_template: str

WINDOWS_SHORTCUTS: List[Shortcut] = [
    Shortcut("Alt + Tab", "Alternar janelas", "/api/keys?keys=alt,tab"),
    Shortcut("Win + D", "Mostrar desktop", "/api/keys?keys=win,d"),
    Shortcut("Alt + F4", "Fechar janela", "/api/keys?keys=alt,f4"),
    Shortcut("Ctrl + W", "Fechar aba/documento", "/api/keys?keys=ctrl,w"),
    Shortcut("Ctrl + Z", "Desfazer", "/api/keys?keys=ctrl,z"),
    Shortcut("Ctrl + Y", "Refazer", "/api/keys?keys=ctrl,y"),
    Shortcut("Ctrl + S", "Salvar", "/api/keys?keys=ctrl,s"),
    Shortcut("Ctrl + N", "Novo", "/api/keys?keys=ctrl,n"),
    Shortcut("Ctrl + O", "Abrir", "/api/keys?keys=ctrl,o"),
    Shortcut("Escape", "Cancelar/Fechar", "/api/keys?keys=escape"),
    Shortcut("Enter", "Confirmar", "/api/keys?keys=enter"),
    Shortcut("F5", "Atualizar", "/api/keys?keys=f5"),
]

# -------------------------------------------------------------------------
# 📊 TELEMETRIA E SINAIS DE SUCESSO (Reference: MASTER.md lines 410-430)
# -------------------------------------------------------------------------
class SignalWeight(Enum):
    HIGH = "High"
    MED = "Med"
    LOW = "Low"

class TelemetrySignal(NamedTuple):
    signal: str
    weight: SignalWeight
    meaning: str
    detection_method: str

TELEMETRY_SIGNALS: List[TelemetrySignal] = [
    TelemetrySignal("Title Modification", SignalWeight.HIGH, "Documento alterado", "* no window_title"),
    TelemetrySignal("Canvas UI Change", SignalWeight.HIGH, "Desenho realizado", "Diferença de pixels no annotated_path"),
    TelemetrySignal("Process Load", SignalWeight.MED, "App iniciou", "CPU/Memory spike + window list"),
    TelemetrySignal("Wait Cursor", SignalWeight.LOW, "App ocupado", "Mouse cursor icon change"),
    TelemetrySignal("New Dialog", SignalWeight.HIGH, "Interrupção", "Nova janela modal detectada"),
]

# -------------------------------------------------------------------------
# 🌐 NAVEGADOR VS DESKTOP (Reference: MASTER.md lines 730-738)
# -------------------------------------------------------------------------
class ContextType(Enum):
    NATIVE_APP = "NATIVE_APP"
    WEB_BROWSER = "WEB_BROWSER"

CONTEXT_RULES: Dict[ContextType, str] = {
    ContextType.NATIVE_APP: "/api/hybrid-vision/desktop",
    ContextType.WEB_BROWSER: "/api/hybrid-vision/web",
}
