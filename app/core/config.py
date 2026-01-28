"""
ONI v2.0 - Configuration System
Pydantic Settings with comprehensive validation
"""
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Log level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogFormat(str, Enum):
    """Log format options."""
    JSON = "json"
    CONSOLE = "console"


class AgentMode(str, Enum):
    """Agent operation modes."""
    AUTONOMOUS = "autonomous"
    SUPERVISED = "supervised"
    MANUAL = "manual"


class VisionSettings(BaseSettings):
    """Computer Vision Configuration."""
    model_config = SettingsConfigDict(env_prefix="VISION__")
    
    capture_fps: int = Field(default=30, ge=1, le=120)
    capture_backend: Literal["dxcam", "mss"] = "dxcam"
    ocr_engines: list[str] = ["tesseract", "easyocr"]
    ocr_languages: list[str] = ["eng", "por"]
    preprocessing_enabled: bool = True
    super_resolution_enabled: bool = False
    object_detection_model: str = "yolov8n.pt"
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_omniparser: bool = True  # Enable advanced OmniParser implementation
    
    # Vision Caching (Phase 4)
    caching_enabled: bool = True
    cache_ttl: float = 2.0 # Seconds valid for same dhash


class LLMSettings(BaseSettings):
    """Language Model Configuration."""
    model_config = SettingsConfigDict(env_prefix="LLM__")
    
    model_path: Path = Field(default=Path("models/llama-3.1-8b.gguf"))
    context_size: int = Field(default=8192, ge=512, le=131072)
    n_threads: int = Field(default=8, ge=1)
    n_gpu_layers: int = Field(default=35, ge=0)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=0)
    repeat_penalty: float = Field(default=1.1, ge=1.0)
    grammar_enabled: bool = True
    grammar_dir: Path = Field(default=Path("configs/grammars"))


class ActuationSettings(BaseSettings):
    """Input Control Configuration."""
    model_config = SettingsConfigDict(env_prefix="ACTUATION__")
    
    mouse_backend: Literal["win32", "pyautogui"] = "win32"
    humanize_enabled: bool = True
    movement_duration: float = Field(default=0.5, ge=0.1, le=5.0)
    typing_wpm: int = Field(default=60, ge=20, le=200)
    error_simulation_enabled: bool = False
    error_rate: float = Field(default=0.01, ge=0.0, le=0.1)


class MemorySettings(BaseSettings):
    """Memory System Configuration."""
    model_config = SettingsConfigDict(env_prefix="MEMORY__")
    
    redis_url: str = "redis://localhost:6379"
    sqlite_path: Path = Field(default=Path("data/memory.db"))
    vector_store_path: Path = Field(default=Path("data/chroma"))
    working_memory_ttl: int = Field(default=3600, ge=60)
    episodic_memory_max_entries: int = Field(default=10000, ge=100)
    episodic_memory_max_entries: int = Field(default=10000, ge=100)
    enable_compression: bool = True
    render_retention_hours: int = Field(default=24, ge=1) # Phase 4: Auto-cleanup


class MonitoringSettings(BaseSettings):
    """Monitoring & Observability Configuration."""
    model_config = SettingsConfigDict(env_prefix="MONITORING__")
    
    metrics_enabled: bool = True
    metrics_port: int = Field(default=9090, ge=1024, le=65535)
    tracing_enabled: bool = False
    tracing_endpoint: str | None = None
    log_level: LogLevel = LogLevel.INFO
    log_format: LogFormat = LogFormat.JSON


class APISettings(BaseSettings):
    """API Server Configuration."""
    model_config = SettingsConfigDict(env_prefix="API__")
    
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1024, le=65535)
    reload: bool = False
    workers: int = Field(default=1, ge=1)
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    api_key: str | None = None
    enable_graphql: bool = True


class SafetySettings(BaseSettings):
    """Safety & Guardian Configuration."""
    model_config = SettingsConfigDict(env_prefix="SAFETY__")
    
    enforce_axioms: bool = False # Hard enforcement of soul tokens
    block_destructive_commands: bool = True
    require_confirmation_threshold: float = 0.8 # Confidence threshold



class AgentSettings(BaseSettings):
    """Agent Behavior Configuration."""
    model_config = SettingsConfigDict(env_prefix="AGENT__")
    
    mode: AgentMode = AgentMode.SUPERVISED
    max_actions_per_cycle: int = Field(default=10, ge=1)
    max_iterations: int = Field(default=100, ge=1)
    action_timeout: float = Field(default=30.0, ge=1.0)
    verification_enabled: bool = True
    retry_attempts: int = Field(default=3, ge=0)
    learning_enabled: bool = True
    
    # v3.0: Hybrid agent features
    enable_reflection: bool = True
    enable_code_agent: bool = True
    enable_code_agent: bool = True
    max_trajectory_length: int = Field(default=8, ge=1)


class GroundingSettings(BaseSettings):
    """Grounding & Context Configuration."""
    model_config = SettingsConfigDict(env_prefix="GROUNDING__")
    
    enabled: bool = True
    max_search_results: int = Field(default=5, ge=1)
    search_provider: Literal["google", "bing"] = "google"
    endpoint_url: str | None = None  # UI-TARS endpoint URL
    api_key: str | None = None  # API key for grounding services
    model: str = "ByteDance-Seed/UI-TARS-1.5-7B"  # Grounding model
    provider: str = "huggingface"  # Provider type (huggingface, openai, etc.)
    grounding_width: int = Field(default=1920, ge=480)  # Reference width for coordinates
    grounding_height: int = Field(default=1080, ge=360)  # Reference height for coordinates
    enable_ocr_fallback: bool = True  # Enable OCR-based fallback when UI-TARS fails


class Settings(BaseSettings):
    """Main Application Settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )
    
    app_name: str = "Omega Neural Interface"
    app_version: str = "25.1.0"  # ONI V25.1 - Soul Binding Consolidado
    debug: bool = False
    
    vision: VisionSettings = Field(default_factory=VisionSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    actuation: ActuationSettings = Field(default_factory=ActuationSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    api: APISettings = Field(default_factory=APISettings)
    agent: AgentSettings = Field(default_factory=AgentSettings)
    grounding: GroundingSettings = Field(default_factory=GroundingSettings)
    safety: SafetySettings = Field(default_factory=SafetySettings)
    
    @field_validator("llm", mode="after")
    @classmethod
    def validate_model_path(cls, v: LLMSettings) -> LLMSettings:
        """Validate model path exists (warning only)."""
        if not v.model_path.exists():
            import warnings
            warnings.warn(f"LLM model not found at: {v.model_path}")
        return v


# Global settings instance (lazy loaded)
settings = Settings()
