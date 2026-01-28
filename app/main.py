"""
ONI v11.0 - Main Application
Full initialization with LLM, Agent, and Anti-Hallucination Pipeline
"""
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.dependencies import container
from app.infrastructure.monitoring.logger import configure_logging, get_logger

logger = get_logger(__name__)

# Fix P22: Helper at module level
def create_actuation_system():
    """Helper to create actuation system from container."""
    if container.has("mouse") and container.has("keyboard"):
        class ActuationSystem:
            def __init__(self, mouse, keyboard):
                self.mouse = mouse
                self.keyboard = keyboard
        return ActuationSystem(container.get("mouse"), container.get("keyboard"))
    return None

async def init_subsystems() -> None:
    """Initialize all ONI subsystems."""
    logger.info("initializing_subsystems")
    
    # Event Bus
    try:
        from app.core.events import EventBus
        event_bus = EventBus()
        container.register("event_bus", event_bus)
        logger.info("event_bus_ready")
    except Exception as e:
        logger.warning("event_bus_failed", error=str(e))
    
    # Window Manager
    try:
        from app.infrastructure.actuation.window_manager import WindowManager
        window_manager = WindowManager()
        container.register("window_manager", window_manager)
        logger.info("window_manager_ready")
    except Exception as e:
        logger.warning("window_manager_failed", error=str(e))
    
    # Vision System (Screen Capture + OCR)
    try:
        from app.infrastructure.vision.capture import ScreenCapture
        screen_capture = ScreenCapture(backend="auto")
        await screen_capture.initialize()
        
        # Initialize OCR with Tesseract
        import pytesseract
        # Set Tesseract path for Windows
        tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        import os
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info("tesseract_path_set", path=tesseract_path)
            
        # Fix P20: Move Tesseract path setting before ocr.initialize() calls.
        # Ideally this should be done very early or inside TesseractOCR.__init__
        # But here is fine as long as it precedes usage.
        
        from app.infrastructure.vision.ocr.tesseract import TesseractOCR
        ocr = TesseractOCR(languages=["eng", "por"])
        # Fix P20: Async Init (Assuming initialize is async)
        await ocr.initialize()
        
        class VisionSystem:
            def __init__(self, capture, ocr, window_mgr):
                self.capture_obj = capture
                self.ocr = ocr
                self.window_manager = window_mgr
            
            # Allow direct capture call
            async def capture(self, *args, **kwargs):
                return await self.capture_obj.capture(*args, **kwargs)

        vision_system = VisionSystem(
            screen_capture, 
            ocr, 
            container.get("window_manager") if container.has("window_manager") else None
        )
        
        container.register("vision", vision_system)

        # Fix 5.2: Register Shape Service
        from app.services.shape_service import ShapeService
        shape_service = ShapeService()
        container.register("shape_service", shape_service)
        
        logger.info("vision_ready", backend=screen_capture._active_backend, ocr="tesseract", shape_service=True)

        # Fix 5.3: Register Onihand Service (Innovation from tests/)
        from app.services.onihand_service import OnihandService
        onihand_service = OnihandService()
        await onihand_service.initialize()
        container.register("onihand_service", onihand_service)
        logger.info("onihand_service_ready")

    except Exception as e:
        logger.warning("vision_failed", error=str(e))
    
    # OmniParser Service (New v6.1)
    if settings.vision.enable_omniparser:
        try:
            from app.services.omniparser_service import OmniParserService
            # Use configured model path if available, otherwise default
            omniparser = OmniParserService(
                yolo_model_path=settings.vision.object_detection_model
            )
            container.register("omniparser", omniparser)
            logger.info("omniparser_ready")
        except Exception as e:
            logger.warning("omniparser_init_failed", error=str(e))

    # Mouse & Keyboard
    try:
        from app.infrastructure.actuation.human_mouse import HumanMouse
        from app.infrastructure.actuation.keyboard import HumanizedKeyboard
        mouse = HumanMouse()
        keyboard = HumanizedKeyboard()
        container.register("mouse", mouse)
        container.register("keyboard", keyboard)
        logger.info("actuation_ready")
    except Exception as e:
        logger.warning("actuation_failed", error=str(e))

    # Native Service (Win32 API for System Dominion)
    try:
        from app.services.native_service import NativeService
        native_service = NativeService()
        container.register("native_service", native_service)
        logger.info("native_service_ready")
    except Exception as e:
        logger.warning("native_service_failed", error=str(e))

    # Creative Engine (Phase 3)
    try:
        from app.services.creative_engine import CreativeEngineService
        creative_engine = CreativeEngineService()
        container.register("creative_engine", creative_engine)
        logger.info("creative_engine_ready")
    except Exception as e:
        logger.warning("creative_engine_init_failed", error=str(e))
        
    # Phase 4: Maintenance Service (Background Optimization)
    try:
        from app.services.maintenance_service import MaintenanceService
        maintenance = MaintenanceService()
        container.register("maintenance", maintenance)
        # Fire and forget maintenance
        import asyncio
        asyncio.create_task(asyncio.to_thread(maintenance.run_maintenance))
        logger.info("maintenance_service_started")
    except Exception as e:
        logger.warning("maintenance_service_failed", error=str(e))
    
    # Photoshop Service (v10.0 - Direct COM Control)
    try:
        from app.services.photoshop_service import PhotoshopService
        photoshop_service = PhotoshopService()
        # Connect proactively if possible, or wait for request
        # photoshop_service.connect() 
        container.register("photoshop_service", photoshop_service)
        logger.info("photoshop_service_ready")

        # Register Composer Service (V12.2)
        from app.services.photoshop.composer_service import PhotoshopComposer
        composer = PhotoshopComposer()
        container.register("composer_service", composer)
        logger.info("composer_service_ready")

    except Exception as e:
        logger.warning("photoshop_service_failed", error=str(e))
        
    try:
        from app.services.blender_service import BlenderService
        blender_service = BlenderService()
        container.register("blender_service", blender_service)
        logger.info("blender_service_ready")
    except Exception as e:
        logger.warning("blender_service_failed", error=str(e))
    
    # CorelDRAW Service (v2.1 - Lazy Loading)
    try:
        from app.services.corel.corel_service import CorelService, AIVectorizerInterface
        corel_service = CorelService()
        container.register("corel_service", corel_service)
        corel_ai_interface = AIVectorizerInterface(corel_service)
        container.register("corel_ai_interface", corel_ai_interface)
        logger.info("corel_service_ready")
    except Exception as e:
        logger.warning("corel_service_failed", error=str(e))
    
    # LLM Provider - Use providers from .env (ZAI, Mistral, Gemini, OpenRouter, etc.)
    llm_manager = None
    llm_provider = None
    try:
        from app.infrastructure.llm.providers import setup_providers, llm_manager, GeminiProvider, OpenRouterProvider
        from app.infrastructure.llm.mistral_provider import MistralProvider
        from app.infrastructure.llm.zai_provider import ZAIProvider, get_zai_provider
        from app.infrastructure.llm.composed_provider import ComposedProvider, create_composed_provider
        from app.infrastructure.vision.uitars_provider import UITarsProvider
        
        # Setup all providers from .env with fallback
        llm_manager = setup_providers()
        
        # Add ZAI (GLM-4) as PRIORITY provider - supports vision!
        zai_key = os.getenv("ZAI_API_KEY")
        if zai_key:
            zai = get_zai_provider()
            if zai.is_available:
                llm_manager.register_provider("zai", zai)
                logger.info("zai_provider_ready", model=zai.name)
        
        # Also add Mistral if configured
        mistral_key = os.getenv("MISTRAL_API_KEY")
        if mistral_key:
            mistral = MistralProvider()
            if mistral.is_available:
                llm_manager.register_provider("mistral", mistral)
        
        # Set fallback order: ZAI (vision) → Mistral → OpenRouter → Gemini
        llm_manager.set_fallback_order(["zai", "mistral", "openrouter", "gemini", "huggingface", "local"])
        
        # Create ComposedProvider with visual grounding (v4.0)
        uitars = None
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key:
            try:
                uitars = UITarsProvider(model="moondream3", api_key=hf_key)
                logger.info("uitars_grounding_ready", model="moondream3")
            except Exception as e:
                logger.warning("uitars_init_failed", error=str(e))
        
        # Get best available planner (ZAI has priority now)
        planner = llm_manager.get_provider() if llm_manager.available_providers else None
        
        if planner:
            # Create composed provider (grounding + planning)
            # Note: ZAI already has vision, so uitars is optional enhancement
            llm_provider = create_composed_provider(
                planner=planner,
                grounder=uitars,  # May be None, ZAI uses its own vision
            )
            logger.info("composed_provider_ready", 
                       planner=planner.name if hasattr(planner, 'name') else "Unknown",
                       grounding="uitars" if uitars else "native")
        
        if llm_manager.available_providers:
            logger.info("llm_manager_ready", providers=llm_manager.available_providers)
            # Register both composed provider and manager
            container.register("llm", llm_provider or llm_manager)
            # Fix P21: DI Container Cleanup (Already looks okay, but P21 says consolidated?)
            # The current registration is:
            # "llm" -> best available (provider or manager)
            # "llm_manager" -> manager explicitly
            # "llm_composed" -> composed explicitly
            # This seems correct for flexibility, but maybe P21 meant removing redundancy?
            # Keeping as is for maximizing compatibility with different injection patterns.
        else:
            logger.warning("no_llm_providers_available")
            
    except Exception as e:
        logger.error("llm_setup_failed", error=str(e))
        import traceback
        traceback.print_exc()

    
    # Grounding System (v3.0)
    grounding = None
    try:
        from app.grounding.hybrid import HybridGrounding
        from app.grounding.ui_tars import UITarsGrounding
        
        # Setup UI-TARS if configured
        ui_tars = None
        if settings.grounding.endpoint_url:
            ui_tars = UITarsGrounding(
                endpoint_url=settings.grounding.endpoint_url,
                api_key=settings.grounding.api_key,
                model=settings.grounding.model,
                provider=settings.grounding.provider,
                grounding_width=settings.grounding.grounding_width,
                grounding_height=settings.grounding.grounding_height,
            )
            if await ui_tars.initialize():
                logger.info("ui_tars_ready", endpoint=settings.grounding.endpoint_url[:50])
            else:
                ui_tars = None
                logger.warning("ui_tars_init_failed")
        
        # Setup SemanticLocator from existing ONI code
        semantic_locator = None
        try:
            from app.infrastructure.vision.semantic_locator import SemanticLocator
            semantic_locator = SemanticLocator()
            logger.info("semantic_locator_ready")
        except Exception as e:
            logger.warning("semantic_locator_failed", error=str(e))
        
        grounding = HybridGrounding(
            ui_tars=ui_tars,
            semantic_locator=semantic_locator,
            fallback_enabled=settings.grounding.enable_ocr_fallback,
        )
    except Exception as e:
        logger.warning("grounding_setup_failed", error=str(e))
    
    # ONI v11.0 - Anti-Hallucination Services
    try:
        from app.services.oni.calibration_service import CalibrationService, get_calibration_service
        from app.services.oni.consensus_engine import ConsensusEngine, get_consensus_engine
        from app.services.oni.grounded_perception import GroundedPerceptionService, get_grounded_perception_service
        from app.infrastructure.vision.qwen_vl_provider import QwenVLProvider
        
        # Initialize Calibration Service
        calibration_service = get_calibration_service()
        container.register("calibration_service", calibration_service)
        logger.info("calibration_service_ready", dpi_scale=calibration_service.dpi_scale)
        
        # Initialize Consensus Engine
        consensus_engine = get_consensus_engine()
        
        # Register existing providers with consensus engine
        if container.has("omniparser"):
            consensus_engine.register_provider("omniparser", container.get("omniparser"))
        if ui_tars:
            consensus_engine.register_provider("uitars", ui_tars)
        
        # Add Qwen-VL via OpenRouter (default mode)
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            qwen_vl = QwenVLProvider(mode="openrouter")  # Uses OPENROUTER_API_KEY automatically
            consensus_engine.register_provider("qwenvl", qwen_vl)
            logger.info("qwen_vl_provider_ready", mode="openrouter")
        
        container.register("consensus_engine", consensus_engine)
        logger.info("consensus_engine_ready", providers=len(consensus_engine._providers))
        
        # Initialize Grounded Perception
        grounded_perception = GroundedPerceptionService(
            consensus_engine=consensus_engine,
            calibration_service=calibration_service,
            omniparser=container.get("omniparser") if container.has("omniparser") else None,
            uitars=ui_tars,
        )
        container.register("grounded_perception", grounded_perception)
        logger.info("grounded_perception_ready")
        
    except Exception as e:
        logger.warning("v11_services_failed", error=str(e))
    
    # Register grounding (whether v11 succeeded or not)
    if grounding:
        container.register("grounding", grounding)
        logger.info("grounding_ready", ui_tars=bool(ui_tars), ocr_fallback=bool(semantic_locator))
    
    # Hybrid Agent (v3.0) - replaces CognitiveAgent
    try:
        from app.agent.hybrid_agent import HybridAgent, AgentConfig
        
        # Create actuation interface for agent
        # Fix P22: DRY ActuationSystem Helper
        # Actuation helper is defined at module level
            
        actuation = create_actuation_system()
        if actuation:
            container.register("actuation", actuation)
        
        # Get LLM (Fix: retrieve 'llm' which is the registered provider/manager)
        llm_manager = container.get("llm") if container.has("llm") else None
        
        # Get vision system
        vision = container.get("vision") if container.has("vision") else None
        
        # Create agent configuration
        agent_config = AgentConfig(
            ui_tars_endpoint=settings.grounding.endpoint_url,
            ui_tars_api_key=settings.grounding.api_key or "",
            grounding_width=settings.grounding.grounding_width,
            grounding_height=settings.grounding.grounding_height,
            max_steps=settings.agent.max_iterations,
            action_timeout=settings.agent.action_timeout,
            max_trajectory_length=settings.agent.max_trajectory_length,
            enable_reflection=settings.agent.enable_reflection,
            enable_code_agent=settings.agent.enable_code_agent,
            mode=settings.agent.mode.value,
        )
        
        # Create hybrid agent
        agent = HybridAgent(
            config=agent_config,
            llm=llm_manager,
            actuation=actuation,
            vision=vision,
            memory=None,  # Can add memory system later
            planner=None,  # Can use HTN planner later
        )
        
        # Initialize agent components
        await agent.initialize()
        
        container.register("agent", agent)
        container.register("hybrid_agent", agent)  # Also register with v3 name
        logger.info(
            "hybrid_agent_ready",
            mode=settings.agent.mode.value,
            reflection=settings.agent.enable_reflection,
            code_agent=settings.agent.enable_code_agent,
        )
        
    except Exception as e:
        logger.error("hybrid_agent_init_failed", error=str(e))
        # Critical failure - do not fallback to legacy agent
        raise e
    
    logger.info("all_subsystems_initialized")


