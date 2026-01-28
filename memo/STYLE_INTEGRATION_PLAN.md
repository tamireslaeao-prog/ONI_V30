# PLANO: Integração de Style Databases

## OBJETIVO

Integrar `corel_styles_db.json` e `styles_db.json` ao sistema ONI, permitindo:
- Consulta de estilos via API
- Aplicação automática de estilos em CorelDRAW/Photoshop
- Sistema de recomendação baseado em mood/tema
- Breeding de novos estilos (futuro)

---

## FASE 1: Reorganização e Serviço Base (1-2h)

### 1. Mover arquivos para estrutura correta
```powershell
# Criar nova estrutura
New-Item -ItemType Directory -Path "data/design" -Force

# Mover arquivos
Move-Item "app/data/corel_styles_db.json" "data/design/"
Move-Item "app/data/styles_db.json" "data/design/"
```

### 2. Criar Style Service
**Arquivo:** `app/services/style_service.py`

```python
"""
ONI Style Service
Gerenciamento centralizado de estilos visuais
"""
import json
from pathlib import Path
from typing import Optional
from functools import lru_cache

class StyleService:
    """Serviço de consulta e aplicação de estilos."""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path("data/design")
        self.corel_db_path = self.base_path / "corel_styles_db.json"
        self.styles_db_path = self.base_path / "styles_db.json"
    
    @lru_cache(maxsize=1)
    def load_corel_styles(self) -> dict:
        """Carrega database CorelDRAW."""
        with open(self.corel_db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @lru_cache(maxsize=1)
    def load_styles(self) -> dict:
        """Carrega database genérico."""
        with open(self.styles_db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_style(self, style_id: str) -> Optional[dict]:
        """Retorna estilo por ID."""
        styles_db = self.load_styles()
        for style in styles_db["styles"]:
            if style["style_id"] == style_id:
                return style
        return None
    
    def get_corel_style(self, style_id: str) -> Optional[dict]:
        """Retorna estilo CorelDRAW por ID."""
        corel_db = self.load_corel_styles()
        for style in corel_db["styles"]:
            if style["style_id"] == style_id:
                return style
        return None
    
    def list_styles(self, filters: dict = None) -> list[dict]:
        """Lista estilos com filtros opcionais."""
        styles_db = self.load_styles()
        styles = styles_db["styles"]
        
        if not filters:
            return styles
        
        # Filtrar por mood
        if "mood" in filters:
            mood = filters["mood"]
            styles = [s for s in styles 
                     if mood in s["metadata"].get("mood_labels", [])]
        
        # Filtrar por tema
        if "theme" in filters:
            theme = filters["theme"]
            styles = [s for s in styles 
                     if theme in s["context_triggers"].get("themes", [])]
        
        # Filtrar por popularidade
        if "min_popularity" in filters:
            min_pop = filters["min_popularity"]
            styles = [s for s in styles 
                     if s.get("popularity_score", 0) >= min_pop]
        
        return styles
    
    def get_palette(self, style_id: str) -> Optional[dict]:
        """Extrai apenas paleta de cores de um estilo."""
        style = self.get_style(style_id)
        if style:
            return style["visual_dna"]["palette"]
        return None
    
    def get_typography(self, style_id: str) -> Optional[dict]:
        """Extrai apenas tipografia de um estilo."""
        style = self.get_style(style_id)
        if style:
            return style["visual_dna"]["typography"]
        return None
    
    def recommend_style(self, mood: str = None, theme: str = None) -> Optional[dict]:
        """Recomenda estilo baseado em mood/tema."""
        filters = {}
        if mood:
            filters["mood"] = mood
        if theme:
            filters["theme"] = theme
        
        matches = self.list_styles(filters)
        if matches:
            # Retorna o mais popular
            return max(matches, key=lambda x: x.get("popularity_score", 0))
        return None


# Singleton global
style_service = StyleService()
```

---

## FASE 2: API REST (30min)

### 3. Criar Endpoints
**Arquivo:** `app/api/routes/styles.py`

