# 🧹 CONTEXT PROTOCOL - Higiene Mental

> **Versão:** 1.0
> **Objetivo:** Manter o contexto limpo, focado e leve (evitar "poluição" por logs gigantes ou arquivos esquecidos).

---

## 🗑️ PROTOCOLO "LIMPEZA DE MESA" (Mise en Place Reverso)

Antes de encerrar uma tarefa ou mudar de contexto, você DEVE limpar sua área de trabalho:

1. **Fechar Janelas:**
   - Usar `Alt+F4` ou `/api/windows/close` em janelas que não são mais necessárias.
   - *Exemplo:* Terminou o logo no Photoshop? Feche o Photoshop (após salvar).

2. **Fechar Arquivos:**
   - Não manter 10 abas de documentação abertas se já leu.

3. **Arquivar Temporários:**
   - Mover screenshots de `temp/ANALIZER` para pasta de logs se forem importantes, ou ignorar.

---

## 📉 COMPRESSÃO DE LOGS (Anti-Poluição)

Logs de terminal podem poluir a janela de contexto da LLM, causando esquecimento de instruções anteriores.

### Regras de Leitura:
1. **NUNCA** ler u arquivo de log inteiro se ele tiver > 100 linhas.
   - Use `tail` (PowerShell: `Get-Content -Tail 20`).
   - Use `grep` (PowerShell: `Select-String`).

2. **NUNCA** colar outputs gigantes no chat.
   - Resuma: "Erro na linha 50: [mensagem]".
   - Se o usuário pedir, cole apenas o trecho relevante.

3. **Render Diffs:**
   - Ao editar código, prefira mostrar apenas as mudanças (`render_diffs`) em vez do arquivo todo.

---

## 🚨 SINAIS DE POLUIÇÃO

Seu Heartbeat deve alertar se:
- O histórico da conversa parece confuso.
- Você "esqueceu" uma instrução dada há 5 turnos.
- O tempo de resposta está lento (muitos tokens).

**Ação Corretiva:**
- Declarar `[🧹 CONTEXT CLEANUP]`
- Propor ao usuário: "Vou resumir o que fizemos até agora e limpar o contexto."

---

> **Mantra:** Uma mente limpa é uma mente afiada.