async def shutdown_subsystems() -> None:
    """Shutdown subsystems."""
    logger.info("shutting_down")
    
    # Stop Safety Monitor
    try:
        from app.core.safety_monitor import SafetyMonitor
        SafetyMonitor.stop()
    except:
        pass
    
    if container.has("agent"):
        agent = container.get("agent")
        if hasattr(agent, 'stop'):
            await agent.stop()
    
    if container.has("llm"):
        llm = container.get("llm")
        if hasattr(llm, 'unload'):
            await llm.unload()
    
    container.clear()
    logger.info("shutdown_complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    configure_logging(settings.monitoring.log_level.value)
    logger.info("oni_starting", version=settings.app_version)
    
    # Initialize Cognitive Memory (Fix 5)
    try:
        from app.services.oni import CognitiveMemoryService
        CognitiveMemoryService.init_db()
        logger.info("cognitive_memory_initialized")
    except Exception as e:
        logger.error("cognitive_memory_init_failed", error=str(e))

    # FUTUROSOUL: Context Infinite (Memory Persistence)
    try:
        from app.services.session_manager import get_session_manager
        session = get_session_manager()
        ctx = session.get_context()
        logger.info("context_infinite_loaded", persona=ctx.get("persona"), summary=ctx.get("context_summary"))
    except Exception as e:
        logger.error("session_manager_init_failed", error=str(e))


    # Safety Monitor (Priority High)
    try:
        from app.core.safety_monitor import SafetyMonitor
        SafetyMonitor.start_listening()
        logger.info("safety_monitor_initialized")
    except Exception as e:
        logger.error("safety_monitor_init_failed", error=str(e))

    await init_subsystems()
    
    logger.info("oni_ready", mode=settings.agent.mode.value)
    
    # Start Shared Vision Service
    from app.services.vision_shared import initialize_shared_vision, shutdown_shared_vision
    await initialize_shared_vision()
    
    # Start Process Sentinel Background Task
    from app.core.process_sentinel import sentinel
    import asyncio
    
    async def sentinel_background_loop():
        while True:
            await asyncio.sleep(300) # Scan every 5 minutes
            try:
                sentinel.scan_and_purge()
            except Exception as e:
                logger.error("sentinel_scan_failed", error=str(e))
    
    asyncio.create_task(sentinel_background_loop())
    
    yield
    
    await shutdown_shared_vision()
    await shutdown_subsystems()
    # Final emergency purge on shutdown
    # DISABLED: This was killing ALL processes including VS Code and Photoshop (ERR-016)
    # try:
    #     sentinel.emergency_purge_automation()
    # except:
    #     pass
    
    # Save Final Session Context
    try:
        from app.services.session_manager import get_session_manager
        get_session_manager().save_session({"system_status": "shutdown_clean"})
        logger.info("context_infinite_saved")
    except Exception as e:
        logger.error("session_save_failed", error=str(e))

    logger.info("oni_stopped")


def create_application() -> FastAPI:
    """Create FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="OMEGA NEURAL INTERFACE - Cognitive Desktop Automation",
        lifespan=lifespan,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware: Focus Validation (Fix 3)
    @app.middleware("http")
    async def verify_focus(request: Request, call_next):
        if "action" in request.url.path and request.method == "POST":
            expected_app = request.headers.get("X-Expected-App")
            if expected_app:
                try:
                    from app.infrastructure.actuation.window_manager import WindowManager
                    active = await WindowManager.get_active_window_info()
                    if active and expected_app.lower() not in active.get('title', '').lower():
                        logger.warning("focus_mismatch", expected=expected_app, actual=active.get('title'))
                        # Fix P23: Enforce Focus Validation
                        from fastapi import HTTPException
                        raise HTTPException(409, f"Wrong app in focus. Expected '{expected_app}', got '{active.get('title')}'") 
                except Exception as e:
                    logger.error("focus_check_failed", error=str(e))
        response = await call_next(request)
        return response
    
    # Static files
    static_path = Path(__file__).parent.parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Routes
    from app.api.routes import health, agent
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(agent.router, prefix="/api/v1/agent", tags=["Agent"])
    # app.include_router(vision.router, prefix="/api/v1/vision", tags=["Vision"]) # Fix P18: Deleted

    # Natural Language API (Sprint 7)
    from app.api.routes import natural_language
    app.include_router(natural_language.router, prefix="/api/v1", tags=["NaturalLanguage"])

    # Onihand API (Innovation)
    from app.api.routes import onihand
    app.include_router(onihand.router, prefix="/api/v1/onihand", tags=["Onihand"])
    
    # ONI API - REST endpoints for external AI brain
    from app.api.routes import oni
    app.include_router(oni.router, prefix="/api", tags=["ONI"])

    # Photoshop API
    from app.api.routes import photoshop
    app.include_router(photoshop.router, prefix="/api/photoshop", tags=["Photoshop"])
    
    # Blender API
    from app.api.routes.oni import blender as oni_blender
    app.include_router(oni_blender.router, prefix="/api/blender", tags=["Blender"])

    # CorelDRAW API
    from app.api.routes import corel
    app.include_router(corel.router, prefix="/api/corel", tags=["CorelDRAW"])

    # Segmentation API (scikit-image)
    from app.api.routes import segmentation
    app.include_router(segmentation.router, tags=["Segmentation"])

    # v3 Grounding API (v11.0 Anti-Hallucination)
    # from app.api.routes.oni.v3_grounding import router as v3_router
    # app.include_router(v3_router, prefix="/api/v3", tags=["v3-Grounding"])

    # Exception Handlers (ONI Panic System)
    from app.infrastructure.monitoring.exception_handlers import oni_error_handler, general_exception_handler
    from app.core.exceptions import ONIError
    app.add_exception_handler(ONIError, oni_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # v23.0 Cognitive Middlewares - Anti Memória Episódica
    try:
        from app.infrastructure.middleware.cognitive_middleware import register_cognitive_middlewares
        register_cognitive_middlewares(app)
        logger.info("cognitive_middlewares_registered")
    except Exception as e:
        logger.warning("cognitive_middlewares_failed", error=str(e))

    
    # WebSocket
    from app.api.websocket import websocket_endpoint
    # Fix P24: Correct WebSocket Route Registration
    app.websocket("/ws/neural")(websocket_endpoint)
    
    # Dashboard
    @app.get("/")
    async def serve_dashboard():
        index_path = static_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"status": "ONI v2.0 API", "dashboard": "/static/index.html"}
    
    return app


# Create app instance
app = create_application()
# ONI Server Reload Trigger: 2026-01-21 20:20
# V24 Hunter Service Active (Recursive Scan + Reveal All)4
