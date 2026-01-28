"""
ONI v12.0 - Action Telemetry
Records and analyzes action performance metrics.
"""
import uuid
import json
import time
from pathlib import Path
from collections import Counter
from typing import Any

import structlog

logger = structlog.get_logger()

class ActionTelemetry:
    """
    Collects metrics for all actions to enable analysis and self-correction.
    """
    
    def __init__(self):
        self.metrics: list[dict[str, Any]] = []
        self.session_id = str(uuid.uuid4())
        self.log_dir = Path("temp/telemetry")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def log_action(self, action_data: dict[str, Any]):
        """
        Log an executed action.
        
        Expected keys in action_data:
            - timestamp: str/float
            - action_type: str
            - intent: str
            - strategy_used: str
            - attempts: int
            - latency_ms: float
            - success: bool
            - context: dict
        """
        # Ensure timestamp
        if 'timestamp' not in action_data:
            action_data['timestamp'] = time.time()
            
        self.metrics.append(action_data)
        
        # Log to structured logger as well
        if action_data.get('success'):
            logger.info("action_success", **action_data)
        else:
            logger.warning("action_failed", **action_data)
        
        # Generate report every 100 actions
        if len(self.metrics) % 100 == 0:
            self._generate_report()
            
    def get_report(self) -> dict[str, Any]:
        """
        Get current performance report.
        """
        if not self.metrics:
            return {
                "total_actions": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0,
                "fallback_count": 0,
                "strategy_usage": {}
            }
            
        total = len(self.metrics)
        success_count = sum(1 for m in self.metrics if m.get('success', False))
        success_rate = success_count / total
        
        avg_latency = sum(m.get('latency_ms', 0) for m in self.metrics) / total
        
        # Fallback usage
        strategies = [m.get('strategy_used', 'unknown') for m in self.metrics]
        strategy_counts = dict(Counter(strategies))
        fallback_count = sum(1 for s in strategies if s != 'UI_CLICK' and s != 'unknown')
        
        return {
            "session_id": self.session_id,
            "timestamp": time.time(),
            "total_actions": total,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency,
            "fallback_count": fallback_count,
            "strategy_usage": strategy_counts
        }

    def _generate_report(self):
        """
        Generate automatic performance analysis report.
        """
        report = self.get_report()
        # Monitor issues (attempts > 1)
        multi_attempts = [m for m in self.metrics if m.get('attempts', 1) > 1]
        monitor_issues = dict(Counter([m.get('context', {}).get('monitor', 'unknown') for m in multi_attempts]))
        report["monitor_issues"] = monitor_issues

        
        # Save report
        report_path = self.log_dir / f"session_{self.session_id}.json"
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info("telemetry_report_generated", path=str(report_path), success_rate=success_rate)
        except Exception as e:
            logger.error("failed_to_save_telemetry", error=str(e))
        
        # Alert if standard implementation
        if success_rate < 0.85:
            logger.warning(f"⚠️ Success rate dropped to {success_rate*100:.1f}%")

# Global instance
telemetry = ActionTelemetry()
