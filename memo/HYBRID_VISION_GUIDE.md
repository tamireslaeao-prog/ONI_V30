# 👁️ Sistema de Visão Híbrida (Hybrid Vision)

Implementado com sucesso no ecossistema ONI v121.
Este sistema combina Selenium (para DOM e Accessibility Tree) com a API do ONI.

## 📁 Arquivos Criados
1.  **Serviço:** `app/services/oni/hybrid_vision_service.py`
    *   Contém a lógica core (`HybridVisionService`).
    *   Gerencia o WebDriver (Chrome) automaticamente.
    *   Injeta Scripts JS para extração de dados.

2.  **Rota:** `app/api/routes/oni/hybrid.py`
    *   Expõe o endpoint `/api/hybrid/analyze`.

3.  **Registro:** Atualizado `app/api/routes/oni/__init__.py`.

## 🚀 Como Usar (Endpoint API)

O endpoint já está ativo (após restart do uvicorn):

**Request:**
`POST http://localhost:8000/api/hybrid/analyze?url=https://www.google.com&headless=true`

**Response (JSON):**
```json
{
  "url": "https://www.google.com",
  "title": "Google",
  "element_count": 45,
  "clickable_count": 12,
  "editable_count": 1,
  "scene_description": "Page 'Google' loaded...",
  "elements": [...]
}
```

## 💻 Como Usar (Localmente/Script)

Você pode importar e usar o serviço diretamente em outros scripts python:

```python
from app.services.oni.hybrid_vision_service import HybridVisionService

service = HybridVisionService(headless=False) # True para rodar invisível
try:
    result = service.analyze("https://www.google.com")
    print(f"Título: {result.title}")
    print(result.scene_description)
finally:
    service.close()
```

## 📦 Dependências Instaladas
*   `selenium`
*   `webdriver-manager` (Gerencia o ChromeDriver automaticamente)
