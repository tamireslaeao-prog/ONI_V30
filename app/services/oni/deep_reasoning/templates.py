"""
ONI Deep Reasoning - Reasoning Templates
"""

DRAWING_REASONING_TEMPLATE = """
You are analyzing a DRAWING task. Think deeply and professionally.

TASK: {task}
APPLICATION: {app_name}
CANVAS BOUNDS: {canvas_bounds}

Analyze this task and provide a PROFESSIONAL execution plan.
(Template truncated for brevity - see original for full content)
"""

GENERAL_REASONING_TEMPLATE = """
You are analyzing a complex task. Think step-by-step.

TASK: {task}
CONTEXT: {context}

Provide a detailed execution plan.
(Template truncated for brevity - see original for full content)
"""
