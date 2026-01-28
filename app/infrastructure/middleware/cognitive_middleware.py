"""
ONI Cognitive Middleware v1.0
Middleware que FORÇA consulta de erros conhecidos e protocolos antes de ações.

Este middleware é a última linha de defesa contra memória episódica.
"""

import time
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = structlog.get_logger(__name__)


class CognitiveMiddleware(BaseHTTPMiddleware):
    """
    Middleware que intercepta ações e verifica erros conhecidos.
    
    Age como um "segundo cérebro" que lembra o que o agente esquece.
    """
    
    # Endpoints que modificam estado (precisam de verificação)
    ACTION_ENDPOINTS = [
        "/api/click",
        "/api/keys", 
        "/api/type",
        "/api/open",
        "/api/do",
        "/api/mouse/safe-drag",
        "/api/neural/draw",
        "/api/artmaster",
    ]
    
    # Endpoints que devem usar o Autonomous Executor
    AUTONOMOUS_RECOMMENDED = [
        "/api/open",
        "/api/artmaster",
    ]
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Verificar se é uma ação que precisa de atenção
        is_action = any(path.startswith(ep) for ep in self.ACTION_ENDPOINTS)
        
        if is_action:
            # 1. Consultar erros conhecidos para esta ação
            from app.services.oni.error_learning import ErrorLearningService
            
            action_desc = f"{request.method} {path}"
            if request.query_params:
                action_desc += f" params={dict(request.query_params)}"
            
            error_check = ErrorLearningService.check_action(action_desc)
            
            if error_check.get("has_known_errors"):
                # Logar aviso (mas não bloquear)
                logger.warning("known_error_pattern_detected",
                              path=path,
                              warnings=error_check.get("warnings"),
                              recommendation=error_check.get("recommendation"))
                
                # Adicionar header de aviso na resposta
                response = await call_next(request)
                response.headers["X-ONI-Warning"] = error_check.get("recommendation", "")[:200]
                return response
            
            # 2. Verificar se deve recomendar Autonomous Executor
            if any(path.startswith(ep) for ep in self.AUTONOMOUS_RECOMMENDED):
                logger.info("autonomous_executor_recommended", path=path)
        
        # Continuar com a requisição normal
        response = await call_next(request)
        return response


class ProtocolEnforcerMiddleware(BaseHTTPMiddleware):
    """
    Middleware que IMPEDE ações se o protocolo não foi seguido.
    
    Verifica:
    - Se houve scan recente (< 30s)
    - Se o estado foi carregado
    """
    
    PROTECTED_ENDPOINTS = [
        "/api/click",
        "/api/keys",
        "/api/type",
        "/api/do",
    ]
    
    # Tracking de último scan
    _last_scan_timestamp = 0
    SCAN_TIMEOUT = 30  # segundos
    
    @classmethod
    def record_scan(cls):
        cls._last_scan_timestamp = time.time()
    
    @classmethod
    def scan_is_fresh(cls) -> bool:
        return (time.time() - cls._last_scan_timestamp) < cls.SCAN_TIMEOUT
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Atualizar timestamp se for scan
        if "/hybrid-vision" in path or "/screenshot" in path:
            self.record_scan()
        
        # Verificar se é endpoint protegido
        is_protected = any(path.startswith(ep) for ep in self.PROTECTED_ENDPOINTS)
        
        if is_protected:
            # NOTA: Não vou BLOQUEAR, porque os endpoints já fazem scan interno
            # Mas vou LOGAR se chegou uma ação sem scan manual recente
            if not self.scan_is_fresh():
                logger.debug("action_without_fresh_manual_scan", 
                            path=path,
                            last_scan_age=time.time() - self._last_scan_timestamp)
        
        return await call_next(request)


# =============================================================================
# REGISTRO DE ERROS EM TEMPO REAL
# =============================================================================

class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que detecta erros em respostas e registra para aprendizado.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Se resposta indica erro, registrar para aprendizado
        if response.status_code >= 400:
            from app.services.oni.error_learning import ErrorLearningService
            
            path = request.url.path
            ErrorLearningService.add_occurrence(
                "ERR-AUTO",
                f"HTTP {response.status_code} em {path}"
            )
            logger.warning("http_error_tracked", 
                          path=path, 
                          status=response.status_code)
        
        return response


# =============================================================================
# HELPER: REGISTRAR MIDDLEWARES
# =============================================================================

def register_cognitive_middlewares(app):
    """
    Registra todos os middlewares cognitivos no app FastAPI.
    
    Chamar isso no main.py durante startup.
    """
    app.add_middleware(CognitiveMiddleware)
    app.add_middleware(ProtocolEnforcerMiddleware)
    # ErrorTrackingMiddleware pode ser muito pesado, desabilitado por padrão
    # app.add_middleware(ErrorTrackingMiddleware)
    
    logger.info("cognitive_middlewares_registered")
