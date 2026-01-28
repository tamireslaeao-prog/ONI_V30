"""
Intent Parser (Tier 3 Moonshot)
Traduz linguagem natural para intenções estruturadas.
No futuro, será substituído por um LLM real (Mistral/GPT).
Por enquanto, usa heurísticas avançadas (Mock).
"""

import re
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger("IntentParser")

@dataclass
class Intent:
    action: str
    params: Dict[str, Any]
    confidence: float
    raw_instruction: str

class IntentParser:
    """Parser de intenções de usuário"""
    
    def __init__(self):
        # Regex patterns for basic intents
        self.patterns = [
            (r"click (?:on )?(?:the )?(.+)", "click"),
            (r"type (.+) in (?:the )?(.+)", "type"),
            (r"open (.+)", "open"),
            (r"save (?:the )?file as (.+)", "save_as"),
            (r"run (?:scan|analysis)", "run_workflow")
        ]
    
    def parse(self, instruction: str) -> Intent:
        """Parses natural language into Intent"""
        instruction = instruction.lower().strip()
        logger.info(f"Parsing instruction: '{instruction}'")
        
        # 1. Try Regex Patterns
        for pattern, action_type in self.patterns:
            match = re.search(pattern, instruction)
            if match:
                groups = match.groups()
                params = {}
                
                if action_type == "click":
                    params = {"target": groups[0]}
                elif action_type == "type":
                    params = {"text": groups[0], "target": groups[1]}
                elif action_type == "open":
                    params = {"app": groups[0]}
                elif action_type == "save_as":
                    params = {"filename": groups[0]}
                elif action_type == "run_workflow":
                    params = {"workflow": "analysis"}
                
                return Intent(
                    action=action_type,
                    params=params,
                    confidence=0.95,
                    raw_instruction=instruction
                )
        
        # 2. Fallback / Generic
        return Intent(
            action="unknown",
            params={},
            confidence=0.0,
            raw_instruction=instruction
        )
