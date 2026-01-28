# 👁️ CORE VISION PROTOCOL - REGRA ABSOLUTA

> **Versão:** 1.0  
> **Data:** 2026-01-08  
> **Status:** ✅ OBRIGATÓRIO EM TODA EXECUÇÃO

---

## 🚨 REGRA SUPREMA: VER ANTES DE AGIR

> [!CAUTION]
> **O Hybrid Vision Annotated é o ÚNICO visualizador prioritário do ONI.**
> 
> É **PROIBIDO** executar qualquer ação (click, type, keys, draw) sem antes:
> 1. Chamar `/api/hybrid-vision/desktop`
> 2. Visualizar o `annotated_path` retornado
> 3. Analisar os elementos detectados

---

## 📋 CICLO OBRIGATÓRIO (RTVDL v22.0)

```
┌─────────────────────────────────────────────────────────┐
│                   ANTES DE CADA AÇÃO                    │
├─────────────────────────────────────────────────────────┤
│  1. SCAN: GET /api/hybrid-vision/desktop?nocache=pre    │
│  2. CACHE CHECK: dHash (Se idêntico, pular inferência)  │
│  3. VIEW: view_file do annotated_path                   │
│  4. ANALYZE: Identificar elementos e coordenadas        │
├─────────────────────────────────────────────────────────┤
│                      EXECUTAR AÇÃO                      │
├─────────────────────────────────────────────────────────┤
│  5. ACTION: GET /api/click, /api/type, /api/keys, etc.  │
├─────────────────────────────────────────────────────────┤
│                   DEPOIS DE CADA AÇÃO                   │
├─────────────────────────────────────────────────────────┤
│  6. VERIFY: GET /api/hybrid-vision/desktop?nocache=post │
│  7. VIEW: view_file do novo annotated_path              │
│  8. CONFIRM: Verificar que a ação teve efeito           │
│  9. UPD_CACHE: Atualizar dHash e resultados SOM         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 ENDPOINTS OBRIGATÓRIOS

### 1. Scan Desktop (SEMPRE ANTES/DEPOIS)
```
GET http://localhost:8000/api/hybrid-vision/desktop?nocache={timestamp}
```

**Retorna:**
```json
{
  "window_title": "...",
  "screenshot_path": "temp/ANALIZER/hybrid_*.png",
  "annotated_path": "temp/ANALIZER/annotated_hybrid_*.png",  // ← VISUALIZAR ESTE
  "canvas_limits": {...},
  "elements": [...]
}
```

### 2. Visualizar Annotated (OBRIGATÓRIO)
```
view_file(annotated_path)
```

**Por que?**
- É a ÚNICA forma de ver exatamente o que o ONI está vendo
- Mostra coordenadas exatas de cada elemento
- Confirma se a tela mudou após a ação

---

## ⚠️ PROIBIÇÕES ABSOLUTAS

| ❌ PROIBIDO | ✅ OBRIGATÓRIO |
|-------------|----------------|
| Clicar sem scan prévio | Scan → Click → Scan |
| Digitar sem verificar foco | Scan → Verificar campo → Type → Scan |
| Assumir que ação funcionou | Sempre verificar com scan pós-ação |
| Usar coordenadas de memória | Sempre extrair coords do scan recente |
| Encadear ações sem verificação | Verificar cada ação individualmente |

---

## 📝 TEMPLATE DE EXECUÇÃO

```markdown
### 🔍 PRE-SCAN
**Endpoint:** `GET /api/hybrid-vision/desktop?nocache=pre_16_42_40`
**Annotated:** [verificar via view_file]
**Window:** [nome da janela]
**Elementos relevantes:**
- uid_xxx: Button "Submit" @ (500, 300)
- uid_yyy: Edit "Username" @ (300, 200)

### ⚡ ACTION
**Objetivo:** Clicar no botão Submit
**Endpoint:** `GET /api/click?x=500&y=300`

### ✅ POST-SCAN
**Endpoint:** `GET /api/hybrid-vision/desktop?nocache=post_16_42_41`
**Annotated:** [verificar via view_file]
**Resultado:** ✓ Página mudou / ✗ Botão ainda visível

### 📊 DECISÃO
- [x] Ação bem-sucedida → Prosseguir
- [ ] Ação falhou → Retry ou Fallback
```

---

## 🎯 CASOS DE USO

### Caso 1: Clicar em Botão
```
1. SCAN: hybrid-vision/desktop
2. VIEW: annotated (encontrar botão)
3. EXTRACT: coordenadas do botão (center_x, center_y)
4. CLICK: /api/click?x={center_x}&y={center_y}
5. SCAN: hybrid-vision/desktop
6. VIEW: annotated
7. CONFIRM: botão sumiu ou tela mudou?
```

### Caso 2: Digitar em Campo
```
1. SCAN: hybrid-vision/desktop
2. VIEW: annotated (encontrar campo)
3. CLICK: clicar no campo para focar
4. SCAN: verificar foco
5. TYPE: /api/type?text=...
6. SCAN: hybrid-vision/desktop
7. VIEW: annotated
8. CONFIRM: texto apareceu no campo?
```

### Caso 3: Atalho de Teclado
```
1. SCAN: hybrid-vision/desktop
2. VIEW: annotated (confirmar janela correta)
3. KEYS: /api/keys?keys=ctrl,n
4. SCAN: hybrid-vision/desktop
5. VIEW: annotated
6. CONFIRM: diálogo/janela nova apareceu?
```

---

## 🔁 FREQUÊNCIA DE SCAN

| Situação | Scan Antes | Scan Depois |
|----------|------------|-------------|
| Click em botão | ✅ | ✅ |
| Type em campo | ✅ | ✅ |
| Keys (atalho) | ✅ | ✅ |
| Draw (ArtMaster) | ✅ | ✅ |
| Abrir app | ❌ (3s delay) | ✅ |
| Fechar diálogo | ✅ | ✅ |

---

## 💾 ARMAZENAMENTO

- **Local:** `temp/ANALIZER/`
- **Padrão:** `annotated_hybrid_{HH-MM-SS-mmm}.png`
- **Retenção:** Manter últimos 50 arquivos (garbage collection)

---

## 🧠 INTEGRAÇÃO COM COGNIÇÃO

Este protocolo deve ser lido em conjunto com:
- `_CORE_COGNITION.md` - Regras de decisão
- `_CORE_SAFETY.md` - Regras de segurança
- `WORKFLOW_UNIVERSAL.md` - Fluxo geral

---

**LEMBRE-SE:** "NUNCA aja cego. O annotated é seus olhos."
