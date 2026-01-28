---
description: skill_web_turbo
---
// turbo-all

# 🌐 SKILL MODULE: WEB SURFER (v3.1 - Full Restore)

> **Contexto:** Carregar este módulo ao interagir com Navegadores (Firefox, Chrome, Edge).
> **Foco:** Navegação, Extração de Dados, Interação com DOM/Visual.

## 🛑 REGRAS DE OURO (WEB)
1. **SLP OBRIGATÓRIO:** Navegadores demoram para abrir. Nunca tente focar imediatamente. Use o **Secure Launch Protocol**.
2. **TITULOS DINÂMICOS:** O título da janela do navegador MUDA conforme o site. 
   - ❌ Não assuma `focus?title=Google`. 
   - ✅ Use `hybrid-vision` para ver o título atual (ex: "Shopee...", "Nova Guia...").

---

# 1. ⚠️ DIFERENÇA CRÍTICA: WEB vs DESKTOP

| Contexto | Endpoint Correto |
|----------|------------------|
| Apps nativos (Photoshop, Word) | `/api/hybrid-vision/desktop` |
| **Páginas web em navegador** | **`/api/hybrid-vision/web`** |

**NUNCA use `/desktop` para analisar páginas web - perde precisão!**

---

# 2. 📋 SEQUÊNCIA OBRIGATÓRIA DE NAVEGAÇÃO

### Passo 1: Focar janela
```bash
GET /api/focus?title=Firefox  # (ou Chrome)
```

### Passo 2: Focar Barra de Endereço (Ctrl+L)
**Nunca** digite URL sem garantir o foco na barra.
```bash
GET /api/keys?keys=ctrl,l
```

### Passo 3: Digitar URL e Confirmar
```bash
GET /api/type?text=https://www.mercadolivre.com.br
GET /api/keys?keys=enter
```

### Passo 4: Aguardar Carregamento
Espere 2-3 segundos para a renderização.
```bash
GET /api/hybrid-vision/web?nocache=page_loaded
```
**VERIFICAÇÃO VISUAL OBRIGATÓRIA:**
- Use `view_file` no `screenshot_path` retornado.
- **NÃO PROSSIGA** se a imagem mostrar que você ainda está no Google ou em uma página erro.

### Passo 5: Interagir com Elementos (Busca/Login)
1. **Identificar:** Olhe o `screenshot_path` (via `view_file`) do passo 4.
2. **Clicar:** `click?x=...&y=...` nas coordenadas do campo.
3. **Digitar:** `type?text=iPhone`
4. **Confirmar:** `keys?keys=enter`

---

# 3. 🔑 ATALHOS DE NAVEGADOR (Referência)

| Atalho | Ação | Endpoint |
|--------|------|----------|
| `Ctrl + L` | Focar barra de endereço | `/api/keys?keys=ctrl,l` |
| `Ctrl + T` | Nova aba | `/api/keys?keys=ctrl,t` |
| `Ctrl + W` | Fechar aba | `/api/keys?keys=ctrl,w` |
| `Ctrl + Tab` | Próxima aba | `/api/keys?keys=ctrl,tab` |
| `Ctrl + Shift + Tab` | Aba anterior | `/api/keys?keys=ctrl,shift,tab` |
| `F5` | Atualizar página | `/api/keys?keys=f5` |
| `Ctrl + F` | Buscar na página | `/api/keys?keys=ctrl,f` |
| `Escape` | Parar carregamento | `/api/keys?keys=escape` |
| `Alt + Left` | Voltar | `/api/keys?keys=alt,left` |

---

# 4. ❌ ERROS COMUNS (WEB)

## Erro 1: "Digitar no Vácuo"
**Sintoma:** Você envia `/type` mas nada acontece na tela.
**Causa:** O foco não estava no campo de input.
**Solução:** Sempre envie `/click` nas coordenadas do campo antes de `/type`.

## Erro 2: Usar endpoint `/desktop`
**Sintoma:** O scan retorna uma imagem genérica do desktop ou corta o conteúdo da página.
**Solução:** Use EXCLUSIVAMENTE `/api/hybrid-vision/web` para browsers.

---

# 5. 📝 TEMPLATES DE TOPO (Best Practices)

## Busca em Site (ToT)
1. **Estratégia 1 (Endereço):** `Ctrl+L` + URL de busca direta (`site.com/search?q=XYZ`) + Enter. (Confiança: 95%)
2. **Estratégia 2 (UI):** Clicar na barra de busca + Digitar + Enter. (Confiança: 80%)
3. **Estratégia 3 (Favoritos):** Clicar no bookmark. (Confiança: 60%)

## Coleta de Dados Múltiplos (Loop)
```markdown
### LOOP: Coletar preços
**Para cada item:**
1. Ctrl+L -> Buscar Item
2. Hybrid Vision (Web) -> Identificar preço
3. Armazenar em variável
4. Repetir
```
