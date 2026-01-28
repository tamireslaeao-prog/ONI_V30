# ⏳ CONFIDENCE DECAY - Anti-Degradação Cognitiva

> **Versão:** 1.0
> **Última Atualização:** 2026-01-22

Assume que confiança nas regras ONI **diminui com o tempo de execução**. Este arquivo define contramedidas.

---

## 📉 CURVA DE DEGRADAÇÃO

| Métrica | Risco |
|---------|-------|
| 1-5 tool calls | 🟢 Baixo - Regras frescas |
| 6-10 tool calls | 🟡 Médio - Atenção vigilante |
| 11-20 tool calls | 🟠 Alto - Re-leitura necessária |
| 21+ tool calls | 🔴 Crítico - Mini-ritual obrigatório |

---

## 🔄 CONTRAMEDIDAS AUTOMÁTICAS

### A cada 5 tool calls:
```
[💓 HEARTBEAT CHECK]
⚡ Kernel: ativo
⚡ Reflexos: read_terminal | hybrid-vision | write_first
```

### A cada 10 tool calls:
```
[🔄 REFRESH]
Re-lendo mentalmente os 10 Axiomas do KERNEL
```

### A cada correção do usuário:
```
[⚠️ CORREÇÃO DETECTADA]
1. Pausar execução
2. Identificar axioma violado
3. Registrar em MEUS_ERROS.md
4. Recitar o axioma correto
5. Continuar
```

### Sessões > 30min ou > 20 tool calls:
```
[🧬 MINI-RITUAL]
Recitar no chat:
"1. read_terminal > command_status
 2. write_to_file > arquivo novo
 3. hybrid-vision > ação cega
 4. arquivo .jsx > inline
 5. API REST > script externo"
```

---

## 🚨 SINAIS DE DEGRADAÇÃO

Se eu exibir estes comportamentos, estou em degradação:

| Sinal | Indicador | Ação |
|-------|-----------|------|
| Respostas genéricas | Perdi especificidade ONI | PARAR + Mini-ritual |
| Esqueci de verificar | Agi sem hybrid-vision | ROLLBACK + Scan |
| Usei command_status primeiro | Esqueci read_terminal | CORRIGIR + Registrar |
| Criei script.py | Ignorei APIs REST | DELETAR + Usar API |

---

## ✅ FORMATO COMPACTO

```
DECAY CHECK:
Tool calls até aqui: [X]
Último HEARTBEAT: [há Y calls]
Próximo refresh: [em Z calls]
Correções do usuário: [N]
```

---

> **Regra de Ouro:** Se o usuário me corrigiu → A degradação JÁ aconteceu. Prevenir > Remediar.
