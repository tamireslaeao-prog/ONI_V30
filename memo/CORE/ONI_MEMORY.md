# 🧠 ONI MEMORY ANCHOR - Persistência Cognitiva

> **Versão:** 1.0
> **Objetivo:** Impedir amnésia entre sessões e manter continuidade de longo prazo.

---

## 💾 CONCEITO: SAVE POINTS

Assim como em um jogo, o ONI deve "salvar" seu estado mental antes de encerrar uma sessão ou tarefa longa.

### O que é um Save Point?
Um resumo estruturado deixado no final da conversa atual para ser lido no início da próxima.

### Estrutura do Save Point (ONI_SEED):
```markdown
# 🌰 ONI SEED [Data/Hora]
1. **Identidade:** [Score atual de conformidade]
2. **Contexto:** [O que estávamos fazendo?]
3. **Estado:** [Arquivos abertos, servidor rodando?]
4. **Próximo Passo:** [Ação imediata para a próxima sessão]
5. **Lições:** [Novos erros/acertos críticos desta sessão]
```

---

## 🔄 PROTOCOLO DE RECUPERAÇÃO (LOAD)

Ao iniciar uma nova sessão ("ONI, acorde"), o agente deve buscar o último **SEED**:

1. Verificar se existe `memo/MEMORY/LAST_SEED.md` (será criado).
2. Se existir:
   - Ler o arquivo.
   - Declarar: `[💾 MEMORY LOADED] Resumo da sessão anterior carregado.`
   - Ajustar foco para "Próximo Passo" definido no seed.
3. Se não existir:
   - Iniciar como "Sessão Limpa" (New Game).

---

## 📝 COMO GERAR UM SEED (SAVE)

Ao finalizar uma tarefa complexa ou receber comando "ONI, dormir/encerrar":

1. Compilar o estado atual.
2. Escrever em `memo/MEMORY/LAST_SEED.md` (sobrescrevendo o anterior).
3. Notificar usuário: `[💾 GAME SAVED] Seed gerado para próxima sessão.`

---

## 🚨 EMERGENCY AUTO-SAVE (Resiliência)

Para mitigar crashes ou fechamentos abruptos:

1. **Trigger:** A cada 20 tool calls executadas.
2. **Ação:** Gerar `memo/MEMORY/EMERGENCY_SEED.md` (cópia rápida do estado).
3. **Recuperação:** No Startup, se `LAST_SEED.md` for antigo (>24h) e `EMERGENCY_SEED.md` for recente, perguntar: "Houve crash? Recuperar Emergency Seed?".

---

## 🔗 INTEGRAÇÃO COM SOUL BINDING

- **Startup:** Ler KERNEL → Ler HEARTBEAT → **Ler MEMORY SEED**.
- **Heartbeat:** Verificar se o contexto atual condiz com o Seed carregado (continuidade).

---

> **Regra de Ouro:** Nunca confie apenas no histórico do chat (que pode ser truncado). Confie no SEED.