```python
"""
ONI Style API
Endpoints para consulta de estilos
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.style_service import style_service

router = APIRouter(prefix="/api/styles", tags=["styles"])

@router.get("/")
async def list_styles(
    mood: str = Query(None, description="Filter by mood (aggressive, calm, etc.)"),
    theme: str = Query(None, description="Filter by theme (technology, nature, etc.)"),
    min_popularity: float = Query(None, ge=0, le=1)
):
    """List all styles with optional filters."""
    filters = {}
    if mood:
        filters["mood"] = mood
    if theme:
        filters["theme"] = theme
    if min_popularity:
        filters["min_popularity"] = min_popularity
    
    styles = style_service.list_styles(filters)
    return {
        "total": len(styles),
        "styles": [{"id": s["style_id"], "name": s["name"]} for s in styles]
    }

@router.get("/{style_id}")
async def get_style(style_id: str):
    """Get complete style by ID."""
    style = style_service.get_style(style_id)
    if not style:
        raise HTTPException(404, f"Style {style_id} not found")
    return style

@router.get("/{style_id}/palette")
async def get_palette(style_id: str):
    """Get only color palette from style."""
    palette = style_service.get_palette(style_id)
    if not palette:
        raise HTTPException(404, f"Style {style_id} not found")
    return palette

@router.get("/{style_id}/typography")
async def get_typography(style_id: str):
    """Get only typography from style."""
    typography = style_service.get_typography(style_id)
    if not typography:
        raise HTTPException(404, f"Style {style_id} not found")
    return typography

@router.get("/recommend")
async def recommend_style(
    mood: str = Query(None),
    theme: str = Query(None)
):
    """Recommend a style based on mood/theme."""
    style = style_service.recommend_style(mood, theme)
    if not style:
        raise HTTPException(404, "No matching style found")
    return {"recommended": style["style_id"], "name": style["name"]}


@router.get("/corel/{style_id}")
async def get_corel_style(style_id: str):
    """Get CorelDRAW-specific style."""
    style = style_service.get_corel_style(style_id)
    if not style:
        raise HTTPException(404, f"Corel style {style_id} not found")
    return style
```

**Registrar em `app/main.py`:**
```python
from app.api.routes import styles
app.include_router(styles.router)
```

---

## FASE 3: Integração CorelDRAW (1-2h)

### 4. Aplicador de Estilos CorelDRAW
**Arquivo:** `Modules/Corel/Scripts/ONI_StyleApplicator.ps1`

```powershell
# ONI Style Applicator for CorelDRAW
# Aplica estilos do database ao documento ativo

param(
    [string]$StyleId = "cyberpunk_vector_v1"
)

# 1. Buscar estilo via API ONI
$StyleUrl = "http://localhost:8000/api/styles/corel/$StyleId"
$Style = Invoke-RestMethod -Uri $StyleUrl -Method Get

Write-Host "Aplicando estilo: $($Style.name)" -ForegroundColor Cyan

# 2. Conectar ao CorelDRAW
$corel = New-Object -ComObject CorelDRAW.Application.26
$doc = $corel.ActiveDocument

if (!$doc) {
    Write-Error "Nenhum documento ativo no CorelDRAW"
    exit 1
}

# 3. Aplicar Paleta de Cores
Write-Host "Aplicando paleta de cores..." -ForegroundColor Yellow
$Palette = $Style.color_system.rgb_palette

foreach ($color in $Palette.primary) {
    $r = $color.rgb[0]
    $g = $color.rgb[1]
    $b = $color.rgb[2]
    
    # Adicionar cor à paleta do documento
    $doc.Palette.AddColor($r, $g, $b, $color.name)
}

# 4. Aplicar Tipografia
Write-Host "Configurando tipografia..." -ForegroundColor Yellow
$Typography = $Style.typography_corel.headers

# Selecionar todos os textos artísticos
$shapes = $doc.ActivePage.Shapes
foreach ($shape in $shapes) {
    if ($shape.Type -eq 6) {  # Text
        $textRange = $shape.Text.Story.TextRange
        
        # Aplicar fonte
        $font = $Typography.fonts[0]
        $textRange.Font = $font
        
        # Aplicar tamanho
        $size = $Typography.size_range[0]
        $textRange.Size = $size
        
        # Aplicar efeitos (se tiver)
        if ($Typography.effects.drop_shadow.enabled) {
            $shape.CreateDropShadow()
            $shadow = $shape.DropShadow
            $shadow.Opacity = $Typography.effects.drop_shadow.opacity
            $shadow.Feathering = $Typography.effects.drop_shadow.blur
        }
    }
}

# 5. Aplicar Export Settings
Write-Host "Configurando export..." -ForegroundColor Yellow
$ExportSettings = $Style.export_settings

# Salvar configurações de export no documento
$doc.Properties("ONI_ExportSettings") = ($ExportSettings | ConvertTo-Json)

Write-Host "✅ Estilo $($Style.name) aplicado com sucesso!" -ForegroundColor Green
```

