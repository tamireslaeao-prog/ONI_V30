"""
ONI Autonomous Executor v1.0
Sistema de Execução Autônoma - Elimina Dependência de Memória Episódica.

PRINCÍPIO FUNDAMENTAL:
O protocolo VER→PENSAR→AGIR→VERIFICAR é INTERNO ao sistema.
O agente NÃO pode "esquecer" de seguir o protocolo porque ele é AUTOMÁTICO.

Autor: ONI System
Data: 2026-01-14
"""

import asyncio
import time
import json
import os
import hashlib
from typing import Optional, Dict, List, Any, Callable
import structlog

from .autonomous_types import ExecutionPhase, SuccessCriteria, ExecutionState, ActionResult
from .infrastructure_discovery import InfrastructureDiscovery

logger = structlog.get_logger(__name__)


class AutonomousExecutor:
    """
    Executor Autônomo - O coração do sistema anti-memória-episódica.
    
    Cada ação passa automaticamente por:
    1. PRE-SCAN (Hybrid Vision)
    2. EXECUTE (Ação real)
    3. POST-SCAN (Hybrid Vision)
    4. VERIFY (Critério de sucesso)
    5. RECOVER (Se falhar, tenta corrigir)
    
    O agente NÃO PODE pular nenhuma etapa porque são INTERNAS.
    """
    
    STATE_FILE = "temp/autonomous_state.json"
    MAX_RECOVERIES = 3
    SCAN_TIMEOUT_SECONDS = 30
    
    _current_state: Optional[ExecutionState] = None
    
    @classmethod
    def _load_state(cls) -> Optional[ExecutionState]:
        """Carrega estado do disco."""
        try:
            if os.path.exists(cls.STATE_FILE):
                with open(cls.STATE_FILE, 'r') as f:
                    data = json.load(f)
                    return ExecutionState(
                        task_id=data.get("task_id", "unknown"),
                        current_phase=ExecutionPhase(data.get("current_phase", "pre_scan")),
                        last_scan_timestamp=data.get("last_scan_timestamp", 0),
                        last_scan_path=data.get("last_scan_path", ""),
                        last_window_title=data.get("last_window_title", ""),
                        last_screen_hash=data.get("last_screen_hash", ""),
                        actions_executed=data.get("actions_executed", 0),
                        recoveries_attempted=data.get("recoveries_attempted", 0),
                        started_at=data.get("started_at", time.time())
                    )
        except Exception as e:
            logger.error("load_state_failed", error=str(e))
        return None
    
    @classmethod
    def _save_state(cls):
        """Salva estado no disco."""
        if cls._current_state:
            try:
                os.makedirs(os.path.dirname(cls.STATE_FILE), exist_ok=True)
                with open(cls.STATE_FILE, 'w') as f:
                    json.dump(cls._current_state.to_dict(), f, indent=2)
            except Exception as e:
                logger.error("save_state_failed", error=str(e))
    
    @classmethod
    async def _do_scan(cls) -> Dict[str, Any]:
        """
        Executa scan via Hybrid Vision.
        SEMPRE chamado internamente - impossível esquecer.
        """
        import aiohttp
        
        timestamp = int(time.time() * 1000)
        url = f"http://localhost:8000/api/hybrid-vision/desktop?nocache=auto_{timestamp}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Atualizar estado
                        if cls._current_state:
                            cls._current_state.last_scan_timestamp = time.time()
                            cls._current_state.last_scan_path = data.get("annotated_path", "")
                            cls._current_state.last_window_title = data.get("window_title", "")
                            # Calcular hash da tela para comparação
                            screen_data = json.dumps(data.get("elements", []), sort_keys=True)
                            cls._current_state.last_screen_hash = hashlib.md5(screen_data.encode()).hexdigest()
                            cls._save_state()
                        
                        logger.info("autonomous_scan_complete", 
                                   window=data.get("window_title"),
                                   elements=len(data.get("elements", [])))
                        return data
                    else:
                        logger.error("scan_failed", status=response.status)
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error("scan_exception", error=str(e))
            return {"error": str(e)}
    
    @classmethod
    async def _verify_success(
        cls, 
        criteria: SuccessCriteria, 
        criteria_value: Any,
        pre_scan: Dict,
        post_scan: Dict
    ) -> bool:
        """
        Verifica se a ação foi bem sucedida.
        """
        try:
            if criteria == SuccessCriteria.WINDOW_TITLE_CONTAINS:
                return criteria_value.lower() in post_scan.get("window_title", "").lower()
            
            elif criteria == SuccessCriteria.WINDOW_TITLE_CHANGED:
                return pre_scan.get("window_title") != post_scan.get("window_title")
            
            elif criteria == SuccessCriteria.SCREEN_CHANGED:
                pre_hash = hashlib.md5(json.dumps(pre_scan.get("elements", []), sort_keys=True).encode()).hexdigest()
                post_hash = hashlib.md5(json.dumps(post_scan.get("elements", []), sort_keys=True).encode()).hexdigest()
                return pre_hash != post_hash
            
            elif criteria == SuccessCriteria.FILE_EXISTS:
                return os.path.exists(criteria_value)
            
            elif criteria == SuccessCriteria.FILES_COUNT_GTE:
                path, count = criteria_value.split("|")
                if os.path.exists(path):
                    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
                    return len(files) >= int(count)
                return False
            
            elif criteria == SuccessCriteria.NO_ERROR_POPUP:
                window_title = post_scan.get("window_title", "").lower()
                error_patterns = ["error", "erro", "warning", "aviso", "failed", "falhou"]
                return not any(p in window_title for p in error_patterns)
            
            elif criteria == SuccessCriteria.ELEMENT_VISIBLE:
                elements = post_scan.get("elements", [])
                for el in elements:
                    if criteria_value.lower() in str(el).lower():
                        return True
                return False
            
            else:
                # Custom ou desconhecido - assume sucesso se não houver erro
                return "error" not in post_scan
                
        except Exception as e:
            logger.error("verify_failed", error=str(e))
            return False
    
    @classmethod
    async def _attempt_recovery(cls, error_context: Dict) -> Dict[str, Any]:
        """
        Tenta recuperação automática.
        Usa o ErrorRecoveryService existente.
        """
        from app.services.oni.error_recovery import ErrorRecoveryService
        
        cls._current_state.recoveries_attempted += 1
        cls._save_state()
        
        result = await ErrorRecoveryService.check_and_recover(
            action_name=error_context.get("action", "unknown"),
            expected_window=error_context.get("expected_window"),
            actual_window=error_context.get("actual_window"),
            screen_hash_before=error_context.get("pre_hash"),
            screen_hash_after=error_context.get("post_hash"),
            timeout_occurred=error_context.get("timeout", False)
        )
        
        return result
    
    @classmethod
    async def execute(
        cls,
        task_id: str,
        action_callable: Callable,
        action_params: Dict = None,
        success_criteria: SuccessCriteria = SuccessCriteria.SCREEN_CHANGED,
        criteria_value: Any = None,
        expected_window: str = None
    ) -> ActionResult:
        """
        Executa uma ação de forma TOTALMENTE AUTÔNOMA.
        
        O protocolo VER→PENSAR→AGIR→VERIFICAR é INTERNO.
        O agente não pode esquecer nenhuma etapa.
        
        Args:
            task_id: Identificador da tarefa
            action_callable: Função async que executa a ação real
            action_params: Parâmetros para a função
            success_criteria: Critério para verificar sucesso
            criteria_value: Valor para comparar no critério
            expected_window: Título esperado da janela (opcional)
        
        Returns:
            ActionResult com todos os detalhes
        """
        start_time = time.time()
        action_params = action_params or {}
        
        # Inicializar estado
        cls._current_state = ExecutionState(
            task_id=task_id,
            current_phase=ExecutionPhase.PRE_SCAN
        )
        cls._save_state()
        
        result = ActionResult(
            success=False,
            phase=ExecutionPhase.PRE_SCAN
        )
        
        try:
            # ═══════════════════════════════════════════════════════════
            # FASE 1: PRE-SCAN (AUTOMÁTICO - IMPOSSÍVEL ESQUECER)
            # ═══════════════════════════════════════════════════════════
            logger.info("autonomous_phase", phase="PRE_SCAN", task=task_id)
            cls._current_state.current_phase = ExecutionPhase.PRE_SCAN
            cls._save_state()
            
            pre_scan = await cls._do_scan()
            result.pre_scan_path = pre_scan.get("annotated_path", "")
            
            if "error" in pre_scan:
                result.error = f"Pre-scan failed: {pre_scan['error']}"
                return result
            
            pre_window = pre_scan.get("window_title", "")
            pre_hash = cls._current_state.last_screen_hash
            
            # ═══════════════════════════════════════════════════════════
            # FASE 2: EXECUTE (AÇÃO REAL)
            # ═══════════════════════════════════════════════════════════
            logger.info("autonomous_phase", phase="EXECUTE", task=task_id)
            cls._current_state.current_phase = ExecutionPhase.EXECUTE
            cls._save_state()
            
            try:
                action_output = await action_callable(**action_params)
                result.action_output = action_output
                cls._current_state.actions_executed += 1
            except Exception as e:
                result.error = f"Action failed: {str(e)}"
                result.phase = ExecutionPhase.EXECUTE
                return result
            
            # Pequeno delay para UI atualizar
            await asyncio.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════
            # FASE 3: POST-SCAN (AUTOMÁTICO - IMPOSSÍVEL ESQUECER)
            # ═══════════════════════════════════════════════════════════
            logger.info("autonomous_phase", phase="POST_SCAN", task=task_id)
            cls._current_state.current_phase = ExecutionPhase.POST_SCAN
            cls._save_state()
            
            post_scan = await cls._do_scan()
            result.post_scan_path = post_scan.get("annotated_path", "")
            
            if "error" in post_scan:
                result.error = f"Post-scan failed: {post_scan['error']}"
                result.phase = ExecutionPhase.POST_SCAN
                return result
            
            post_window = post_scan.get("window_title", "")
            post_hash = cls._current_state.last_screen_hash
            
            # ═══════════════════════════════════════════════════════════
            # FASE 4: VERIFY (AUTOMÁTICO - IMPOSSÍVEL ESQUECER)
            # ═══════════════════════════════════════════════════════════
            logger.info("autonomous_phase", phase="VERIFY", task=task_id)
            cls._current_state.current_phase = ExecutionPhase.VERIFY
            cls._save_state()
            
            success = await cls._verify_success(
                criteria=success_criteria,
                criteria_value=criteria_value,
                pre_scan=pre_scan,
                post_scan=post_scan
            )
            
            if success:
                result.success = True
                result.phase = ExecutionPhase.COMPLETE
                cls._current_state.current_phase = ExecutionPhase.COMPLETE
                cls._save_state()
                
                logger.info("autonomous_success", task=task_id, 
                           criteria=success_criteria.value)
                
            else:
                # ═══════════════════════════════════════════════════════
                # FASE 5: RECOVER (AUTOMÁTICO SE FALHAR)
                # ═══════════════════════════════════════════════════════
                logger.warning("autonomous_verify_failed", task=task_id,
                              criteria=success_criteria.value)
                
                if cls._current_state.recoveries_attempted < cls.MAX_RECOVERIES:
                    logger.info("autonomous_phase", phase="RECOVER", task=task_id)
                    cls._current_state.current_phase = ExecutionPhase.RECOVER
                    cls._save_state()
                    
                    recovery_result = await cls._attempt_recovery({
                        "action": task_id,
                        "expected_window": expected_window or pre_window,
                        "actual_window": post_window,
                        "pre_hash": pre_hash,
                        "post_hash": post_hash
                    })
                    
                    if recovery_result.get("recovery_success"):
                        result.recovery_applied = recovery_result.get("strategy_used", "unknown")
                        
                        # Retry após recovery
                        logger.info("autonomous_retry_after_recovery", task=task_id)
                        retry_result = await cls.execute(
                            task_id=f"{task_id}_retry",
                            action_callable=action_callable,
                            action_params=action_params,
                            success_criteria=success_criteria,
                            criteria_value=criteria_value,
                            expected_window=expected_window
                        )
                        return retry_result
                    else:
                        result.error = "Recovery failed"
                        result.phase = ExecutionPhase.RECOVER
                else:
                    result.error = f"Max recoveries ({cls.MAX_RECOVERIES}) exceeded"
                    result.phase = ExecutionPhase.RECOVER
            
        except Exception as e:
            result.error = str(e)
            logger.error("autonomous_exception", error=str(e), task=task_id)
        
        finally:
            result.execution_time_ms = (time.time() - start_time) * 1000
            cls._save_state()
        
        return result


    @classmethod
    async def execute_simple(
        cls,
        task_id: str,
        api_endpoint: str,
        api_params: Dict = None,
        success_criteria: SuccessCriteria = SuccessCriteria.SCREEN_CHANGED,
        criteria_value: Any = None
    ) -> ActionResult:
        """
        Versão simplificada que executa uma chamada HTTP à API do ONI.
        """
        import aiohttp
        
        async def call_api(**params):
            url = f"http://localhost:8000{api_endpoint}"
            if params:
                query = "&".join(f"{k}={v}" for k, v in params.items())
                url = f"{url}?{query}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    return await response.json()
        
        return await cls.execute(
            task_id=task_id,
            action_callable=call_api,
            action_params=api_params or {},
            success_criteria=success_criteria,
            criteria_value=criteria_value
        )


    @classmethod
    def get_state(cls) -> Optional[Dict]:
        """Retorna estado atual para debug/monitoramento."""
        if cls._current_state:
            return cls._current_state.to_dict()
        state = cls._load_state()
        if state:
            return state.to_dict()
        return None
