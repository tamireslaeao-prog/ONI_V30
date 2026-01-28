"""
ONI Error Learning Service v1.0
Sistema de aprendizado de erros para prevenção.

Consulta erros conhecidos ANTES de cada ação e registra novos erros.
"""

import os
import re
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class KnownError:
    """Representa um erro conhecido."""
    id: str
    category: str
    name: str
    pattern: str
    symptom: str
    cause: str
    solution: str
    occurrences: List[str]


class ErrorLearningService:
    """
    Serviço de aprendizado de erros.
    Consulta e registra erros para prevenção.
    """
    
    ERRORS_FILE = "memo/MEUS_ERROS.md"
    
    # Erros conhecidos em memória (carregados do arquivo)
    _known_errors: Dict[str, KnownError] = {
        "ERR-001": KnownError(
            id="ERR-001",
            category="CONFIRMAÇÃO",
            name="Digitar sem Enter",
            pattern="digitar|type|texto|busca|search|campo|input|field",
            symptom="Ação não executada após digitação",
            cause="Assumir que digitar = executar",
            solution="SEMPRE enviar Enter após digitar em campos de entrada",
            occurrences=[]
        ),
        "ERR-002": KnownError(
            id="ERR-002",
            category="NAVEGAÇÃO",
            name="Clicar em elemento errado",
            pattern="click|clicar|coordenada|position",
            symptom="Clica em elemento diferente do desejado",
            cause="Coordenadas estimadas sem verificação",
            solution="Verificar posição via OCR antes de clicar",
            occurrences=[]
        ),
        "ERR-003": KnownError(
            id="ERR-003",
            category="MENU",
            name="Menu Windows 11 simplificado",
            pattern="menu|contexto|right.click|direito|winrar|7zip|compress|extractir|comprim",
            symptom="Apps não aparecem no menu de contexto",
            cause="Windows 11 tem menu simplificado",
            solution="Usar Shift+F10 para menu clássico completo",
            occurrences=[]
        ),
        "ERR-004": KnownError(
            id="ERR-004",
            category="VERIFICAÇÃO",
            name="Executar sem verificar resultado",
            pattern="next|próximo|continuar|executar|múltiplas|sequência",
            symptom="Próxima ação falha porque anterior não completou",
            cause="Não seguir ciclo VER→PENSAR→AGIR→VERIFICAR",
            solution="Screenshot + view_file + análise ANTES e DEPOIS de CADA ação",
            occurrences=[]
        ),
        "ERR-005": KnownError(
            id="ERR-005",
            category="COMANDOS",
            name="Comandos longos no Run Dialog",
            pattern="win.r|run|executar.*programa|path.*longo|winrar.*command",
            symptom="Windows não encontra arquivo ou programa",
            cause="Run Dialog tem limitações com paths longos",
            solution="NÃO usar Win+R para comandos complexos. Usar PowerShell direto ou automação visual",
            occurrences=[]
        ),
        "ERR-006": KnownError(
            id="ERR-006",
            category="PROTOCOLO",
            name="Ignorar protocolo estabelecido",
            pattern="automação|ação|executar|fazer|realizar",
            symptom="Erros que as regras deveriam prevenir acontecem",
            cause="Pressa, otimização prematura",
            solution="SEMPRE seguir ciclo: Screenshot→view_file→análise→ação→Screenshot→view_file→confirmar",
            occurrences=[]
        ),
        "ERR-007": KnownError(
            id="ERR-007",
            category="VISÃO",
            name="Confiar em metadados ao invés de visão real",
            pattern="active-window|janela|window|tela|screen|ver|olhar",
            symptom="Ações baseadas em dados incorretos ou desatualizados",
            cause="Screenshot capturado mas NÃO visualizado com view_file",
            solution="OBRIGATÓRIO: screenshot + view_file('C:/temp/oni_screenshot.png') + análise visual escrita",
            occurrences=[]
        ),
        "ERR-008": KnownError(
            id="ERR-008",
            category="ANÁLISE_FALSA",
            name="Escrever análise visual SEM OLHAR a imagem",
            pattern="análise|analysis|vejo|see|imagem|image|screenshot|visual",
            symptom="Análise não corresponde ao que está na imagem",
            cause="Preguiça mental, pressa, confiar na memória",
            solution="Após view_file: descrever LITERALMENTE o que vê. PROIBIDO inventar!",
            occurrences=[]
        ),
        "ERR-009": KnownError(
            id="ERR-009",
            category="BUSCA",
            name="Ctrl+F não foca busca no Explorer",
            pattern="busca|search|ctrl.f|explorer|arquivo|file|pesquisar|find",
            symptom="Texto digitado não aparece no campo de busca",
            cause="Explorer do Windows não responde bem a Ctrl+F",
            solution="USAR Win+digitação! Depois navegar até 'Abrir local do arquivo' com setas",
            occurrences=[]
        ),
        "ERR-010": KnownError(
            id="ERR-010",
            category="INFRAESTRUTURA",
            name="Porta Errada do Servidor",
            pattern="porta|port|5173|3000|5000|connection|refused|timeout",
            symptom="Conexão recusada ou timeout",
            cause="Usar porta errada ao invés de 8000",
            solution="Servidor ONI SEMPRE roda na porta 8000",
            occurrences=[]
        ),
        "ERR-011": KnownError(
            id="ERR-011",
            category="INFRAESTRUTURA",
            name="Script Errado para Iniciar",
            pattern="main.py|app.py|iniciar|start|servidor|server",
            symptom="Servidor não inicia ou inicia errado",
            cause="Usar script errado para iniciar",
            solution="Usar run.bat ou run.py para iniciar o servidor",
            occurrences=[]
        ),
        "ERR-012": KnownError(
            id="ERR-012",
            category="INFRAESTRUTURA",
            name="Ignorar Bridges Existentes",
            pattern="bridge|adapter|módulo|module|reinventar|criar novo",
            symptom="Recria código que já existe",
            cause="Não consultar infraestrutura antes de implementar",
            solution="Chamar /api/autonomous/discover ANTES de qualquer tarefa",
            occurrences=[]
        ),
        "ERR-013": KnownError(
            id="ERR-013",
            category="DIÁLOGO",
            name="Diálogo não fechou",
            pattern="diálogo|dialog|modal|popup|salvar|save|abrir|open",
            symptom="Diálogo permanece aberto após Enter",
            cause="Não verificar se diálogo fechou após confirmação",
            solution="Fazer Hybrid Vision scan após Enter para confirmar fechamento",
            occurrences=[]
        ),
    }
    
    @classmethod
    def check_action(cls, action_description: str) -> Dict[str, Any]:
        """
        Verifica se uma ação tem erros conhecidos associados.
        DEVE ser chamado ANTES de executar a ação.
        
        Returns:
            Dict com warnings e soluções preventivas
        """
        action_lower = action_description.lower()
        warnings = []
        solutions = []
        
        for error_id, error in cls._known_errors.items():
            # Verificar se padrão do erro casa com a ação
            if re.search(error.pattern, action_lower, re.IGNORECASE):
                warnings.append({
                    "id": error.id,
                    "category": error.category,
                    "name": error.name,
                    "risk": error.symptom
                })
                solutions.append({
                    "id": error.id,
                    "solution": error.solution
                })
        
        if warnings:
            logger.warning("known_errors_found", 
                          action=action_description[:50],
                          errors=[w["id"] for w in warnings])
        
        return {
            "action": action_description,
            "has_known_errors": len(warnings) > 0,
            "warnings": warnings,
            "preventive_solutions": solutions,
            "recommendation": cls._get_recommendation(solutions)
        }
    
    @classmethod
    def _get_recommendation(cls, solutions: List[Dict]) -> str:
        """Gera recomendação combinada."""
        if not solutions:
            return "Nenhum erro conhecido. Prossiga com cuidado."
        
        recs = [s["solution"] for s in solutions]
        return " | ".join(recs)
    
    @classmethod
    def register_error(
        cls,
        category: str,
        name: str,
        pattern: str,
        symptom: str,
        cause: str,
        solution: str,
        context: str = ""
    ) -> str:
        """
        Registra um novo erro no sistema.
        
        Returns:
            ID do erro criado
        """
        # Gerar novo ID
        existing_ids = [int(e.id.split("-")[1]) for e in cls._known_errors.values()]
        new_id = f"ERR-{max(existing_ids) + 1:03d}"
        
        new_error = KnownError(
            id=new_id,
            category=category.upper(),
            name=name,
            pattern=pattern,
            symptom=symptom,
            cause=cause,
            solution=solution,
            occurrences=[f"{datetime.now().isoformat()}: {context}"]
        )
        
        cls._known_errors[new_id] = new_error
        
        # Persist to disk immediately
        cls._persist_errors()
        
        logger.info("new_error_registered", id=new_id, name=name)
        
        return new_id
    
    @classmethod
    def _persist_errors(cls):
        """Salva erros conhecidos no arquivo Markdown."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(cls.ERRORS_FILE), exist_ok=True)
            
            with open(cls.ERRORS_FILE, 'w', encoding='utf-8') as f:
                f.write("# MEUS ERROS CONHECIDOS (Memória de Longo Prazo)\n\n")
                f.write("> **Autogerado pelo ONI ErrorLearningService**\n")
                f.write(f"> Atualizado em: {datetime.now().isoformat()}\n\n")
                
                for err_id, error in sorted(cls._known_errors.items()):
                    f.write(f"## {error.id}: {error.name}\n")
                    f.write(f"- **Categoria:** {error.category}\n")
                    f.write(f"- **Sintoma:** {error.symptom}\n")
                    f.write(f"- **Causa:** {error.cause}\n")
                    f.write(f"- **Solução:** {error.solution}\n")
                    f.write(f"- **Padrão de Detecção:** `{error.pattern}`\n")
                    f.write("- **Ocorrências:**\n")
                    for occ in error.occurrences[-5:]: # Keep last 5 to avoid bloat
                        f.write(f"  - {occ}\n")
                    f.write("\n---\n\n")
                    
        except Exception as e:
            logger.error("persist_errors_failed", error=str(e))
    
    @classmethod
    def add_occurrence(cls, error_id: str, context: str):
        """Adiciona nova ocorrência a um erro existente."""
        if error_id in cls._known_errors:
            cls._known_errors[error_id].occurrences.append(
                f"{datetime.now().isoformat()}: {context}"
            )
            # Re-persist to update occurrence count
            cls._persist_errors()
            logger.info("error_occurrence_added", id=error_id)
    
    @classmethod
    def list_errors(cls) -> List[Dict]:
        """Lista todos os erros conhecidos."""
        return [
            {
                "id": e.id,
                "category": e.category,
                "name": e.name,
                "solution": e.solution,
                "occurrences_count": len(e.occurrences)
            }
            for e in cls._known_errors.values()
        ]
    
    @classmethod
    def get_solution(cls, error_id: str) -> Optional[str]:
        """Retorna solução para um erro específico."""
        if error_id in cls._known_errors:
            return cls._known_errors[error_id].solution
        return None


# Regras específicas Windows
WINDOWS_RULES = {
    "input_fields": {
        "rule": "Após digitar em QUALQUER campo, SEMPRE enviar Enter ou verificar",
        "applies_to": ["busca", "search", "barra de endereço", "formulário", "diálogo"]
    },
    "context_menu_w11": {
        "rule": "Usar Shift+F10 para menu clássico completo no Windows 11",
        "applies_to": ["menu contexto", "clique direito", "winrar", "7zip", "compactar"]
    },
    "verify_action": {
        "rule": "Capturar screenshot e analisar após CADA ação",
        "applies_to": ["qualquer ação"]
    }
}
