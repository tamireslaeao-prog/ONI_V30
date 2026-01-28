"""
ONI Autonomous Error Recovery Service v1.0
Sistema de recuperação automática de erros.

Detecta, classifica e corrige problemas automaticamente.
"""

import asyncio
import time
import hashlib
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import sqlite3
import structlog

logger = structlog.get_logger(__name__)


class ErrorClass(str, Enum):
    """Classificação de erros."""
    DIALOG_POPUP = "dialog_popup"       # Popup inesperado apareceu
    APP_FROZEN = "app_frozen"           # App não responde
    APP_CRASHED = "app_crashed"         # App fechou inesperadamente
    ACTION_FAILED = "action_failed"     # Ação não teve efeito
    PERMISSION_DENIED = "permission"    # Sem permissão
    RESOURCE_MISSING = "resource"       # Arquivo/recurso não encontrado
    TIMEOUT = "timeout"                 # Tempo limite excedido
    UNKNOWN = "unknown"                 # Erro desconhecido


class RecoveryStrategy(str, Enum):
    """Estratégias de recuperação."""
    DISMISS_POPUP = "dismiss_popup"     # Pressiona Esc ou Enter
    CLICK_AWAY = "click_away"           # Clica fora do popup
    ROLLBACK = "rollback"               # Ctrl+Z e tenta novamente
    WAIT_RETRY = "wait_retry"           # Espera e tenta de novo
    RESTART_APP = "restart_app"         # Fecha e reabre o app
    ESCALATE = "escalate"               # Pede ajuda humana


@dataclass
class Checkpoint:
    """Estado salvo para possível rollback."""
    id: int
    timestamp: float
    action_name: str
    screen_hash: str
    window_title: str
    can_undo: bool = True


@dataclass
class AnomalyReport:
    """Relatório de anomalia detectada."""
    error_class: ErrorClass
    confidence: float
    details: Dict[str, Any]
    suggested_strategy: RecoveryStrategy
    timestamp: float = field(default_factory=time.time)


class AnomalyDetector:
    """
    Detecta anomalias comparando estados esperados vs reais.
    """
    
    # Padrões de título que indicam popup/diálogo
    POPUP_PATTERNS = [
        "save", "salvar", "guardar",
        "confirm", "confirmar",
        "warning", "aviso",
        "error", "erro",
        "alert", "alerta",
        "do you want", "deseja",
        "are you sure", "tem certeza",
        "not responding", "não responde",
        "permission", "permissão",
        "access denied", "acesso negado",
    ]
    
    # Padrões de OCR que indicam problemas
    ERROR_OCR_PATTERNS = [
        "file not found", "arquivo não encontrado",
        "access denied", "acesso negado",
        "error", "erro",
        "failed", "falhou",
        "cannot", "não pode",
        "unable", "impossível",
    ]
    
    @classmethod
    async def detect(
        cls,
        expected_window: str,
        actual_window: str,
        screen_changed: bool,
        ocr_text: str = "",
        timeout_occurred: bool = False
    ) -> Optional[AnomalyReport]:
        """
        Detecta se há anomalia no estado atual.
        
        Returns:
            AnomalyReport se anomalia detectada, None se tudo ok
        """
        
        # 1. Verificar timeout
        if timeout_occurred:
            return AnomalyReport(
                error_class=ErrorClass.TIMEOUT,
                confidence=0.95,
                details={"expected": expected_window, "actual": actual_window},
                suggested_strategy=RecoveryStrategy.WAIT_RETRY
            )
        
        # 2. Verificar se app mudou inesperadamente (popup)
        if expected_window and actual_window:
            expected_lower = expected_window.lower()
            actual_lower = actual_window.lower()
            
            # Verificar padrões de popup
            for pattern in cls.POPUP_PATTERNS:
                if pattern in actual_lower and pattern not in expected_lower:
                    return AnomalyReport(
                        error_class=ErrorClass.DIALOG_POPUP,
                        confidence=0.85,
                        details={
                            "popup_title": actual_window,
                            "pattern_matched": pattern
                        },
                        suggested_strategy=RecoveryStrategy.DISMISS_POPUP
                    )
            
            # Verificar se app mudou completamente (crash)
            if expected_lower.split(" - ")[0] != actual_lower.split(" - ")[0]:
                if "not responding" in actual_lower:
                    return AnomalyReport(
                        error_class=ErrorClass.APP_FROZEN,
                        confidence=0.9,
                        details={"window": actual_window},
                        suggested_strategy=RecoveryStrategy.WAIT_RETRY
                    )
        
        # 3. Verificar se ação não teve efeito
        if not screen_changed:
            return AnomalyReport(
                error_class=ErrorClass.ACTION_FAILED,
                confidence=0.7,
                details={"reason": "screen_unchanged"},
                suggested_strategy=RecoveryStrategy.ROLLBACK
            )
        
        # 4. Verificar OCR para erros
        if ocr_text:
            ocr_lower = ocr_text.lower()
            for pattern in cls.ERROR_OCR_PATTERNS:
                if pattern in ocr_lower:
                    return AnomalyReport(
                        error_class=ErrorClass.PERMISSION_DENIED if "denied" in pattern or "permission" in pattern else ErrorClass.RESOURCE_MISSING,
                        confidence=0.75,
                        details={"ocr_match": pattern, "text": ocr_text[:200]},
                        suggested_strategy=RecoveryStrategy.ESCALATE
                    )
        
        # Nenhuma anomalia detectada
        return None


