# 🎨 PHOTOSHOP BRIDGE V2 - IMPLEMENTATION PLAN
> **Versão:** 2.0  
> **Data:** 2026-01-21  
> **Autor:** ANT (Google DeepMind Mode)  
> **Status:** 🔴 PLANNING

---

## 📋 CONTEXTO

### O Que Existe Hoje
```
app/api/routes/photoshop.py     → 3 endpoints básicos
app/services/photoshop_service.py → COM Bridge via win32com
```

### Endpoints Atuais
1. `POST /api/photoshop/connect` - Conectar ao Photoshop
2. `POST /api/photoshop/command` - Comandos genéricos (create_doc, set_color)
3. `POST /api/photoshop/draw/stroke` - Desenhar paths via JavaScript

### O Que Falta (Crítico para Automação)
- ❌ Listagem de layers
- ❌ Seleção de layers
- ❌ Abertura de Smart Objects
- ❌ Substituição de texto
- ❌ Execução de JSX arbitrário

---

## 🎯 NOVOS ENDPOINTS PROPOSTOS

### Tier 1: Críticos (Layer Management)

#### 1. `GET /api/photoshop/layers`
**Descrição:** Lista todas as layers do documento ativo
**Response:**
```json
{
  "success": true,
  "document": "ONI_HARVEST_TARGET.psd",
  "layers": [
    {"index": 0, "name": "Background", "kind": "NORMAL", "visible": true},
    {"index": 1, "name": "Ramadan", "kind": "SMARTOBJECT", "visible": true},
    {"index": 2, "name": "Effects", "kind": "GROUP", "visible": true}
  ]
}
```

#### 2. `POST /api/photoshop/layers/select`
**Descrição:** Seleciona layer por nome ou índice
**Body:**
```json
{"name": "Ramadan"} 
// ou
{"index": 1}
```

#### 3. `POST /api/photoshop/smart-object/open`
**Descrição:** Abre o Smart Object selecionado (equivalente a double-click)
**Response:**
```json
{
  "success": true,
  "opened_file": "@Ramadan.psb",
  "message": "Smart Object opened for editing"
}
```

#### 4. `POST /api/photoshop/smart-object/close`
**Descrição:** Salva e fecha o .psb atual, retornando ao documento pai
**Response:**
```json
{
  "success": true,
  "saved": true,
  "returned_to": "ONI_HARVEST_TARGET.psd"
}
```

---

### Tier 2: Importantes (Text & Document)

#### 5. `POST /api/photoshop/text/replace`
**Descrição:** Substitui texto em layer de texto ou Smart Object
**Body:**
```json
{
  "layer_name": "Title",  // opcional se layer já selecionada
  "old_text": "Ramadan",
  "new_text": "ONI"
}
```

#### 6. `GET /api/photoshop/document/info`
**Descrição:** Informações do documento ativo
**Response:**
```json
{
  "name": "file.psd",
  "width": 1920,
  "height": 1080,
  "path": "C:/path/to/file.psd",
  "saved": false
}
```

#### 7. `POST /api/photoshop/document/save`
**Descrição:** Salva documento atual (Ctrl+S equivalente)

---

### Tier 3: Flexíveis (Power User)

#### 8. `POST /api/photoshop/execute-jsx`
**Descrição:** Executa código JavaScript/ExtendScript arbitrário
**Body:**
```json
{
  "script": "app.activeDocument.artLayers[0].name = 'NewName';"
}
```
**Response:**
```json
{
  "success": true,
  "result": "Script executed",
  "return_value": null
}
```

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### PhotoshopService (Extensão)

```python
# Adicionar a app/services/photoshop_service.py

def get_layers(self) -> list:
    """Lista todas as layers do documento ativo."""
    self.ensure_connection()
    doc = self.app.ActiveDocument
    layers = []
    
    def recurse_layers(layer_set, depth=0):
        for layer in layer_set:
            kind = "SMARTOBJECT" if layer.Kind == 17 else \
                   "TEXT" if layer.Kind == 2 else \
                   "GROUP" if hasattr(layer, 'Layers') else "NORMAL"
            layers.append({
                "name": layer.Name,
                "kind": kind,
                "visible": layer.Visible,
                "bounds": list(layer.Bounds) if hasattr(layer, 'Bounds') else None
            })
            if hasattr(layer, 'Layers'):
                recurse_layers(layer.Layers, depth+1)
    
    recurse_layers(doc.Layers)
    return layers

def select_layer(self, name: str = None, index: int = None):
    """Seleciona layer por nome ou índice."""
    self.ensure_connection()
    doc = self.app.ActiveDocument
    
    if name:
        layer = doc.ArtLayers[name]  # ou busca recursiva
    elif index is not None:
        layer = doc.ArtLayers[index]
    else:
        raise ValueError("Provide name or index")
    
    doc.ActiveLayer = layer
    return layer.Name

def open_smart_object(self):
    """Abre Smart Object selecionado para edição."""
    self.ensure_connection()
    # Via JavaScript (melhor suporte)
    js = """
    var idplacedLayerEditContents = stringIDToTypeID("placedLayerEditContents");
    executeAction(idplacedLayerEditContents, undefined, DialogModes.NO);
    app.activeDocument.name;
    """
    result = self.app.DoJavaScript(js)
    return result

def close_smart_object(self):
    """Salva e fecha o Smart Object (.psb)."""
    self.ensure_connection()
    doc = self.app.ActiveDocument
    doc.Save()
    doc.Close()
    return self.app.ActiveDocument.Name

def replace_text(self, layer_name: str, old_text: str, new_text: str):
    """Substitui texto em layer de texto."""
    self.ensure_connection()
    js = f"""
    var layer = app.activeDocument.artLayers.getByName("{layer_name}");
    if (layer.kind == LayerKind.TEXT) {{
        var contents = layer.textItem.contents;
        layer.textItem.contents = contents.replace("{old_text}", "{new_text}");
    }}
    layer.textItem.contents;
    """
    return self.app.DoJavaScript(js)

def execute_jsx(self, script: str):
    """Executa script JSX arbitrário."""
    self.ensure_connection()
    return self.app.DoJavaScript(script)
```

