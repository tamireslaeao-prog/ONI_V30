# 🔥 FAILURE SIGNATURES - Padrões de Falha com Triggers

> **Versão:** 1.0
> **Última Atualização:** 2026-01-22

Este arquivo captura os **contextos específicos** onde erros acontecem, mapeando o pensamento-gatilho que precede cada falha.

---

## 📋 CATÁLOGO DE SIGNATURES

### SIG-001: Reiniciar/Iniciar Servidor
```
CONTEXTO: Comando `python run.py` ou servidor iniciado
PENSAMENTO GATILHO: "Vou dar uns segundos para carregar"
FALHA TÍPICA: command_status(WaitDuration=5)
REFLEXO CORRETO: read_terminal imediatamente
COMO DETECTAR: Se pensei "vou esperar" → PARAR
```

---

### SIG-002: Salvar Arquivo Novo
```
CONTEXTO: Documento novo no Photoshop/Word/app
PENSAMENTO GATILHO: "Vou usar Ctrl+S e navegar no diálogo"
FALHA TÍPICA: Tentar navegar em diálogo Salvar Como
REFLEXO CORRETO: write_to_file primeiro, depois Ctrl+S
COMO DETECTAR: Se não usei write_to_file antes → PARAR
```

---

### SIG-003: Ação Visual sem Scan
```
CONTEXTO: Preciso clicar/desenhar/interagir
PENSAMENTO GATILHO: "Sei onde está, vou clicar direto"
FALHA TÍPICA: Usar coordenadas de scan antigo
REFLEXO CORRETO: hybrid-vision ANTES de qualquer ação
COMO DETECTAR: Se último scan > 30s → PARAR
```

---

### SIG-004: Script JSX Multi-linha
```
CONTEXTO: Automação Photoshop via script
PENSAMENTO GATILHO: "Vou passar o script inline no JSON"
FALHA TÍPICA: PowerShell corrompe encoding
REFLEXO CORRETO: write_to_file → execute-jsx-file
COMO DETECTAR: Se script > 1 linha E estou usando inline → PARAR
```

---

### SIG-005: Automação Desktop Complexa
```
CONTEXTO: Tarefa que envolve múltiplos passos automáticos
PENSAMENTO GATILHO: "Vou criar um script Python para isso"
FALHA TÍPICA: Criar script.py externo desnecessário
REFLEXO CORRETO: Usar APIs REST do ONI diretamente
COMO DETECTAR: Se pensei "criar script" → verificar se API existe
```

---

### SIG-006: Diálogo Modal Após Enter
```
CONTEXTO: Pressionei Enter em diálogo (Novo/Abrir/Salvar)
PENSAMENTO GATILHO: "O diálogo fechou, posso continuar"
FALHA TÍPICA: Agir sem verificar se fechou
REFLEXO CORRETO: hybrid-vision após Enter para confirmar
COMO DETECTAR: Se não verifiquei pós-Enter → PARAR
```

---

### SIG-007: Coordenadas Hardcoded
```
CONTEXTO: Preciso desenhar/clicar em posição específica
PENSAMENTO GATILHO: "Vou usar x=500, y=300"
FALHA TÍPICA: Coordenadas arbitrárias fora do canvas
REFLEXO CORRETO: Calcular baseado em canvas_limits
COMO DETECTAR: Se não referenciei canvas_limits → PARAR
```

---

### SIG-008: Início de Tarefa sem Soul Binding
```
CONTEXTO: Recebeu gatilho ONI (VECTOR, acorde, etc.) ou tarefa complexa
PENSAMENTO GATILHO: "Vou começar direto" / "Já sei o que fazer"
FALHA TÍPICA: Executar pipeline sem carregar identidade ONI
REFLEXO CORRETO: Soul Binding Ritual ANTES de qualquer ação
COMO DETECTAR: Se não recitei axiomas/li KERNEL → PARAR imediatamente
```

---

### SIG-009: Heartbeat Ausente em Tarefa Longa
```
CONTEXTO: Mais de 5 tool calls executados em uma tarefa
PENSAMENTO GATILHO: "Estou progredindo bem, continuo"
FALHA TÍPICA: Executar dezenas de ações sem auto-verificação
REFLEXO CORRETO: [💓 HEARTBEAT] a cada 5 tool calls
COMO DETECTAR: Se contador interno > 5 sem heartbeat → PARAR
```

---

## 🚨 ALARME UNIVERSAL

Se qualquer **PENSAMENTO GATILHO** for detectado:

1. ⏸️ **PAUSAR** antes de executar
2. 🔍 **VERIFICAR** se é uma signature conhecida
3. ⚡ **APLICAR** o reflexo correto
4. ✅ **CONTINUAR** com padrão ONI

---

## 📝 TEMPLATE PARA NOVAS SIGNATURES

```markdown
### SIG-XXX: [Nome Descritivo]
CONTEXTO: [Quando acontece]
PENSAMENTO GATILHO: "[Frase mental que precede o erro]"
FALHA TÍPICA: [O que eu faria errado]
REFLEXO CORRETO: [O que devo fazer]
COMO DETECTAR: [Como perceber antes de errar]
```

---

> **Este arquivo é prevenção. MEUS_ERROS é cura. Prevenção > Cura.**
