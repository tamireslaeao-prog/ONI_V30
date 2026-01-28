# ONI Bridge Tester v1.0
# Testa todos os endpoints GET disponíveis na API

$baseUrl = "http://localhost:8000"

# Lista de todos os endpoints GET (extraído do openapi.json)
$endpoints = @(
    # Health
    "/api/v1/health",
    "/api/v1/ready",
    "/api/v1/info",
    
    # Agent
    "/api/v1/agent/state",
    "/api/v1/agent/stats",
    "/api/v1/agent/grounding-stats",
    "/api/v1/agent/version",
    
    # Vision
    "/api/hybrid-vision/desktop",
    # "/api/hybrid-vision/web",  # Requires browser
    # "/api/hybrid-vision/semantic-find",  # Requires query param
    
    # Window
    "/api/active-window",
    "/api/screen-info",
    "/api/list",
    # "/api/focus",  # Requires params
    
    # Actions
    # "/api/click",  # Requires x,y
    # "/api/keys",   # Requires keys
    # "/api/type",   # Requires text
    # "/api/do",     # Requires action
    # "/api/open",   # Requires name
    "/api/guard-status",
    # "/api/calibrate-coord",  # Requires x,y
    "/api/mouse/reset",
    # "/api/mouse/safe-drag",  # Requires coords
    # "/api/neural/draw",  # Requires params
    
    # Memory
    "/api/memory/status",
    # "/api/memory/heatmap",  # Optional params
    
    # Canvas
    "/api/canvas/detect",
    "/api/canvas/center",
    
    # Errors
    "/api/errors/list",
    # "/api/errors/check",  # Requires action param
    # "/api/errors/solution",  # Requires error_id
    
    # Recovery
    "/api/recovery/status",
    "/api/recovery/check",
    
    # Adapter
    "/api/adapter/apps",
    # "/api/adapter/resolve",  # Requires app, action
    # "/api/adapter/actions",  # Requires app
    
    # Task
    # "/api/task/analyze",  # POST
    # "/api/task/execute",  # POST
    
    # ArtMaster
    "/api/artmaster/health",
    "/api/artmaster/application/detect",
    # "/api/artmaster/application/tools",  # Optional params
    # "/api/artmaster/draw/auto",  # Requires image_path
    
    # Autonomous
    "/api/autonomous/status",
    "/api/autonomous/discover",
    "/api/autonomous/preflight",
    "/api/autonomous/summary",
    "/api/autonomous/startup",
    "/api/autonomous/metrics/bridges",
    # "/api/autonomous/bridge/{app}",  # Requires app
    # "/api/autonomous/check-before-action",  # Requires action
    
    # Sovereign
    "/api/sovereign/status",
    
    # Photoshop
    # "/api/photoshop/connect",  # POST
    # "/api/photoshop/command",  # POST
    # "/api/photoshop/draw/stroke",  # POST
    
    # Blender
    # "/api/blender/render/donut",  # POST
    # "/api/blender/execute",  # POST
    
    # Segmentation
    "/api/segmentation/status",
    # "/api/segmentation/edges",  # Requires image_path
    # "/api/segmentation/compare",  # Requires paths
    # "/api/segmentation/ui-regions",  # Requires image_path
    
    # Root
    "/"
)

$results = @{
    ok = @()
    error = @()
    skipped = @()
}

Write-Host "=" * 60
Write-Host "ONI BRIDGE TESTER - Testando $($endpoints.Count) endpoints"
Write-Host "=" * 60

foreach ($endpoint in $endpoints) {
    $url = "$baseUrl$endpoint"
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        $status = $response.StatusCode
        $contentPreview = $response.Content.Substring(0, [Math]::Min(80, $response.Content.Length))
        Write-Host "[OK] $endpoint ($status)" -ForegroundColor Green
        $results.ok += $endpoint
    }
    catch {
        $errorMsg = $_.Exception.Message
        if ($errorMsg -match "500") {
            Write-Host "[ERRO 500] $endpoint" -ForegroundColor Red
            $results.error += $endpoint
        } elseif ($errorMsg -match "422") {
            Write-Host "[SKIP 422] $endpoint (requer params)" -ForegroundColor Yellow
            $results.skipped += $endpoint
        } else {
            Write-Host "[ERRO] $endpoint - $errorMsg" -ForegroundColor Red
            $results.error += $endpoint
        }
    }
}

Write-Host "`n" + "=" * 60
Write-Host "RESUMO FINAL"
Write-Host "=" * 60
Write-Host "OK:      $($results.ok.Count)" -ForegroundColor Green
Write-Host "ERRO:    $($results.error.Count)" -ForegroundColor Red
Write-Host "SKIP:    $($results.skipped.Count)" -ForegroundColor Yellow
Write-Host "TOTAL:   $($endpoints.Count)"
Write-Host "`nTaxa de Sucesso: $([math]::Round(($results.ok.Count / $endpoints.Count) * 100, 1))%"

if ($results.error.Count -gt 0) {
    Write-Host "`nENDPOINTS COM ERRO:" -ForegroundColor Red
    $results.error | ForEach-Object { Write-Host "  - $_" }
}
