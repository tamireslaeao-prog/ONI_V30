# 🌐 EDGE KNOWLEDGE BASE

> **Módulo:** Modules/Edge
> **Versão:** V24
> **Status:** Browser Ready

---

## 🎯 Quick Commands

### Atalhos de Navegador
| Ação | Atalho |
|------|--------|
| Nova aba | Ctrl+T |
| Fechar aba | Ctrl+W |
| DevTools | F12 |
| Barra de URL | Ctrl+L |
| Coleções | Ctrl+Shift+Y |

### Comandos Bridge (CDP)
```javascript
// Via Chrome DevTools Protocol (compatível)
await ONI.Edge.goto("https://example.com");
await ONI.Edge.screenshot("output.png");
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI.Edge.js` - API CDP (19KB)
- `Scripts/ONI_Edge_Harvester.ps1`
- `Scripts/ONI_Edge_Launcher.ps1`
- `Scripts/ONI_Edge_Sentinel.ps1`

### Capacidades
- Mesmas do Chrome (CDP compatível)
- Suporte nativo Windows
- Integração com Microsoft 365

---

## 💡 Dicas Avançadas

### Edge Headless
```powershell
msedge.exe --headless --remote-debugging-port=9222
```

### IE Mode
Edge suporta modo compatibilidade com IE para sites legados.

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| CDP não conecta | Iniciar com --remote-debugging-port |