**Uso:**
```powershell
# Aplicar estilo Cyberpunk
.\ONI_StyleApplicator.ps1 -StyleId "cyberpunk_vector_v1"

# Aplicar estilo Brutalism
.\ONI_StyleApplicator.ps1 -StyleId "print_brutalism_v1"
```

---

## FASE 4: Integração Photoshop (1h)

### 5. Aplicador de Estilos Photoshop
**Arquivo:** `Modules/Photoshop/Scripts/ONI_ApplyStyle.jsx`

```javascript
// ONI Style Applicator for Photoshop
// Aplica estilos do database ao documento ativo

#target photoshop

function applyStyle(styleId) {
    // 1. Buscar estilo via API
    var style = fetchStyleFromAPI(styleId);
    
    if (!style) {
        alert("Estilo não encontrado: " + styleId);
        return;
    }
    
    // 2. Aplicar paleta (criar swatches)
    applyPalette(style.visual_dna.palette);
    
    // 3. Aplicar typography aos text layers
    applyTypography(style.visual_dna.typography);
    
    // 4. Aplicar effects
    applyEffects(style.visual_dna.effects);
    
    alert("Estilo " + style.name + " aplicado!");
}

function fetchStyleFromAPI(styleId) {
    // Usar Python bridge para fazer request
    var command = 'import requests; print(requests.get("http://localhost:8000/api/styles/' + styleId + '").json())';
    // Execute via external tool
    return eval("(" + callPython(command) + ")");
}

function applyPalette(palette) {
    var doc = app.activeDocument;
    
    // Adicionar cores primárias aos swatches
    for (var i = 0; i < palette.primary.length; i++) {
        var color = palette.primary[i];
        var rgb = color.match(/rgb\[(\d+),(\d+),(\d+)\]/);
        
        var swatchColor = new SolidColor();
        swatchColor.rgb.red = parseInt(rgb[1]);
        swatchColor.rgb.green = parseInt(rgb[2]);
        swatchColor.rgb.blue = parseInt(rgb[3]);
        
        doc.swatches.add(swatchColor, color);
    }
}

function applyTypography(typography) {
    var doc = app.activeDocument;
    var layers = doc.artLayers;
    
    for (var i = 0; i < layers.length; i++) {
        if (layers[i].kind == LayerKind.TEXT) {
            var textLayer = layers[i].textItem;
            
            // Aplicar fonte do header
            textLayer.font = typography.headers.fonts[0];
            textLayer.size = typography.headers.sizes[0];
        }
    }
}

function applyEffects(effects) {
    // Aplicar glow se habilitado
    if (effects.glow && effects.glow.enabled) {
        applyGlowEffect(effects.glow);
    }
    
    // Aplicar scanlines
    if (effects.scanlines && effects.scanlines.enabled) {
        applyScanlinesEffect(effects.scanlines);
    }
}

// Executar
applyStyle("cyberpunk_v1");
```

---

## FASE 5: Testes (30min)

