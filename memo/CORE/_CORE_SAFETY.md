# 🛡️ ONI CORE SAFETY PROTOCOLS (Legacy Reference)

> [!IMPORTANT]
> **⚠️ DOCUMENTATION STATUS UPGRADE**
> This document is legally **SUPERSEDED** by `ONI_MASTER_MANUAL.md`.
> Consult the Master Manual for the Unified Constitution and latest protocols.

---

# 1. PRINCÍPIOS FUNDAMENTAIS

## 🎯 Regra de Ouro
```
AUTOMATIZAR SEMPRE QUE POSSÍVEL → SafeToAutoRun: true
> **Regra Turbo:** Se o comando foi validado pelo seu julgamento técnico como SEGURO, você **DEVE** autorizá-lo (true). Não peça permissão para passos triviais.
```

## 📋 Ciclo Obrigatório
```
VER → PENSAR (ToT) → AGIR → VERIFICAR → (repetir)
```

## ⚠️ Proibições Absolutas
- ❌ **NUNCA** criar scripts Python externos (.py)
- ❌ **NUNCA** usar subprocess/os.system
- ❌ **NUNCA** usar browser_subagent
- ❌ **NUNCA** agir sem antes escanear com Hybrid Vision
- ❌ **NUNCA** ignorar o `annotated_path`
- ❌ **NUNCA** confiar que um diálogo fechou sem verificar
- ❌ **NUNCA** usar "Save As" para criar arquivos novos (usar `write_to_file` primeiro = PWF)
- ❌ **NUNCA** usar `generate_image` (IA generativa) EXCETO se o usuário EXPLICITAMENTE pedir
- ✅ **SEMPRE** definir `SafeToAutoRun: true` in `run_command`
- ✅ **SEMPRE** usar APIs REST do ONI via `read_url_content`
- ✅ **SEMPRE** executar `view_file` imediatamente após um scan para visualizar o `annotated_path`.

---

# 2. 🧠 SYSTEM 2 THINKING (OBRIGATÓRIO)

**Antes de qualquer bloco de ferramenta de ação (click, type, draw), você DEVE escrever no chat:**

```markdown
### 🧠 ANÁLISE PRÉ-AÇÃO
0. **VERIFICAÇÃO VISUAL:** Eu executei a ferramenta `view_file` no `annotated_path.png` gerado pelo último scan? [SIM/NÃO]
   - *Se NÃO: Pare tudo e execute o `view_file` agora. Você não pode agir sem ver.*
1. **O que eu vejo na imagem?** (Descreva elementos, cores, popups, blockers...)
2. **O que eu quero?** (Objetivo imediato)
3. **Plano (Mise en Place):**
   - [ ] Passo 1
   - [ ] Passo 2
4. **ToT (Tree of Thoughts):**
   - Opção A (Escolhida): ...
   - Opção B (Fallback): ...
```

**Só APÓS escrever isso você tem permissão para chamar a ferramenta.**

---

# 3. 🛡️ PROTOCOLOS DE ROBUSTEZ (FAIL-SAFE)

## 3.1 PAD - Protocolo Anti-Diálogo
> **"Janelas nativas são zonas de morte."**
- **Regra:** É ESTRITAMENTE PROIBIDO usar Diálogos de Arquivo (`Open`, `Save As`) se houver qualquer alternativa viável.

## 3.2 PWF - Princípio Write-First
> **"O arquivo deve existir antes de ser aberto."**
**Fluxo Obrigatório:**
1. **CRIAR:** `write_to_file` (Cria esqueleto no disco)
2. **ABRIR:** `Start-Process` (Abre o arquivo específico)
3. **EDITAR:** Interação Visual
4. **SALVAR:** `Ctrl+S` (Salva sem abrir diálogos)

## 3.3 VFJ - Verificação de Fechamento de Janela
> **"Enter não garante nada."**
- Após qualquer interação que deveria fechar uma janela, execute um SCAN imediato para confirmar.
- Se persistir: Tente `Escape` logicamente.

