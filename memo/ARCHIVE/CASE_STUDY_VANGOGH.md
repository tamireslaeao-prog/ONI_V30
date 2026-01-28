# 🎨 WORKFLOW EXEMPLO: VACA VAN GOGH (GOLDEN STANDARD)

> **Status:** ✅ SUCESSO COMPROVADO
> **Propósito:** Modelo de referência obrigatório para execução do Ciclo Visual.
> **Regra:** Imite a estrutura deste workflow em SUAS tarefas.

---

# ETAPA 0: MISE EN PLACE (REGRA ZERO)

## 📋 DEFINIÇÃO DA TAREFA

| Campo | Valor |
|-------|-------|
| **Objetivo** | Desenhar uma vaca no estilo Van Gogh no Adobe Photoshop |
| **Ferramentas** | Hybrid Vision Desktop, ArtMaster API |

## 🎯 DECOMPOSIÇÃO DOS PASSOS (The Loop)

> **O Ciclo Sagrado:** `Action` -> `Hybrid Vision` -> `View File (Annotated)` -> `Decision`

## ⚠️ PONTOS FRACOS IDENTIFICADOS & FALLBACKS
- **Risco:** `canvas_limits: null` (PS sem doc).
- **Fallback:** Usar coords do annotated visualmente.

---

# EXECUÇÃO EXEMPLAR (Do It Like This)

## ETAPA 1: HYBRID VISION - ESTADO INICIAL
**Comando:** `GET /api/hybrid-vision/desktop?nocache=etapa1`
**Análise:** `window_title`: "Program Manager" (Não é PS).
**Ação de Verificação:** `view_file(annotated_path)`

## ETAPA 2: DECISÃO
**Raciocínio:** O PS não está aberto. Preciso abrir.

## ETAPA 3: AÇÃO - ABRIR APP
**Comando:** `GET /api/open?name=photoshop`

## ETAPA 4: VERIFICAÇÃO (RTVDL)
**Comando:** `GET /api/hybrid-vision/desktop?nocache=etapa4`
**Análise:** `window_title`: "Adobe Photoshop" (Sucesso).
**Ação de Verificação:** `view_file(annotated_path)`

## ETAPA 5: DECISÃO - CANVAS?
**Análise:** `canvas_limits` é null. Preciso criar doc.

## ETAPA 6: AÇÃO - NOVO DOC
**Comando:** `GET /api/keys?keys=ctrl,n`

## ETAPA 7: VERIFICAÇÃO (RTVDL)
**Comando:** `GET /api/hybrid-vision/desktop?nocache=etapa7`
**Ação de Verificação:** `view_file(annotated_path)` -> Vejo o diálogo "Novo Doc".

## ETAPA 8: AÇÃO - CONFIRMAR
**Comando:** `GET /api/keys?keys=enter`

## ETAPA 9: VERIFICAÇÃO FINAL DE ESTADO
**Comando:** `GET /api/hybrid-vision/desktop?nocache=etapa9`
**Análise:** `canvas_limits` detectado! (150, 200).
**Ação de Verificação:** `view_file(annotated_path)`

---

# 🎓 LIÇÕES APRENDIDAS (Resumo)

1. **SEMPRE** verificar com Hybrid Vision após cada ação.
2. **SEMPRE** visualizar o `annotated_path`, não apenas o JSON.
3. **SEMPRE** analisar o `window_title` e `canvas_limits` antes de agir.
4. **NUNCA** agir cego.

---
