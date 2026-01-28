"""
Prediction Engine V2 - Otimizado
Correções: latência real, threshold dinâmico
"""

import time
from collections import deque
from typing import Dict, Tuple
import numpy as np


class ActionPredictorV2:
    """Versão otimizada com medição correta de latência"""
    
    def __init__(self, window_size: int = 50):
        # Histórico recente (sliding window)
        self.history = deque(maxlen=window_size)
        
        # Cache de predições
        self.cache = {}
        
        # Estatísticas por tipo de ação
        self.stats = {}
    
    def predict_success(
        self, 
        action_type: str, 
        context_hash: str
    ) -> Tuple[float, float]:
        """
        Prediz probabilidade de sucesso
        
        Returns:
            (confidence, latency_ms)
        """
        start = time.perf_counter()  # ← FIX: usar perf_counter
        
        # Cache hit
        cache_key = f"{action_type}_{context_hash}"
        if cache_key in self.cache:
            cached_conf = self.cache[cache_key]
            latency = (time.perf_counter() - start) * 1000
            return cached_conf, latency
        
        # Calcular confidence baseado em histórico
        if action_type not in self.stats:
            # Primeira vez: confidence alta
            confidence = 0.85
        else:
            stats = self.stats[action_type]
            total = stats['success'] + stats['failure']
            
            if total == 0:
                confidence = 0.85
            else:
                # Confidence = taxa de sucesso com decay agressivo
                success_rate = stats['success'] / total
                
                # Penalizar fortemente falhas recentes
                recent_failures = sum(
                    1 for h in list(self.history)[-10:]  # Últimas 10
                    if h['type'] == action_type and not h['success']
                )
                
                # FIX: Decay mais agressivo (0.3 em vez de 0.2)
                confidence = success_rate * (1.0 - recent_failures * 0.3)
                confidence = max(0.1, min(1.0, confidence))
        
        # Atualizar cache
        self.cache[cache_key] = confidence
        
        latency = (time.perf_counter() - start) * 1000
        return confidence, latency
    
    def record_result(
        self,
        action_type: str,
        success: bool,
        strategy_used: str
    ):
        """Registra resultado de uma ação"""
        
        # Atualizar estatísticas
        if action_type not in self.stats:
            self.stats[action_type] = {'success': 0, 'failure': 0}
        
        if success:
            self.stats[action_type]['success'] += 1
        else:
            self.stats[action_type]['failure'] += 1
        
        # Adicionar ao histórico
        self.history.append({
            'type': action_type,
            'success': success,
            'strategy': strategy_used,
            'timestamp': time.time()
        })
        
        # Invalidar cache (forçar recálculo)
        self.cache.clear()
    
    def get_optimal_threshold(self, action_type: str) -> float:
        """
        Calcula threshold ótimo baseado em histórico
        
        Returns:
            Threshold entre 0.4-0.7
        """
        if action_type not in self.stats:
            return 0.5  # Padrão balanceado
        
        stats = self.stats[action_type]
        total = stats['success'] + stats['failure']
        
        if total < 10:
            return 0.5  # Pouco histórico: balanceado
        
        success_rate = stats['success'] / total
        
        if success_rate > 0.85:
            # Alta confiabilidade: threshold mais relaxado
            return 0.4
        elif success_rate < 0.60:
            # Baixa confiabilidade: threshold mais conservador
            return 0.7
        else:
            # Normal
            return 0.5
