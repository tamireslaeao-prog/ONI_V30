# 🎬 AFTER EFFECTS KNOWLEDGE BASE

> **Módulo:** Modules/AfterEffects
> **Versão:** V24
> **Status:** Golden Standard

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Atalho |
|------|--------|
| Nova composição | Ctrl+N |
| Render Queue | Ctrl+Shift+/ |
| Preview RAM | 0 (numpad) |
| Keyframe | Alt+Click na propriedade |

### Comandos Bridge
```powershell
# Via aerender.exe (CLI)
& "C:\Program Files\Adobe\After Effects 2025\aerender.exe" -project "file.aep" -comp "Main" -output "out.mp4"

# Via Startup Injection (Nuclear Option)
Copy-Item "script.jsx" "$env:APPDATA\Adobe\After Effects\2025\Scripts\Startup\"
Start-Process "AfterFX.exe"
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `oni_lib_aftereffects.jsx` - Biblioteca ExtendScript (453 linhas)
- `ONI.AfterEffects.Automation.ps1` - PowerShell module (610 linhas)
- `oni_ae_bridge.py` - Python bridge
- `ae_styles_db.json` - Estilos

### Métodos de Automação

#### V4: Process-Aware Injection
```powershell
& AfterFX.exe -m -r "script.jsx"
```
- Pros: Confiável para one-off
- Cons: Reinicia AE a cada script

#### V5: Hybrid Engine (Static Library)
- Biblioteca `ONI_AE_Library.jsx` com 60+ helpers
- PowerShell gera payload JSX pequeno que carrega biblioteca

#### V6: Startup Injection ☢️ (Nuclear Option)
1. Copiar JSX para `Scripts\Startup\`
2. Iniciar AfterFX.exe
3. Script executa automaticamente
4. Self-destruct: `new File($.fileName).remove()`

---

## 🎨 Assets Disponíveis

**Localização:** `Modules/AfterEffects/`

- `ae_styles_db.json` - Banco de estilos (13KB)
- `Scripts/ONI_AEP_Harvester.ps1`
- `templates/` - Templates prontos
- `Assets/` - Assets diversos

---

## 💡 Dicas Avançadas

### Self-Destruct Pattern
```javascript
try {
    // ... lógica ...
    app.project.save(File("output.aep"));
} catch(e) {
    alert(e);
} finally {
    new File($.fileName).remove();  // Auto-delete
}
```

### Flattening Pattern (PowerShell)
```powershell
$CleanExpr = $Expression -replace "`r`n", " " -replace "`n", " " -replace "'", "\\'"
```

### Módulos da Biblioteca
- **Core:** Init, Verify, Color helpers
- **Shapes:** CreateRect, CreateEllipse, paths
- **Text:** CreateText, styling
- **FX:** Blur, Noise, effects
- **Animation:** Keyframes, easing
- **Export:** render, output

---

## 🚨 Erros Conhecidos

| Erro | Causa | Solução |
|------|-------|---------|
| -r ignorado | Permissões | Usar Startup Injection |
| Script não executa | Startup folder errado | Verificar versão AE |
| SyntaxError em expressão | Newlines | Usar Flattening Pattern |
| COM não existe | AE não tem COM | Usar JSX/CLI |

---

## 📋 Desafio Único

After Effects **NÃO** expõe interface COM como Photoshop/AutoCAD.
- CLI é unidirecional (só lança processos)
- **Solução:** Startup Injection ou biblioteca JSX