class CheckpointManager:
    """
    Gerencia checkpoints para rollback.
    """
    
    _checkpoints: deque = deque(maxlen=20)
    _counter: int = 0
    
    @classmethod
    def create_checkpoint(
        cls,
        action_name: str,
        screen_hash: str,
        window_title: str,
        can_undo: bool = True
    ) -> Checkpoint:
        """Cria um novo checkpoint."""
        cls._counter += 1
        checkpoint = Checkpoint(
            id=cls._counter,
            timestamp=time.time(),
            action_name=action_name,
            screen_hash=screen_hash,
            window_title=window_title,
            can_undo=can_undo
        )
        cls._checkpoints.append(checkpoint)
        logger.debug("checkpoint_created", id=checkpoint.id, action=action_name)
        return checkpoint
    
    @classmethod
    def get_last_checkpoint(cls) -> Optional[Checkpoint]:
        """Retorna o último checkpoint."""
        if cls._checkpoints:
            return cls._checkpoints[-1]
        return None
    
    @classmethod
    def get_safe_checkpoint(cls, steps_back: int = 1) -> Optional[Checkpoint]:
        """Retorna um checkpoint N passos atrás."""
        if len(cls._checkpoints) >= steps_back:
            return cls._checkpoints[-steps_back]
        return None
    
    @classmethod
    def clear_checkpoints(cls):
        """Limpa todos os checkpoints."""
        cls._checkpoints.clear()
        cls._counter = 0


class RecoveryExecutor:
    """
    Executa estratégias de recuperação.
    """
    
    @classmethod
    async def execute(
        cls,
        strategy: RecoveryStrategy,
        anomaly: AnomalyReport
    ) -> Dict[str, Any]:
        """
        Executa uma estratégia de recuperação.
        
        Returns:
            Dict com resultado da recuperação
        """
        import pyautogui
        
        logger.info("recovery_executing", 
                   strategy=strategy.value, 
                   error_class=anomaly.error_class.value)
        
        result = {
            "strategy": strategy.value,
            "success": False,
            "details": {}
        }
        
        try:
            if strategy == RecoveryStrategy.DISMISS_POPUP:
                # Tenta Esc primeiro, depois Enter
                pyautogui.press("escape")
                await asyncio.sleep(0.3)
                result["details"]["action"] = "pressed_escape"
                result["success"] = True
                
            elif strategy == RecoveryStrategy.CLICK_AWAY:
                # Clica no canto da tela
                pyautogui.click(10, 10)
                await asyncio.sleep(0.2)
                result["details"]["action"] = "clicked_corner"
                result["success"] = True
                
            elif strategy == RecoveryStrategy.ROLLBACK:
                # Ctrl+Z
                pyautogui.hotkey("ctrl", "z")
                await asyncio.sleep(0.3)
                result["details"]["action"] = "undo"
                result["success"] = True
                
            elif strategy == RecoveryStrategy.WAIT_RETRY:
                # Espera 2 segundos
                await asyncio.sleep(2.0)
                result["details"]["action"] = "waited_2s"
                result["success"] = True
                
            elif strategy == RecoveryStrategy.RESTART_APP:
                # Tenta reiniciar o aplicativo
                try:
                    import psutil
                    import subprocess
                    
                    # Tentar encontrar processo pela janela
                    window_title = anomaly.details.get("window", "")
                    restarted = False
                    
                    if window_title:
                        for proc in psutil.process_iter(['pid', 'name', 'exe']):
                            try:
                                if proc.info['name'] and proc.info['name'].lower() in window_title.lower():
                                    exe_path = proc.info['exe']
                                    proc.kill()
                                    await asyncio.sleep(2.0)
                                    
                                    if exe_path:
                                        subprocess.Popen(exe_path)
                                        restarted = True
                                        result["details"]["action"] = f"restarted_{proc.info['name']}"
                                    break
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                                
                    if not restarted:
                        result["details"]["action"] = "restart_failed_process_not_found"
                        result["success"] = False
                    else:
                        result["success"] = True
                        
                except ImportError:
                    # Fallback para taskkill se psutil não existir
                    result["details"]["action"] = "restart_failed_missing_psutil"
                    result["success"] = False
                except Exception as e:
                    result["details"]["error"] = str(e)
                    result["success"] = False
                
            elif strategy == RecoveryStrategy.ESCALATE:
                # Não pode fazer nada automaticamente
                result["details"]["action"] = "needs_human"
                result["details"]["message"] = "Este erro requer intervenção humana"
                result["success"] = False
            
            logger.info("recovery_completed", **result)
            return result
            
        except Exception as e:
            logger.error("recovery_failed", error=str(e))
            result["error"] = str(e)
            return result


