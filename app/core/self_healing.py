"""
Self-Healing Workflows (Tier 3 Moonshot)
Sistema que aprende e conserta automaticamente erros de execução,
baseado em histórico de erros similares e base de conhecimento.
"""

import time
import json
import logging
import pickle
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from app.core.process_sentinel import sentinel

# Mock sklearn/sentence_transformers if not installed
try:
    import numpy as np
    from sklearn.cluster import DBSCAN
except ImportError:
    np = None
    DBSCAN = None

logger = logging.getLogger("SelfHealing")

@dataclass
class ErrorRecord:
    type: str
    message: str
    context: Dict
    action: Dict
    timestamp: float
    solution_applied: Optional[str] = None
    success: bool = False

class ErrorDatabase:
    """Banco de dados de erros e soluções"""
    
    def __init__(self, db_dir: str = "oni_memory"):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.errors: List[Dict] = []
        self.solutions: Dict[str, List[str]] = {}
        self._load()
        
        # Mock logic for embeddings if ML not available
        self.ml_ready = (np is not None)

    def record_error(self, error_type: str, error_message: str, context: Dict, failed_action: Dict):
        """Registra um erro"""
        err = {
            "type": error_type,
            "message": error_message,
            "context": context,
            "action": failed_action,
            "timestamp": time.time()
        }
        self.errors.append(err)
        self._save()
        logger.info(f"Recorded error: {error_type} - {error_message[:50]}...")

    def record_solution(self, error_signature: str, solution: str, success: bool):
        """Registra uma solução que funcionou"""
        if error_signature not in self.solutions:
            self.solutions[error_signature] = []
        
        if success:
            if solution not in self.solutions[error_signature]:
                self.solutions[error_signature].append(solution)
        
        self._save()
        logger.info(f"Recorded solution '{solution}' for '{error_signature}' (Success: {success})")

    def find_similar_errors(self, error_message: str, threshold: float = 0.8) -> List[Dict]:
        """Encontra erros similares (Mocking semantic search for prototype)"""
        if not self.errors:
            return []
            
        # Simplified string matching for prototype
        # In a real scenario, use SentenceTransformer embeddings
        similar = []
        words = set(error_message.lower().split())
        
        for err in self.errors:
            err_words = set(err["message"].lower().split())
            overlap = len(words.intersection(err_words))
            union = len(words.union(err_words))
            jaccard = overlap / union if union > 0 else 0
            
            if jaccard >= 0.3: # Low threshold for mock text matching
                similar.append({**err, "similarity": jaccard})
        
        return sorted(similar, key=lambda x: x["similarity"], reverse=True)

    def _save(self):
        try:
            with open(self.db_dir / "errors.pkl", "wb") as f:
                pickle.dump(self.errors, f)
            with open(self.db_dir / "solutions.pkl", "wb") as f:
                pickle.dump(self.solutions, f)
        except Exception as e:
            logger.error(f"Failed to save DB: {e}")

    def _load(self):
        try:
            if (self.db_dir / "errors.pkl").exists():
                with open(self.db_dir / "errors.pkl", "rb") as f:
                    self.errors = pickle.load(f)
            if (self.db_dir / "solutions.pkl").exists():
                with open(self.db_dir / "solutions.pkl", "rb") as f:
                    self.solutions = pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load DB: {e}")


class SelfHealingWorkflow:
    """Workflow que se conserta sozinho"""
    
    def __init__(self, db_dir: str = "oni_memory"):
        self.error_db = ErrorDatabase(db_dir)
        # Mock executor for this prototype
        self.executor = self 
    
    def execute_action(self, action: Dict) -> bool:
        """Mock execution method"""
        # Simulate failures for testing
        if action.get("simulate_fail"):
            raise Exception("Simulated Failure")
        print(f"Executing: {action}")
        return True

    def execute_with_healing(self, workflow: List[Dict]) -> bool:
        """
        Executa workflow com auto-correção
        """
        for i, action in enumerate(workflow):
            try:
                # Attempt Execution
                success = self.execute_action(action)
                if not success:
                    raise Exception("Action returned False")
                
            except Exception as e:
                # Self-Healing Triggered
                print(f"⚠️ Action {i} failed: {e}. Attempting heal...")
                
                # Record initial error
                self.error_db.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={"workflow_step": i},
                    failed_action=action
                )
                
                healed = self._heal_action(action, workflow, i, str(e))
                
                if not healed:
                    print(f"❌ Self-heal failed for step {i}")
                    return False
                
                print(f"✓ Self-healed successfully at step {i}")
        
        return True

    def _heal_action(self, failed_action: Dict, workflow: List[Dict], step_index: int, error_msg: str) -> bool:
        """Tenta curar uma ação que falhou"""
        
        # 1. Search Known Solutions
        error_sig = f"{failed_action.get('type','unknown')}:{error_msg[:20]}" # Simple sig
        
        # Check explicit history first
        if error_sig in self.error_db.solutions:
            solutions = self.error_db.solutions[error_sig]
            logger.info(f"Found known solutions: {solutions}")
            for sol in solutions:
                if self._apply_solution(failed_action, sol):
                    print(f"  ✓ Fixed using known solution: {sol}")
                    return True

        # 2. Generic Heuristics
        heuristics = ["retry_delay", "alt_hotkey", "purge_ghosts"]
        
        for fix in heuristics:
            print(f"  Trying heuristic: {fix}")
            if self._apply_generic_fix(failed_action, fix):
                # Record successful new solution
                self.error_db.record_solution(error_sig, fix, True)
                return True
                
        return False

    def _apply_solution(self, action: Dict, solution: str) -> bool:
        """Re-applies a specific solution strategy"""
        return self._apply_generic_fix(action, solution)

    def _apply_generic_fix(self, action: Dict, fix: str) -> bool:
        """Implementation of fix strategies"""
        if fix == "retry_delay":
            time.sleep(1) # Delay
            print("  Retrying with delay...")
            try:
                # For simulation, remove the fail flag on retry if we want it to verify success
                # In real world, delay might actually fix race conditions
                if action.get("simulate_fail"):
                    # Simulating that retry fixes it (sometimes)
                    action_copy = action.copy()
                    del action_copy["simulate_fail"] 
                    return self.execute_action(action_copy)
                return self.execute_action(action)
            except Exception:
                return False
                
        elif fix == "alt_hotkey":
            if action.get("type") == "click" and action.get("intent") == "save":
                 print("  Converting Click -> Ctrl+S")
                 return self.execute_action({"type": "keys", "keys": "ctrl+s"})
        
        elif fix == "purge_ghosts":
            print("  ⚠️ Emergency Purge: Cleaning all automation ghosts...")
            sentinel.emergency_purge_automation()
            time.sleep(2)
            return self.execute_action(action)
        
        return False
