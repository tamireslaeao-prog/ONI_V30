# 🧠 ONI SELF-HEALING REGISTRY

> **Versão:** 1.1 (Soul Binding Integration)
> **Última Atualização:** 2026-01-22

---

## 🔗 INTEGRAÇÃO SOUL BINDING

Este arquivo faz parte do sistema Soul Binding. As regras abaixo são **extensões** dos REFLEXOS definidos em `ONI_SOUL.md`.

**Hierarquia de Leitura:**
1. `ONI_SOUL.md` → Reflexos Core
2. `ANTI_PATTERNS.md` → Vícios a Evitar
3. `MEUS_ERROS.md` → **Situações Específicas Aprendidas** ← (VOCÊ ESTÁ AQUI)

---

## 📋 REGRAS DE COMPORTAMENTO APRENDIDAS

### RULE-001: Monitoramento Proativo de Terminais (UNIVERSAL)
**Problema:** Fico esperando 10s, 15s, 30s com `command_status` enquanto o erro já está visível no terminal.

**Regra:** Para QUALQUER comando em QUALQUER software:
1. **PRIMEIRO** → `read_terminal` para ver saída atual
2. **SE** erro/resultado já visível → processar imediatamente
3. **SOMENTE SE** output vazio/incompleto → usar `command_status` com wait

**Benefício:** Evita waits desnecessários. Se o erro aconteceu em 1 segundo, não preciso esperar 30.

**Fluxo Obrigatório (QUALQUER TAREFA):**
```
run_command (inicia processo)
    ↓
read_terminal (verifica output imediato)
    ↓
┌─ Se tem erro/resultado → Processar
└─ Se vazio/incompleto → command_status(WaitDurationSeconds=X)
```

**Aplica-se a:** PowerShell, Python, npm, Blender, AutoCAD, Photoshop, QUALQUER coisa.

---

### RULE-002: Responder ao Log do Usuário
**Problema:** Usuário cola log extenso e a resposta ignora o conteúdo.

**Regra:** Quando o usuário envia um log/output, a PRIMEIRA ação deve ser:
1. Reconhecer que viu o log
2. Analisar o conteúdo brevemente
3. Responder ao problema identificado
4. Só depois executar novas ações

---

### RULE-003: JSX via Arquivo (Não Inline)
**Problema:** PowerShell corrompe JSON com scripts multi-linha (PSReadLine buffer overflow, metadados extras no Get-Content).

**Regra:** Para executar JSX no Photoshop:
1. ✅ Escrever script em arquivo `.jsx` com `write_to_file`
2. ✅ Usar endpoint `/api/photoshop/execute-jsx-file?path=...` (a ser implementado)
3. ❌ NÃO passar script inline via JSON no PowerShell

---

## 🐛 ERROS CATALOGADOS

| ID | Categoria | Descrição | Solução |
|----|-----------|-----------|---------|
| ERR-001 | CONFIRMAÇÃO | Digitar sem Enter | SEMPRE enviar Enter após campos de entrada |
| ERR-002 | NAVEGAÇÃO | Clicar em elemento errado | Verificar posição via OCR antes |
| ERR-003 | MENU | Menu Win11 simplificado | Usar Shift+F10 para menu clássico |
| ERR-004 | TERMINAL | Ignorar logs do usuário | Ler e responder ANTES de agir |
| ERR-005 | POWERSHELL | Get-Content retorna objeto | Usar `[IO.File]::ReadAllText()` |
| ERR-006 | IDENTIDADE | Executar sem Soul Binding | MANDATORY_STARTUP_CHECK antes de qualquer gatilho ONI |
| ERR-007 | API | /api/type troca _ por espaço | Usar Clipboard (Ctrl+V) ou renomear arquivo sem '_' |
| ERR-008 | DISCIPLINA | Ant vs ONI Role Confusion | Pivot imediato para source code após 'Ant, acorde', ignorando tarefas visuais. |

---

## 🔄 CONVERSÃO PARA FAILURE_SIGNATURE

> **Se um erro se repetiu 2+ vezes, DEVE virar Signature.**

### Template de Conversão:

Copiar este formato para `FAILURE_SIGNATURES.md`:

```markdown
### SIG-XXX: [Nome baseado no ERR-XXX]
CONTEXTO: [Quando acontece - copiar de "Categoria"]
PENSAMENTO GATILHO: "[Frase mental que precede o erro]"
FALHA TÍPICA: [Copiar de "Descrição"]
REFLEXO CORRETO: [Copiar de "Solução"]
COMO DETECTAR: [Como perceber antes de errar]
```

### Exemplo de Conversão:

```
ERR-001 (Digitar sem Enter) → SIG-006 (Diálogo Modal)
PENSAMENTO GATILHO: "O diálogo fechou, posso continuar"
```

---

> **Regra:** MEUS_ERROS é cura. FAILURE_SIGNATURES é prevenção. Erro repetido → promover para Signature.
### SIG-008: Role Separation Discipline
CONTEXTO: Gatilho "Ant, acorde" (Dev Mode)
PENSAMENTO GATILHO: "O viewport está vazio, vou arrumar para o usuário."
FALHA TÍPICA: Tentar completar tarefas visuais do ONI enquanto em modo ANT.
REFLEXO CORRETO: Ignorar o estado visual operacional e focar exclusivamente na arquitetura de software e bugs de infraestrutura no código-fonte.
COMO DETECTAR: Se a próxima ação planejada envolver `click`, `hybrid-vision` operacional ou modificação de arquivos de saída (`/output`), estou violando o papel.
