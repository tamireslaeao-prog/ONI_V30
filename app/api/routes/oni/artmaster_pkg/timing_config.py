"""
ONI Timing Constants
Centralized timing configuration for UI automation delays.
"""

class TimingConfig:
    """Timing constants for GUI automation.
    
    All values in seconds. Adjust based on system performance.
    """
    
    # UI Response Delays
    UI_SETTLE = 0.5  # Allow UI to settle after action
    UI_QUICK = 0.2   # Quick UI response
    UI_INSTANT = 0.1 # Instant UI feedback
    
    # Input Delays
    KEYPRESS = 0.1       # Between keypresses
    HOTKEY = 0.1         # After hotkey
    TYPE_CHAR = 0.05     # Between typed characters
    TYPE_FINISH = 0.2    # After typing completes
    
    # Dialog Delays
    DIALOG_OPEN = 0.3    # Wait for dialog to open
    DIALOG_CLOSE = 0.5   # Wait for dialog to close
    
    # Tool Delays
    TOOL_SELECT = 0.1    # After selecting tool
    TOOL_CONFIG = 0.2    # After configuring tool
    
    # Heavy Operations
    FILE_SAVE = 0.5      # File save operation
    LAYER_MERGE = 0.5    # Layer merge (heavy)
    LAYER_CREATE = 0.3   # Layer creation
    
    # Drawing Delays
    DRAW_STEP = 0.01     # Fast bursts (brush size adjustment)
    DRAW_FINISH = 0.2    # After drawing completes
    
    # Focus Delays
    WINDOW_ACTIVATE = 0.5  # After activating window
    CANVAS_CLICK = 0.2     # After clicking canvas


# Backward compatibility aliases
DELAY_UI_SETTLE = TimingConfig.UI_SETTLE
DELAY_QUICK = TimingConfig.UI_QUICK
DELAY_INSTANT = TimingConfig.UI_INSTANT
