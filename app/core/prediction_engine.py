"""
Prediction Engine Adapter (V1 -> V2)
Created to satisfy dependencies in app.infrastructure.actuation.executor.py
"""
from app.core.prediction_engine_v2 import ActionPredictorV2

class LegacyPredictorAdapter:
    def __init__(self):
        self.v2 = ActionPredictorV2()

    def predict_success(self, action_type: str, context_hash: str):
        return self.v2.predict_success(action_type, context_hash)

    def should_skip_to_fallback(self, confidence: float, threshold: float = 0.2) -> bool:
        return confidence < threshold

    def update_outcome(self, action_type: str, context_hash: str, result: bool):
        # context_hash in executor is constructed as f"{action.type}_{action.strategy.name}"
        # We try to extract strategy from it, defaulting to "unknown"
        parts = context_hash.split('_', 1)
        strategy = parts[1] if len(parts) > 1 else "unknown"
        self.v2.record_result(action_type, result, strategy)

# Global instance expected by executor.py
predictor = LegacyPredictorAdapter()