class ErrorRecoveryService:
    """
    Serviço principal de recuperação de erros.
    Orquestra detecção, classificação e execução de recuperação.
    """
    
    DB_FILE = "oni_recovery_history.db"
    _retry_count: Dict[str, int] = {}
    MAX_RETRIES = 3
    
    @classmethod
    def _init_db(cls):
        """Inicializa banco de histórico."""
        try:
            conn = sqlite3.connect(cls.DB_FILE)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recovery_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    error_class TEXT,
                    strategy_used TEXT,
                    success BOOLEAN,
                    app_name TEXT,
                    context TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("recovery_db_init_failed", error=str(e))
    
    @classmethod
    async def check_and_recover(
        cls,
        action_name: str,
        expected_window: Optional[str] = None,
        actual_window: Optional[str] = None,
        screen_hash_before: Optional[str] = None,
        screen_hash_after: Optional[str] = None,
        ocr_text: str = "",
        timeout_occurred: bool = False
    ) -> Dict[str, Any]:
        """
        Verifica se há anomalia e tenta recuperar.
        INTEGRAÇÃO REFLEX ENGINE V1.0
        """
        
        # 0. REFLEX ARC (Fast Path)
        # Tentar lembrar se já resolvemos isso antes
        from app.services.oni.cortex import CortexService
        
        # Determinar assinatura do erro (Simplificado)
        error_sig = "generic_anomaly"
        if timeout_occurred: error_sig = "timeout"
        elif ocr_text: error_sig = ocr_text[:50] # Primeiros 50 chars do erro OCR
        
        reflex = CortexService.recall_reflex(error_sig, action_name)
        if reflex and reflex['is_reflex']:
            logger.info("reflex_takeover", strategy=reflex['strategy'])
            # Executar Reflexo (Bypass Detection)
            try:
                # Mapear string do reflexo para Enum
                reflex_strategy = RecoveryStrategy(reflex['strategy'])
                # Forçar esta estratégia na detecção se possível, ou retornar diretamente
                # Como anomalia ainda não foi detectada, não temos objeto AnomalyReport
                # Vamos deixar passar para o REFLEX OVERRIDE abaixo
            except ValueError:
                logger.warning("invalid_reflex_strategy", strategy=reflex['strategy'])
        
        # Determinar se tela mudou
        screen_changed = (screen_hash_before != screen_hash_after) if screen_hash_before and screen_hash_after else True
        
        # Detectar anomalia
        anomaly = await AnomalyDetector.detect(
            expected_window=expected_window or "",
            actual_window=actual_window or "",
            screen_changed=screen_changed,
            ocr_text=ocr_text,
            timeout_occurred=timeout_occurred
        )
        
        if not anomaly:
            # Sucesso! Gravar na memória episódica
            CortexService.record_episode(action_name, "check", "SUCCESS")
            return {"anomaly_detected": False, "status": "ok"}
            
        # 1.5 REFLEX OVERRIDE
        # Se o Cortex sugeriu algo para este tipo de erro (class), usamos
        reflex_strat = CortexService.recall_reflex(anomaly.error_class.value, action_name)
        if reflex_strat:
             # Converter string para Enum (Naive)
             try:
                 override = RecoveryStrategy(reflex_strat['strategy'])
                 anomaly.suggested_strategy = override
                 logger.info("reflex_strategy_applied", strategy=override)
             except Exception:
                 pass
        
        # Verificar limite de retries
        retry_key = f"{action_name}_{anomaly.error_class.value}"
        cls._retry_count[retry_key] = cls._retry_count.get(retry_key, 0) + 1
        
        if cls._retry_count[retry_key] > cls.MAX_RETRIES:
            CortexService.record_episode(action_name, "recover", "FAIL_MAX_RETRIES", anomaly.error_class.value)
            logger.warning("max_retries_exceeded", action=action_name)
            return {
                "anomaly_detected": True,
                "error_class": anomaly.error_class.value,
                "status": "max_retries_exceeded",
                "message": f"Excedido limite de {cls.MAX_RETRIES} tentativas"
            }
        
        # Executar recuperação
        recovery_result = await RecoveryExecutor.execute(
            anomaly.suggested_strategy,
            anomaly
        )
        
        # 2. LEARNING LOOP
        # Ensinar o cérebro
        CortexService.memorize_outcome(
            error_signature=anomaly.error_class.value,
            app_name=action_name,
            strategy=recovery_result["strategy"],
            success=recovery_result["success"]
        )
        
        # Registrar no histórico legado (Backup)
        cls._record_recovery(anomaly, recovery_result)
        
        # Limpar retry count se sucesso
        if recovery_result["success"]:
            cls._retry_count[retry_key] = 0
            CortexService.record_episode(action_name, "recover", "SUCCESS", anomaly.error_class.value)
        
        return {
            "anomaly_detected": True,
            "error_class": anomaly.error_class.value,
            "confidence": anomaly.confidence,
            "recovery_attempted": True,
            "recovery_success": recovery_result["success"],
            "strategy_used": recovery_result["strategy"],
            "details": recovery_result.get("details", {}),
            "retry_count": cls._retry_count.get(retry_key, 0)
        }
    
    @classmethod
    def _record_recovery(cls, anomaly: AnomalyReport, result: Dict):
        """Registra recuperação no histórico."""
        try:
            cls._init_db()
            conn = sqlite3.connect(cls.DB_FILE)
            conn.execute("""
                INSERT INTO recovery_history 
                (timestamp, error_class, strategy_used, success, context)
                VALUES (?, ?, ?, ?, ?)
            """, (
                time.time(),
                anomaly.error_class.value,
                result["strategy"],
                result["success"],
                str(anomaly.details)
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("record_recovery_failed", error=str(e))
    
    @classmethod
    def create_checkpoint(cls, action_name: str, screen_hash: str, window_title: str):
        """Cria checkpoint antes de ação."""
        return CheckpointManager.create_checkpoint(
            action_name=action_name,
            screen_hash=screen_hash,
            window_title=window_title
        )
    
    @classmethod
    async def detect_anomaly(cls, actual_window_title: str) -> Optional[AnomalyReport]:
        """ Wrapper para detectar anomalias baseado apenas no título da janela atual. """
        return await AnomalyDetector.detect(
            expected_window="", # Não temos expectativa neste endpoint simples
            actual_window=actual_window_title,
            screen_changed=True # Assumimos mudança para não falhar check ACTION_FAILED
        )

    @classmethod
    async def attempt_recovery(cls, anomaly: AnomalyReport) -> Dict[str, Any]:
        """ Wrapper para tentar recuperação. """
        return await RecoveryExecutor.execute(anomaly.suggested_strategy, anomaly)
        
    @classmethod
    def reset_retries(cls, action_name: str = None):
        """Reseta contadores de retry."""
        if action_name:
            keys_to_remove = [k for k in cls._retry_count if k.startswith(action_name)]
            for k in keys_to_remove:
                del cls._retry_count[k]
        else:
            cls._retry_count.clear()
