# MEUS ERROS CONHECIDOS (Memória de Longo Prazo)

> **Autogerado pelo ONI ErrorLearningService**
> Atualizado em: 2026-01-15T00:08:02.860949

## ERR-001: Digitar sem Enter
- **Categoria:** CONFIRMAÇÃO
- **Sintoma:** Ação não executada após digitação
- **Causa:** Assumir que digitar = executar
- **Solução:** SEMPRE enviar Enter após digitar em campos de entrada
- **Padrão de Detecção:** `digitar|type|texto|busca|search|campo|input|field`
- **Ocorrências:**
  - 2026-01-14T23:59:06.894158: Check before: clicar no menu de contexto e salvar dialog
  - 2026-01-15T00:04:53.712688: Check before: clicar no menu de contexto para salvar
  - 2026-01-15T00:05:59.629812: Check before: menu contexto salvar

---

## ERR-002: Clicar em elemento errado
- **Categoria:** NAVEGAÇÃO
- **Sintoma:** Clica em elemento diferente do desejado
- **Causa:** Coordenadas estimadas sem verificação
- **Solução:** Verificar posição via OCR antes de clicar
- **Padrão de Detecção:** `click|clicar|coordenada|position`
- **Ocorrências:**
  - 2026-01-14T23:57:40.296761: Check before: clicar no menu salvar dialog
  - 2026-01-14T23:59:06.894684: Check before: clicar no menu de contexto e salvar dialog
  - 2026-01-15T00:04:53.713222: Check before: clicar no menu de contexto para salvar

---

## ERR-003: Menu Windows 11 simplificado
- **Categoria:** MENU
- **Sintoma:** Apps não aparecem no menu de contexto
- **Causa:** Windows 11 tem menu simplificado
- **Solução:** Usar Shift+F10 para menu clássico completo
- **Padrão de Detecção:** `menu|contexto|right.click|direito|winrar|7zip|compress|extractir|comprim`
- **Ocorrências:**
  - 2026-01-14T23:59:58.857442: Check before: menu salvar
  - 2026-01-15T00:04:53.713759: Check before: clicar no menu de contexto para salvar
  - 2026-01-15T00:05:59.630340: Check before: menu contexto salvar
  - 2026-01-15T00:07:07.769308: Check before: menu
  - 2026-01-15T00:08:02.860949: Check before: menu

---

## ERR-004: Executar sem verificar resultado
- **Categoria:** VERIFICAÇÃO
- **Sintoma:** Próxima ação falha porque anterior não completou
- **Causa:** Não seguir ciclo VER→PENSAR→AGIR→VERIFICAR
- **Solução:** Screenshot + view_file + análise ANTES e DEPOIS de CADA ação
- **Padrão de Detecção:** `next|próximo|continuar|executar|múltiplas|sequência`
- **Ocorrências:**

---

## ERR-005: Comandos longos no Run Dialog
- **Categoria:** COMANDOS
- **Sintoma:** Windows não encontra arquivo ou programa
- **Causa:** Run Dialog tem limitações com paths longos
- **Solução:** NÃO usar Win+R para comandos complexos. Usar PowerShell direto ou automação visual
- **Padrão de Detecção:** `win.r|run|executar.*programa|path.*longo|winrar.*command`
- **Ocorrências:**

---

## ERR-006: Ignorar protocolo estabelecido
- **Categoria:** PROTOCOLO
- **Sintoma:** Erros que as regras deveriam prevenir acontecem
- **Causa:** Pressa, otimização prematura
- **Solução:** SEMPRE seguir ciclo: Screenshot→view_file→análise→ação→Screenshot→view_file→confirmar
- **Padrão de Detecção:** `automação|ação|executar|fazer|realizar`
- **Ocorrências:**

---

## ERR-007: Confiar em metadados ao invés de visão real
- **Categoria:** VISÃO
- **Sintoma:** Ações baseadas em dados incorretos ou desatualizados
- **Causa:** Screenshot capturado mas NÃO visualizado com view_file
- **Solução:** OBRIGATÓRIO: screenshot + view_file('C:/temp/oni_screenshot.png') + análise visual escrita
- **Padrão de Detecção:** `active-window|janela|window|tela|screen|ver|olhar`
- **Ocorrências:**

---

## ERR-008: Escrever análise visual SEM OLHAR a imagem
- **Categoria:** ANÁLISE_FALSA
- **Sintoma:** Análise não corresponde ao que está na imagem
- **Causa:** Preguiça mental, pressa, confiar na memória
- **Solução:** Após view_file: descrever LITERALMENTE o que vê. PROIBIDO inventar!
- **Padrão de Detecção:** `análise|analysis|vejo|see|imagem|image|screenshot|visual`
- **Ocorrências:**

---

## ERR-009: Ctrl+F não foca busca no Explorer
- **Categoria:** BUSCA
- **Sintoma:** Texto digitado não aparece no campo de busca
- **Causa:** Explorer do Windows não responde bem a Ctrl+F
- **Solução:** USAR Win+digitação! Depois navegar até 'Abrir local do arquivo' com setas
- **Padrão de Detecção:** `busca|search|ctrl.f|explorer|arquivo|file|pesquisar|find`
- **Ocorrências:**

---

## ERR-010: Porta Errada do Servidor
- **Categoria:** INFRAESTRUTURA
- **Sintoma:** Conexão recusada ou timeout
- **Causa:** Usar porta errada ao invés de 8000
- **Solução:** Servidor ONI SEMPRE roda na porta 8000
- **Padrão de Detecção:** `porta|port|5173|3000|5000|connection|refused|timeout`
- **Ocorrências:**

---

## ERR-011: Script Errado para Iniciar
- **Categoria:** INFRAESTRUTURA
- **Sintoma:** Servidor não inicia ou inicia errado
- **Causa:** Usar script errado para iniciar
- **Solução:** Usar run.bat ou run.py para iniciar o servidor
- **Padrão de Detecção:** `main.py|app.py|iniciar|start|servidor|server`
- **Ocorrências:**

---

## ERR-012: Ignorar Bridges Existentes
- **Categoria:** INFRAESTRUTURA
- **Sintoma:** Recria código que já existe
- **Causa:** Não consultar infraestrutura antes de implementar
- **Solução:** Chamar /api/autonomous/discover ANTES de qualquer tarefa
- **Padrão de Detecção:** `bridge|adapter|módulo|module|reinventar|criar novo`
- **Ocorrências:**

---

## ERR-013: Diálogo não fechou
- **Categoria:** DIÁLOGO
- **Sintoma:** Diálogo permanece aberto após Enter
- **Causa:** Não verificar se diálogo fechou após confirmação
- **Solução:** Fazer Hybrid Vision scan após Enter para confirmar fechamento
- **Padrão de Detecção:** `diálogo|dialog|modal|popup|salvar|save|abrir|open`
- **Ocorrências:**
  - 2026-01-14T23:57:40.297447: Check before: clicar no menu salvar dialog
  - 2026-01-14T23:59:06.895662: Check before: clicar no menu de contexto e salvar dialog
  - 2026-01-14T23:59:58.857442: Check before: menu salvar
  - 2026-01-15T00:04:53.714285: Check before: clicar no menu de contexto para salvar
  - 2026-01-15T00:05:59.630869: Check before: menu contexto salvar

---

