# 🚀 TURBO MODE - CONFIGURAÇÃO PERMANENTE

> **Data:** 2026-01-02  
> **Status:** ✅ VALIDADO E FUNCIONANDO

---

## O que é o Turbo Mode?

Permite que comandos de terminal executem **automaticamente** sem pedir confirmação do usuário, quando o agente define `SafeToAutoRun: true`.

---

## Configuração Necessária

### 1. Arquivo `.vscode/settings.json`

Criar ou editar o arquivo `.vscode/settings.json` no root do projeto:

```json
{
  "gemini.autoApproveAllCommands": true
}
```

**Localização:** `  vscode\settings.json`

---

### 2. Workspace Trust (Opcional mas Recomendado)

1. Abrir VS Code no projeto
2. `Ctrl+Shift+P` → "Manage Workspace Trust"
3. Marcar o workspace como **Trusted**

---

## Como Funciona

| Condição | Auto-Run? |
|----------|-----------|
| `SafeToAutoRun: true` + Config ativada | ✅ Sim |
| `SafeToAutoRun: false` | ❌ Pede confirmação |
| Config desativada | ❌ Pede confirmação |

---

## Testes de Validação

Comandos usados para testar:

```powershell
# Teste 1 - Echo simples
echo "Teste 1 - Auto Run OK"

# Teste 2 - Segundo comando
echo "Teste 2 - Segundo comando"
```

**Resultado:** Ambos executaram sem prompt de confirmação ✅

---

## Notas Importantes

1. **Segurança:** Esta configuração confia no agente para determinar o que é seguro. O agente ainda avalia cada comando antes de marcar como `SafeToAutoRun: true`.

2. **Escopo:** A configuração é por **workspace** (projeto). Cada projeto precisa ter seu próprio `.vscode/settings.json`.

3. **PowerShell Aliases:** Evitar usar `curl` diretamente no PowerShell (é alias do `Invoke-WebRequest`). Usar `Invoke-RestMethod` ou chamar via `read_url_content`.

---

## Referência Cruzada

- Workflow principal: [WORKFLOW_UNIVERSAL.md](./WORKFLOW_UNIVERSAL.md)
- Regra de Ouro: `SafeToAutoRun: true` sempre que possível
