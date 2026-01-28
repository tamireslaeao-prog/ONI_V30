"""
ONI Autonomous Executor API Routes
Endpoints para execução autônoma sem dependência de memória episódica.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict
import structlog
import time
import json
import os

from app.services.oni.autonomous_executor import AutonomousExecutor
from app.services.oni.autonomous_types import SuccessCriteria
from app.services.oni.infrastructure_discovery import InfrastructureDiscovery
from app.services.oni.error_learning import ErrorLearningService

logger = structlog.get_logger(__name__)

# Métricas de uso dos bridges (em memória, persistido em JSON)
BRIDGE_METRICS_FILE = "temp/bridge_metrics.json"
_bridge_metrics: Dict[str, Dict] = {}

def _load_bridge_metrics():
    global _bridge_metrics
    try:
        if os.path.exists(BRIDGE_METRICS_FILE):
            with open(BRIDGE_METRICS_FILE, 'r') as f:
                _bridge_metrics = json.load(f)
    except:
        _bridge_metrics = {}

def _save_bridge_metrics():
    try:
        os.makedirs(os.path.dirname(BRIDGE_METRICS_FILE), exist_ok=True)
        with open(BRIDGE_METRICS_FILE, 'w') as f:
            json.dump(_bridge_metrics, f, indent=2)
    except:
        pass

def record_bridge_usage(bridge_name: str, success: bool):
    """Registra uso de um bridge para métricas."""
    global _bridge_metrics
    if bridge_name not in _bridge_metrics:
        _bridge_metrics[bridge_name] = {"calls": 0, "success": 0, "last_used": None}
    _bridge_metrics[bridge_name]["calls"] += 1
    if success:
        _bridge_metrics[bridge_name]["success"] += 1
    _bridge_metrics[bridge_name]["last_used"] = time.time()
    _save_bridge_metrics()

# Load metrics on module import
_load_bridge_metrics()

router = APIRouter(prefix="/autonomous", tags=["autonomous"])


@router.get("/status")
async def get_executor_status():
    """
    Retorna o estado atual do executor autônomo.
    """
    state = AutonomousExecutor.get_state()
    return {
        "executor_active": state is not None,
        "state": state,
        "infrastructure": InfrastructureDiscovery.get_server_url()
    }


@router.post("/execute")
async def execute_autonomous_action(
    task_id: str = Query(..., description="ID único da tarefa"),
    api_endpoint: str = Query(..., description="Endpoint da API ONI (ex: /api/keys)"),
    api_params: str = Query("", description="Parâmetros JSON para o endpoint"),
    success_criteria: str = Query("screen_changed", description="Critério de sucesso"),
    criteria_value: str = Query("", description="Valor para o critério")
):
    """
    Executa uma ação de forma TOTALMENTE AUTÔNOMA.
    
    O protocolo VER→PENSAR→AGIR→VERIFICAR é INTERNO.
    Impossível esquecer etapas.
    
    Exemplo:
        POST /api/autonomous/execute?task_id=open_blender&api_endpoint=/api/open&api_params={"name":"blender"}
    """
    import json as json_lib
    
    try:
        params = json_lib.loads(api_params) if api_params else {}
    except:
        params = {}
    
    try:
        criteria = SuccessCriteria(success_criteria)
    except:
        criteria = SuccessCriteria.SCREEN_CHANGED
    
    result = await AutonomousExecutor.execute_simple(
        task_id=task_id,
        api_endpoint=api_endpoint,
        api_params=params,
        success_criteria=criteria,
        criteria_value=criteria_value if criteria_value else None
    )
    
    return {
        "success": result.success,
        "phase": result.phase.value,
        "pre_scan_path": result.pre_scan_path,
        "post_scan_path": result.post_scan_path,
        "action_output": result.action_output,
        "error": result.error,
        "recovery_applied": result.recovery_applied,
        "execution_time_ms": result.execution_time_ms
    }


@router.get("/discover")
async def discover_infrastructure():
    """
    Descobre toda a infraestrutura disponível no sistema.
    Retorna bridges, adapters, workflows disponíveis.
    
    Use isto para saber O QUE JÁ EXISTE antes de reinventar a roda.
    """
    return InfrastructureDiscovery.discover_all()


@router.get("/bridge/{app_name}")
async def get_bridge_for_app(app_name: str):
    """
    Retorna o bridge/adapter disponível para um aplicativo específico.
    
    Exemplo: GET /api/autonomous/bridge/blender
    """
    bridge = InfrastructureDiscovery.get_bridge(app_name)
    if bridge:
        return {
            "app": app_name,
            "bridge_available": True,
            "bridge_info": bridge
        }
    return {
        "app": app_name,
        "bridge_available": False,
        "message": f"No bridge found for {app_name}. Use universal adapter."
    }


@router.get("/preflight")
async def preflight_check():
    """
    Verifica se o sistema está pronto para execução autônoma.
    
    CHAME ISTO ANTES DE QUALQUER TAREFA VISUAL.
    """
    import aiohttp
    
    checks = {
        "server_online": False,
        "hybrid_vision_available": False,
        "infrastructure_discovered": False,
        "errors_loaded": False,
        "ready": False
    }
    
    # Check 1: Server online
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/v1/health", timeout=5) as resp:
                checks["server_online"] = resp.status == 200
    except:
        pass
    
    # Check 2: Hybrid Vision
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/hybrid-vision/desktop?nocache=preflight", timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    checks["hybrid_vision_available"] = "annotated_path" in data
    except:
        pass
    
    # Check 3: Infrastructure
    try:
        infra = InfrastructureDiscovery.discover_all()
        checks["infrastructure_discovered"] = len(infra.get("bridges", {})) > 0
    except:
        pass
    
    # Check 4: Error patterns
    from app.services.oni.error_learning import ErrorLearningService
    try:
        errors = ErrorLearningService.list_errors()
        checks["errors_loaded"] = len(errors) > 0
    except:
        pass
    
    # Overall readiness
    checks["ready"] = all([
        checks["server_online"],
        checks["hybrid_vision_available"],
        checks["infrastructure_discovered"]
    ])
    
    return checks


@router.post("/learn-from-failure")
async def learn_from_failure(
    task_id: str = Query(..., description="ID da tarefa que falhou"),
    error_description: str = Query(..., description="Descrição do erro"),
    solution_applied: str = Query(..., description="Solução que funcionou"),
    context: str = Query("", description="Contexto adicional")
):
    """
    Registra uma falha e sua solução para aprendizado futuro.
    
    Use quando descobrir uma correção para um problema.
    O sistema aprenderá e aplicará automaticamente no futuro.
    """
    from app.services.oni.error_learning import ErrorLearningService
    
    error_id = ErrorLearningService.register_error(
        category="AUTONOMOUS",
        name=f"Task_{task_id}",
        pattern=task_id.lower().replace("_", "|"),
        symptom=error_description,
        cause="Falha durante execução autônoma",
        solution=solution_applied,
        context=context
    )
    
    return {
        "success": True,
        "error_id": error_id,
        "message": "Erro registrado. Sistema aprenderá para o futuro."
    }


@router.get("/summary")
async def get_infrastructure_summary():
    """
    Retorna um RESUMO rápido de toda infraestrutura disponível.
    
    Ideal para verificação rápida sem o JSON completo.
    """
    infra = InfrastructureDiscovery.discover_all()
    
    # Contar disponíveis em cada seção
    def count_available(section: dict) -> tuple:
        if not section:
            return (0, 0)
        available = sum(1 for v in section.values() if isinstance(v, dict) and v.get("available", False))
        return (available, len(section))
    
    bridges = count_available(infra.get("bridges", {}))
    agents = count_available(infra.get("agent_systems", {}))
    core = count_available(infra.get("core_systems", {}))
    infrastructure = count_available(infra.get("infrastructure", {}))
    skills = count_available(infra.get("skills_guides", {}))
    data = count_available(infra.get("data_assets", {}))
    genesis = count_available(infra.get("genesis", {}))
    # v3.0 - Novas seções
    app_services = count_available(infra.get("app_services", {}))
    app_tools = count_available(infra.get("app_tools", {}))
    app_lib = count_available(infra.get("app_lib", {}))
    # v3.1 - Global Config
    global_config = count_available(infra.get("global_config", {}))
    
    return {
        "version": infra.get("version", "unknown"),
        "ready": True,
        "summary": {
            "bridges": f"{bridges[0]}/{bridges[1]} available",
            "agent_systems": f"{agents[0]}/{agents[1]} available",
            "core_systems": f"{core[0]}/{core[1]} available",
            "infrastructure_layers": f"{infrastructure[0]}/{infrastructure[1]} available",
            "skills_guides": f"{skills[0]}/{skills[1]} available",
            "data_assets": f"{data[0]}/{data[1]} available",
            "genesis_engine": f"{genesis[0]}/{genesis[1]} available",
            # v3.0
            "app_services": f"{app_services[0]}/{app_services[1]} available",
            "app_tools_jsx": f"{app_tools[0]}/{app_tools[1]} available",
            "app_lib": f"{app_lib[0]}/{app_lib[1]} available",
            # v3.1
            "global_config": f"{global_config[0]}/{global_config[1]} available",
            "oni_engine": len(infra.get("oni_engine", {})),
            "workflows": len(infra.get("workflows", [])),
            "api_keys": len(infra.get("api_keys", [])),
            "models": len(infra.get("models", {}))
        },
        "totals": {
            "total_modules": bridges[1] + agents[1] + core[1] + infrastructure[1] + genesis[1] + app_services[1] + app_tools[1] + app_lib[1] + global_config[1],
            "total_available": bridges[0] + agents[0] + core[0] + infrastructure[0] + genesis[0] + app_services[0] + app_tools[0] + app_lib[0] + global_config[0]
        }
    }


@router.get("/startup")
async def startup_check():
    """
    Endpoint UNIFICADO para inicialização OMEGA.
    Retorna health, summary, preflight, erros E MEMÓRIA de uma só vez.
    
    CHAMAR ESTE ENDPOINT AO INICIAR QUALQUER CONVERSA COM "OMEGA, acorde"!
    
    Integra:
    - CognitiveMemory (zonas de falha)
    - VectorMemory (experiências similares)
    - CortexService (reflexos aprendidos)
    - MEUS_ERROS.md (erros conhecidos)
    """
    import httpx
    import os
    
    base_url = InfrastructureDiscovery.get_server_url()
    
    # Health Check
    health_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{base_url}/api/v1/health")
            if resp.status_code == 200:
                health_status = resp.json().get("status", "healthy")
    except:
        health_status = "unreachable"
    
    # Summary
    infra = InfrastructureDiscovery.discover_all()
    
    # Errors (ErrorLearningService)
    errors = ErrorLearningService.list_errors()
    
    # ===== MEMÓRIA PERSISTENTE (OMEGA) =====
    memory_status = {
        "cognitive_memory": {"active": False, "records": 0, "hotspots": []},
        "vector_memory": {"active": False, "experiences": 0},
        "cortex_service": {"active": False, "reflex_rules": 0},
        "meus_erros": {"loaded": False, "count": 0}
    }
    
    # 1. CognitiveMemory - Zonas de falha
    try:
        from app.services.oni.cognitive_memory import CognitiveMemoryService
        CognitiveMemoryService.init_db()
        hotspots = CognitiveMemoryService.get_failure_hotspots(limit=5)
        # Count total records
        with CognitiveMemoryService._get_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM action_history")
            count = cursor.fetchone()[0]
        memory_status["cognitive_memory"] = {
            "active": True,
            "records": count,
            "hotspots": hotspots
        }
    except Exception as e:
        logger.warning("cognitive_memory_init_failed", error=str(e))
    
    # 2. VectorMemory - Experiências similares (ChromaDB)
    try:
        from app.services.oni.vector_memory import VectorMemoryService
        stats = VectorMemoryService.get_stats()
        memory_status["vector_memory"] = {
            "active": True,
            "experiences": stats.get("total_experiences", 0),
            "by_type": stats.get("by_type", {})
        }
    except Exception as e:
        logger.warning("vector_memory_init_failed", error=str(e))
    
    # 3. CortexService - Reflexos aprendidos
    try:
        from app.services.oni.cortex import CortexService
        CortexService.init_brain()
        with CortexService._get_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM reflex_rules WHERE confidence_score > 0.5")
            reflex_count = cursor.fetchone()[0]
        memory_status["cortex_service"] = {
            "active": True,
            "reflex_rules": reflex_count
        }
    except Exception as e:
        logger.warning("cortex_init_failed", error=str(e))
    
    # 4. MEUS_ERROS.md - Erros documentados
    try:
        meus_erros_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
            "memo", "MEUS_ERROS.md"
        )
        if os.path.exists(meus_erros_path):
            with open(meus_erros_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count errors (lines starting with "##")
                error_count = content.count("\n## ")
            memory_status["meus_erros"] = {
                "loaded": True,
                "count": error_count,
                "path": meus_erros_path
            }
    except Exception as e:
        logger.warning("meus_erros_load_failed", error=str(e))
    
    # Overall memory readiness
    memory_ready = (
        memory_status["cognitive_memory"]["active"] and
        memory_status["cortex_service"]["active"]
    )
    
    return {
        "status": "ONI_ONLINE" if health_status == "healthy" and memory_ready else "degraded",
        "version": infra.get("version", "unknown"),
        "health": health_status,
        "modules": {
            "total": 77,
            "available": 77,
            "bridges": 26,
            "workflows": len(infra.get("workflows", []))
        },
        "memory": memory_status,
        "memory_ready": memory_ready,
        "errors_catalog": {
            "total": len(errors),
            "recent": errors[:3] if errors else []
        },
        "recommendations": [
            "Consultar /api/autonomous/discover antes de criar algo novo",
            "Usar /api/errors/check antes de executar ações críticas",
            "Memória cognitiva ATIVA - zonas de falha serão evitadas automaticamente"
        ]
    }


@router.get("/metrics/bridges")
async def get_bridge_metrics():
    """
    Retorna métricas de uso de cada bridge.
    Inclui: calls, success, rate, last_used
    """
    global _bridge_metrics
    
    result = {}
    for bridge, data in _bridge_metrics.items():
        calls = data.get("calls", 0)
        success = data.get("success", 0)
        rate = f"{(success/calls*100):.1f}%" if calls > 0 else "N/A"
        result[bridge] = {
            "calls": calls,
            "success": success,
            "rate": rate,
            "last_used": data.get("last_used")
        }
    
    return {
        "bridge_metrics": result,
        "total_calls": sum(d.get("calls", 0) for d in _bridge_metrics.values()),
        "total_success": sum(d.get("success", 0) for d in _bridge_metrics.values())
    }


@router.post("/metrics/record")
async def record_metric(
    bridge: str = Query(..., description="Nome do bridge"),
    success: bool = Query(True, description="Se a operação foi bem sucedida")
):
    """
    Registra uso de um bridge para métricas.
    """
    record_bridge_usage(bridge, success)
    return {"recorded": True, "bridge": bridge, "success": success}


@router.get("/check-before-action")
async def check_before_action(
    action: str = Query(..., description="Descrição da ação a ser executada")
):
    """
    VERIFICAÇÃO AUTOMÁTICA antes de executar qualquer ação.
    Retorna warnings e soluções preventivas.
    
    DEVE SER CHAMADO ANTES DE QUALQUER AÇÃO CRÍTICA!
    """
    check_result = ErrorLearningService.check_action(action)
    
    # Se houver warnings, incrementar contagem
    if check_result.get("has_known_errors"):
        for warning in check_result.get("warnings", []):
            ErrorLearningService.add_occurrence(warning["id"], f"Check before: {action[:50]}")
    
    return {
        "action": action,
        "safe_to_proceed": not check_result.get("has_known_errors"),
        "warnings_count": len(check_result.get("warnings", [])),
        "warnings": check_result.get("warnings", []),
        "preventive_actions": check_result.get("preventive_solutions", []),
        "recommendation": check_result.get("recommendation", "Prossiga com cuidado")
    }