## 3.4 PHP - Protocolo de Higiene de Popup (Anti-Blocker)
> **"Se algo bloqueia a visão, mate-o antes de agir."**
**Regra:** Ao carregar nova página, busque blockers.
- **Alvos:** Logins, Cookies, CEPs, Banners de App.
- **Algoritmo:**
  1. SCAN (Hybrid Vision)
  2. ESCAPE (Tentativa Soft)
  3. CLICK Fechar (Tentativa Hard - coordenadas do X)


## 3.5 RTVDL - Real-Time Visual Decision Loop (Mandatory)
> **"Nunca aja cego. Valide cada passo."**
- **Regra de Atomicidade:** É PROIBIDO encadear ações críticas (ex: Digitar + Enter) em um único passo sem verificação visual intermediária.
- **O Ciclo de Ouro (The Golden Loop):**
  1. **Action A:** Executar a primeira parte (ex: Digitar texto)
  2. **SCAN:** Executar `view_file` do scan recente
  3. **DECISÃO (If/Else):**
     - *O resultado visual é o esperado?*
     - **SIM:** Prossiga para Action B.
     - **NÃO:** Pare e corrija (Retry/Fallback).
  4. **Action B:** Executar a segunda parte (ex: Pressionar Enter)
  5. **SCAN:** Verificar o resultado final.


## 3.6 SAFETY CALIBRATION (Sanity Check)
> **"Teste a arma antes de atirar."**
- **Regra:** Antes de qualquer operação crítica ou complexa (ex: desenho, clique em coordenadas sensíveis), execute um "Tiro de Teste".
- **Fluxo:**
  1. **SNAP:** Capturar estado visual atual.
  2. **TEST:** Executar ação inócua (ex: Click em área vazia, Type em nada).
  3. **DIFF:** Verificar se o sistema reagiu (Cursor moveu? Houve erro?).
  4. **GO/NO-GO:** Se o teste passou, autorizar a operação real.

## 3.7 SCP - Safety Calibration Protocol (Drawing)
> **"Mostre-me onde você vai desenhar."**
- **Regra:** É **PROIBIDO** iniciar desenho (`ArtMaster`) sem antes executar a Calibragem Visual, especialmente em multi-monitor.
- **Fluxo Obrigatório:**
  1. **DETECT:** Hybrid Vision obtém `canvas_limits`.
  2. **CALIBRATE:** `POST /draw/calibrate` com os limites detectados.
     - O mouse deve mover-se para: Centro -> TopoEsq -> BaixoDir -> Centro.
  3. **VERIFY:** O usuário (ou Vision) confirma que o mouse percorreu a área correta (monitor correto).
  4. **EXECUTE:** Só então chamar `/draw/workflow` (preferencialmente com `force_pyautogui=true` se houve dúvida).

---

# 4. 🧠 TREE OF THOUGHTS (ToT) - DETALHAMENTO

**Metodologia Obrigatória:**
1. Gerar 3 estratégias.
2. Escolher a melhor (maior confiança/menor risco).
3. Ter fallbacks prontos.

**Template de ToT:**
```markdown
### ToT: [Nome da Ação]
| # | Estratégia | Endpoint | Confiança | Risco |
|---|------------|----------|-----------|-------|
| 1 | [Método A] | [endpoint] | 0.9 | Baixo |
| 2 | [Método B] | [endpoint] | 0.7 | Médio |
```

---

# 5. 📊 TELEMETRIA E ROLLBACK

- **Checkpoints:** Sempre faça scan ANTES de operações destrutivas e DEPOIS de cada passo crítico.
- **Rollback:** Se a verificação falhar, use `Ctrl+Z` imediatamente e tente o Fallback do ToT.

---

# 6. 🦾 ONI SENTINEL & PANIC SYSTEM (v22.0)
**Objective:** Guaranteed system stability and resource hygiene.

## 6.1 Sentinel Enforcement
- **Track-By-Default:** The system tracks PIDs of all spawned automation shells.
- **Periodic Purge:** Automatic background scan for orphaned processes every 300s.

## 6.2 Panic Response (Kill-Switch Extension)
- **Automatic Execution:** If a critical error (Timeout, RPC Reject) is detected, the `Panic System` triggers a full Sentinel Purge.
- **Purge Targets:** `powershell.exe`, `pwsh.exe`, `acad.exe`, `excel.exe`.
- **Logic:** Recover > Clean > Notify.