### Routes (Extensão)

```python
# Adicionar a app/api/routes/photoshop.py

@router.get("/layers")
async def get_layers():
    """List all layers in active document."""
    service = container.get("photoshop_service")
    return {"success": True, "layers": service.get_layers()}

@router.post("/layers/select")
async def select_layer(name: str = None, index: int = None):
    service = container.get("photoshop_service")
    selected = service.select_layer(name=name, index=index)
    return {"success": True, "selected": selected}

@router.post("/smart-object/open")
async def open_smart_object():
    service = container.get("photoshop_service")
    opened = service.open_smart_object()
    return {"success": True, "opened_file": opened}

@router.post("/smart-object/close")
async def close_smart_object():
    service = container.get("photoshop_service")
    returned = service.close_smart_object()
    return {"success": True, "returned_to": returned}

@router.post("/text/replace")
async def replace_text(layer_name: str, old_text: str, new_text: str):
    service = container.get("photoshop_service")
    result = service.replace_text(layer_name, old_text, new_text)
    return {"success": True, "new_text": result}

@router.get("/document/info")
async def get_document_info():
    service = container.get("photoshop_service")
    service.ensure_connection()
    doc = service.app.ActiveDocument
    return {
        "success": True,
        "name": doc.Name,
        "width": doc.Width,
        "height": doc.Height,
        "path": doc.FullName if doc.Saved else None,
        "saved": doc.Saved
    }

@router.post("/document/save")
async def save_document():
    service = container.get("photoshop_service")
    service.ensure_connection()
    service.app.ActiveDocument.Save()
    return {"success": True}

@router.post("/execute-jsx")
async def execute_jsx(script: str):
    service = container.get("photoshop_service")
    result = service.execute_jsx(script)
    return {"success": True, "result": str(result)}
```

---

## 📊 PRIORIDADE DE IMPLEMENTAÇÃO

| # | Endpoint | Impacto | Esforço | Prioridade |
|---|----------|---------|---------|------------|
| 1 | `/layers` | ALTO | Baixo | 🔴 P0 |
| 2 | `/layers/select` | ALTO | Baixo | 🔴 P0 |
| 3 | `/smart-object/open` | ALTO | Médio | 🔴 P0 |
| 4 | `/smart-object/close` | ALTO | Baixo | 🔴 P0 |
| 5 | `/text/replace` | ALTO | Médio | 🟠 P1 |
| 6 | `/document/info` | Médio | Baixo | 🟡 P2 |
| 7 | `/document/save` | Médio | Baixo | 🟡 P2 |
| 8 | `/execute-jsx` | FLEX | Baixo | 🟢 P3 |

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Estender `photoshop_service.py` com novos métodos
- [ ] Adicionar rotas em `photoshop.py`
- [ ] Testar conexão COM
- [ ] Testar cada endpoint individualmente
- [ ] Atualizar `API_REGISTRY.md`
- [ ] Criar testes automatizados

---

## 🎯 CASO DE USO: SMART OBJECT TEXT REPLACEMENT

```python
# Workflow completo para trocar "Ramadan" → "ONI"

# 1. Listar layers
GET /api/photoshop/layers
→ Encontrar "Ramadan" (kind: SMARTOBJECT)

# 2. Selecionar layer
POST /api/photoshop/layers/select?name=Ramadan

# 3. Abrir Smart Object
POST /api/photoshop/smart-object/open
→ Abre .psb com texto plano

# 4. Substituir texto (se for layer de texto)
POST /api/photoshop/text/replace?layer_name=Title&old_text=Ramadan&new_text=ONI

# OU se for seleção direta:
# Ctrl+A, digitar "ONI"
GET /api/keys?keys=ctrl,a
GET /api/type?text=ONI

# 5. Salvar e fechar Smart Object
POST /api/photoshop/smart-object/close

# 6. Salvar documento principal
POST /api/photoshop/document/save
```

---

**APROVAÇÃO NECESSÁRIA PARA IMPLEMENTAR** 🚦
