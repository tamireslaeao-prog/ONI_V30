from dataclasses import dataclass
from typing import Literal

@dataclass
class GoalSegment:
    type: Literal["preset", "llm"]
    text: str
    preset_key: str = ""

def parse_goal(goal: str) -> list[GoalSegment]:
    """
    Parse a natural language goal into segments.
    Simple implementation: returns the whole goal as LLM segment.
    """
    return [GoalSegment(type="llm", text=goal)]
