# ONI SKILL: NEURO-INTEGRATION (CorelDRAW)

> **Contexto:** Automação Profunda de CorelDRAW
> **Protocolo:** Neuro-Integration (Injeção de Atalhos XML)
> **Dependências:** `Install-CorelShortcuts.ps1`, `corel_shortcuts.json`

## 🧠 O Que É?
O protocolo **Neuro-Integration** é a capacidade do ONI de modificar o "cérebro" (Workspace) do CorelDRAW para criar seus próprios receptores de comando (Atalhos), em vez de depender apenas do que a interface gráfica mostra.

## 🛠️ Capacidades
1.  **Criação de Atalhos Invisíveis:** Mapeia comandos complexos (ex: Rastreio Detalhado) para teclas (`Ctrl+Shift+D`).
2.  **Bypass de Segurança:** Contorna a necessidade de interação visual ou permissões de VBA ao editar diretamente o `workspace.xml`.
3.  **Padronização de Ambiente:** Força qualquer computador a ter os mesmos atalhos que o ONI espera.

## 📋 Como Usar
### 1. Configuração
Adicione o GUID do comando em `app/config/corel_shortcuts.json`:
```json
{
    "name": "Meu Comando",
    "guid": "guid-do-corel-draw-ui-xml",
    "keys": "Ctrl+Shift+X"
}
```

### 2. Injeção
Execute o injetor via PowerShell:
```powershell
.\app\setup\Install-CorelShortcuts.ps1
```

### 3. Execução (Fallback)
Se a injeção de código (Nexus VBA) falhar, use o atalho via `WScript.Shell`:
```powershell
$wshell.SendKeys("^+x") # Ctrl+Shift+X
```

## ⚠️ Manutenção
- **Workspace Ativo:** O script tenta alterar o `_default.cdws` ou cria `ONI_Neural_v1.cdws`. O usuário deve importar se não for automático.
- **Conflitos:** Teclas já em uso serão sobrescritas. O ONI tem prioridade.

## 🧬 GUIDs Conhecidos (Mapeados)
- **Quick Trace (Detailed):** `21129FEE-F5C2-41bc-9B04-CB5D39CB3974` (`Ctrl+Shift+D`)
- **Convert to Bitmap:** `2962cd49-74fd-4848-8590-fcc6807f0396` (`Ctrl+Shift+B`)
