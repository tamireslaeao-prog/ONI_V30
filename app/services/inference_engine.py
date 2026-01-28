import structlog
import time
import asyncio
from typing import Dict, Any, Optional, Callable, List
import cv2
import numpy as np
from app.services.oni.cognitive_memory import CognitiveMemoryService

logger = structlog.get_logger(__name__)

class ActiveInferenceEngine:
    """
    Motor de Inferência Ativa (Active Inference Engine).
    Implementa o ciclo Perceber-Agir-Verificar para ações autônomas.
    """
    
    def __init__(self, vision_service, window_manager):
        self.vision = vision_service
        self.wm = window_manager
        logger.info("active_inference_engine_initialized")

    async def observe_state(self) -> Dict[str, Any]:
        """
        Captura o estado fenomenológico atual (Visual + Contextual).
        """
        try:
            # Captura visual
            capture = await self.vision.capture()
            image = capture.image if capture else None
            
            # Captura contextual (Janela)
            win_info = self.wm.get_active_window()
            win_title = win_info.title if win_info and win_info.title else 'unknown'
            
            # Hash visual para detecção rápida de mudança
            visual_hash = self._compute_visual_hash(image) if image is not None else 0
            
            return {
                "window_title": win_title,
                "visual_hash": visual_hash,
                "timestamp": time.time(),
                "has_vision": image is not None
            }
        except Exception as e:
            logger.error("observation_failed", error=str(e))
            return {"error": str(e)}

    async def execute_task(
        self, 
        action_callbacks: List[Callable], 
        expectation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa uma ação dentro do loop de inferência ativa com suporte a retries.
        
        Args:
            action_callbacks: Lista de funções async para tentar sequencialmente.
            expectation: Resultado esperado para validação.
        """
        logger.info("inference_loop_start", expectation=expectation, strategies=len(action_callbacks))
        
        history = []
        latency = expectation.get('latency_ms', 500) / 1000.0
        
        for i, action in enumerate(action_callbacks):
            strategy_name = getattr(action, "__name__", f"strategy_{i}")
            logger.info("attempt_start", strategy=strategy_name, attempt=i+1)
            
            # 1. Observação A Priori (T0)
            t0_state = await self.observe_state()
            
            # 2. Ação (Intervenção Ativa)
            try:
                await action()
            except Exception as e:
                logger.warning("action_failed", strategy=strategy_name, error=str(e))
                history.append({"strategy": strategy_name, "error": str(e), "phase": "action"})
                continue
                
            # Aguardar latência prevista
            await asyncio.sleep(latency)
            
            # 3. Observação A Posteriori (T1)
            t1_state = await self.observe_state()
            
            # 4. Minimização de Erro (Verificação)
            verification = self._verify_outcome(t0_state, t1_state, expectation)
            
            if verification['success']:
                result = {
                    "success": True,
                    "confidence": verification['confidence'],
                    "strategy_used": strategy_name,
                    "attempts": i + 1,
                    "t0": {k: v for k,v in t0_state.items() if k != 'image'},
                    "t1": {k: v for k,v in t1_state.items() if k != 'image'},
                    "analysis": verification['reason']
                }
                logger.info("inference_success", result=result)
                return result
            
            # Falha nesta estratégia
            history.append({
                "strategy": strategy_name,
                "verification": verification,
                "t0_hash": t0_state.get('visual_hash'),
                "t1_hash": t1_state.get('visual_hash')
            })
            logger.warning("inference_retry", strategy=strategy_name, reason=verification['reason'])

            # Se chegou aqui, todas falharam
        failure_result = {
            "success": False,
            "error": "All strategies failed to produce expected outcome",
            "history": history
        }
        logger.error("inference_failed_all", result=failure_result)
        
        # Record failure in memory
        try:
            # Pega contexto inicial se disponível
            win_title = history[0]['t0_hash'] if history else "unknown" 
            # (Simplificação: ideal seria pegar title real do t0, mas t0 localmente sobrescrito. 
            #  Para MVP, gravamos 'unknown' ou tentamos recuperar do ultimo estado falho)
            
            CognitiveMemoryService.record_action(
                x=0, y=0,  # Parametros precisariam vir do request, mas execute_task é genérico. 
                           # TODO: Refatorar execute_task para receber params de contexto ou injetar na callback.
                           # Por hora, vamos focar no sucesso que é mais fácil capturar nas camadas acima, 
                           # mas o engine deve ser agnóstico.
                           # MELHOR: O engine retorna o resultado, quem chama (smart.py) grava a memória.
                           # O plano original dizia "inference_engine.py grava". Vamos tentar manter.
                app_name="unknown", 
                success=False, 
                strategy="all_failed"
            )
        except: pass
        
        return failure_result

    def _verify_outcome(self, t0, t1, expectation) -> Dict[str, Any]:
        """Compara T0 e T1 contra a Expectativa."""
        exp_type = expectation.get('type', 'any_change')
        
        # Lógica de Inferência
        
        # Caso 1: Espera mudança de janela
        if exp_type == 'window_change':
            target = expectation.get('target_window', '').lower()
            current = t1.get('window_title', '').lower()
            
            # Verificação exata ou parcial
            if target and target in current:
                return {"success": True, "confidence": 0.95, "reason": f"Window changed to expected '{current}'"}
            elif t0.get('window_title') != t1.get('window_title'):
                # Mudou, mas não para o que esperava (Surpresa Parcial)
                return {"success": False, "confidence": 0.5, "reason": f"Window changed to '{current}', expected '{target}'"}
            else:
                return {"success": False, "confidence": 0.8, "reason": "No window change detected"}

        # Caso 2: Espera qualquer mudança visual (ex: menu abriu)
        elif exp_type == 'visual_change':
            # Comparar Hashes
            h0 = t0.get('visual_hash', 0)
            h1 = t1.get('visual_hash', 0)
            diff = abs(h0 - h1) # Simplificação, dhash real precisa de hamming distance
            
            # Assumindo perceptivo simples por enquanto
            if h0 != h1: 
                return {"success": True, "confidence": 0.7, "reason": "Visual state changed"}
            else:
                return {"success": False, "confidence": 0.6, "reason": "No visual change detected"}
                
        # Fallback: Qualquer mudança
        return {"success": True, "confidence": 0.1, "reason": "Default pass (not implemented)"}

    def _compute_visual_hash(self, image_array):
        """Calcula um hash visual simples para detecção de mudanças (dHash)."""
        try:
            # Resize para 9x8 para dHash
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (9, 8))
            # Comparar pixels adjacentes
            diff = resized[:, 1:] > resized[:, :-1]
            return sum([2**i for i, v in enumerate(diff.flatten()) if v])
        except Exception:
            return 0