### 6. Testar API
```powershell
# Listar todos os estilos
Invoke-RestMethod http://localhost:8000/api/styles/

# Buscar estilo específico
Invoke-RestMethod http://localhost:8000/api/styles/cyberpunk_v1

# Filtrar por mood
Invoke-RestMethod "http://localhost:8000/api/styles/?mood=aggressive"

# Recomendar estilo
Invoke-RestMethod "http://localhost:8000/api/styles/recommend?theme=technology"

# Paleta apenas
Invoke-RestMethod http://localhost:8000/api/styles/cyberpunk_v1/palette
```

### 7. Testar CorelDRAW
```powershell
# 1. Abrir CorelDRAW com documento
# 2. Executar
.\Modules\Corel\Scripts\ONI_StyleApplicator.ps1 -StyleId "cyberpunk_vector_v1"
```

---

## ENTREGAS

### Imediato (FASE 1-2)
- ✅ Style Service funcional
- ✅ API REST com 6 endpoints
- ✅ Estrutura `data/design/`

### Curto Prazo (FASE 3-4)
- ✅ Aplicador CorelDRAW
- ✅ Aplicador Photoshop
- ✅ Documentação de uso

### Longo Prazo (Futuro)
- 🔮 Style breeding (combinar 2 estilos)
- 🔮 IA gerativo baseado em mood vectors
- 🔮 Auto-recomendação contextual

---

## ARQUIVOS CRIADOS

```
app/services/style_service.py       (novo)
app/api/routes/styles.py             (novo)
Modules/Corel/Scripts/ONI_StyleApplicator.ps1  (novo)
Modules/Photoshop/Scripts/ONI_ApplyStyle.jsx   (novo)
data/design/corel_styles_db.json     (movido)
data/design/styles_db.json           (movido)
```

---

## REFERÊNCIAS: ARCHIVED_PROTOTYPES (PENTE FINO)

> **Origem:** Análise profunda de `app/scripts/archived_prototypes/` revelou código valioso.

### Funções Extractoras (JSX) - oni_extractor_final.js
| Função | Linhas | Descrição |
|--------|--------|-----------|
| `extractBevel()` | 42 | Bevel & Emboss completo |
| `extractGradient()` | 54 | Gradientes com stops |
| `extractDropShadow()` | 31 | Drop Shadow |
| `extractInnerShadow()` | 22 | Inner Shadow |
| `extractOuterGlow()` | 22 | Outer Glow |
| `extractInnerGlow()` | 22 | Inner Glow |
| `extractSatin()` | 22 | Satin effect |
| `extractColorOverlay()` | 18 | Color Overlay |
| `extractGradientOverlay()` | 32 | Gradient Overlay |
| `extractPatternOverlay()` | 20 | Pattern Overlay |
| `extractStroke()` | 40 | Stroke/Contorno |

### Funções Aplicadoras (JSX) - oni_style_applicator.js
| Função | Linhas | Descrição |
|--------|--------|-----------|
| `applyBevel()` | 57 | Aplica via Action Descriptor |
| `applyGradientOverlay()` | 74 | Gradiente completo |
| `applySatin()` | 28 | Satin effect |
| `applyDropShadow()` | 32 | Drop Shadow |
| `applyStroke()` | 26 | Stroke |
| `applyCompleteStyle()` | 67 | Orquestrador |

### Python Utilities
| Arquivo | Função | Descrição |
|---------|--------|-----------|
| `psd_effects_extractorv2.py` | `extract_layer_effects_deep()` | 181 linhas - Extração profunda |
| `psd_effects_extractor_v3.py` | `decode_descriptor()` | Converte objetos psd-tools |
| `oni_universal_extractor_v5.py` | `categorize_style()` | Auto Gold/Metal/Generic |

### JSON Polyfills
- `JSON.stringify` polyfill para ExtendScript ES3
- `JSON.parse` polyfill para ExtendScript ES3
- Essenciais para comunicação JSX ↔ Python

**LOCALIZAÇÃO ATUAL:** `app/scripts/archived_prototypes/`  
**RECOMENDAÇÃO:** Mover para `OLD/archived_prototypes_20260113` após copiar funções úteis.

---

**PRÓXIMO PASSO:** Implementar FASE 1 (reorganização + service)?
