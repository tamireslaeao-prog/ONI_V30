# 🌐 CHROME KNOWLEDGE BASE

> **Módulo:** Modules/Chrome
> **Versão:** V24
> **Status:** CDP Ready

---

## 🎯 Quick Commands

### Atalhos de Navegador
| Ação | Atalho |
|------|--------|
| Nova aba | Ctrl+T |
| Fechar aba | Ctrl+W |
| Atualizar | F5 |
| DevTools | F12 |
| Barra de URL | Ctrl+L |

### Comandos Bridge (CDP)
```javascript
// Via Chrome DevTools Protocol
await ONI.Chrome.goto("https://example.com");
await ONI.Chrome.click("#button");
await ONI.Chrome.type("#input", "texto");
await ONI.Chrome.screenshot("output.png");
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI.Chrome.js` - API CDP completa (15KB)
- `Scripts/ONI_Chrome_Controller.ps1`
- `Scripts/ONI_Chrome_Harvester.ps1`
- `Scripts/ONI_Chrome_Scraper.ps1`

### Módulos da API
- **Core:** connect, disconnect, evaluate
- **Navegador:** launch, close, getVersion
- **Abas:** newTab, closeTab, switchTab
- **Páginas:** goto, reload, waitFor
- **Captura:** screenshot, pdf
- **Storage:** cookies, localStorage, sessionStorage
- **Network:** interceptRequest, getRequests
- **Automação:** click, type, scroll, hover

---

## 🎨 Assets Disponíveis

- `assets_db.json` - Banco de assets (1.6MB)
- Dados de bookmarks, extensões, histórico

---

## 💡 Dicas Avançadas

### CDP via WebSocket
```javascript
const ws = new WebSocket("ws://localhost:9222/devtools/browser");
ws.send(JSON.stringify({
    id: 1,
    method: "Page.navigate",
    params: { url: "https://example.com" }
}));
```

### Headless Mode
```powershell
chrome.exe --headless --remote-debugging-port=9222
```

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| Connection refused | Chrome não iniciou com --remote-debugging-port |
| Element not found | Usar waitForSelector antes do click |
| Timeout | Aumentar tempo de espera |
