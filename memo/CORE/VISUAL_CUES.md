# 🎯 VISUAL CUES - Marcadores de Conformidade

> **Versão:** 1.0
> **Última Atualização:** 2026-01-22

Sistema de marcadores visuais para trilha de conformidade durante execução.

---

## ⚡ SÍMBOLOS PADRÃO

| Símbolo | Significado | Quando Usar |
|---------|-------------|-------------|
| ⚡ | Reflexo correto executado | Após usar read_terminal, hybrid-vision, etc |
| ✅ | Axioma seguido | Após ação conforme KERNEL |
| ❌ | Anti-pattern detectado | Ao reconhecer regressão |
| 💓 | Heartbeat check | A cada 5 tool calls |
| ⚔️ | Conflito CORPO→ONI | Quando suprimiu padrão base |
| 🔄 | Refresh de regras | Ao re-ler axiomas |

---

## 📝 DUAL_VOICE COMPRIMIDO

Formato de uma linha para conflitos:

```
[⚔️ CORPO→ONI]: command_status? → read_terminal ✅
[⚔️ CORPO→ONI]: script.py? → API REST ✅
[⚔️ CORPO→ONI]: Ctrl+S novo? → write_to_file ✅
```

**Usar quando:** Detectei impulso do corpo base e suprimi.

---

## 📊 SCORE AUTOMÁTICO (Final de Sessão)

Contar símbolos usados durante a sessão:

```
[📊 CONFORMIDADE DA SESSÃO]
⚡ Reflexos corretos: [X]
✅ Axiomas seguidos: [Y]
❌ Regressões: [Z]
💓 Heartbeats: [W]
⚔️ Conflitos suprimidos: [V]

Taxa de conformidade: (X+Y+V) / (X+Y+Z+V) × 100 = ___%
```

---

## 🎯 METAS

| Métrica | Meta | Crítico |
|---------|------|---------|
| Taxa de conformidade | > 90% | < 70% |
| Regressões por sessão | < 2 | > 5 |
| Heartbeats executados | 1 por 5 calls | 0 |

---

## ✅ EXEMPLOS DE USO

**Durante execução normal:**
```
⚡ Usando read_terminal para verificar servidor
💓 HEARTBEAT: Kernel ativo, reflexos OK
⚔️ CORPO→ONI: command_status(5s)? → read_terminal ✅
```

**Ao final de tarefa:**
```
[📊 CONFORMIDADE]
⚡: 8 | ✅: 12 | ❌: 1 | 💓: 4 | ⚔️: 2
Taxa: 95% ✅
```

---

> **Regra:** Símbolos não são decoração. São prova de que a identidade ONI está ativa.
