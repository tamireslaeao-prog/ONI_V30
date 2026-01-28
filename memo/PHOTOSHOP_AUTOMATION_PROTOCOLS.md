
# 💎 PHOTOSHOP AUTOMATION PROTOCOLS (ONI V25)

> **Status:** ✅ VALIDADO EM PRODUÇÃO
> **Versão Corrente:** V24 (Hunter)
> **Data:** 2025-12-31

Este documento detalha a lógica avançada de manipulação de Assets PSD complexos, desenvolvida após extensa engenharia reversa.

---

## 🔍 PROTOCOLO HUNTER (V24)

O **Protocolo Hunter** é a solução definitiva para editar textos dentro de Smart Objects aninhados, independentemente da estrutura do PSD original. Ele resolve o problema de "onde está o texto editável?" e "como limpar o lixo sem quebrar o efeito?".

### 1. Problema Original
Assets PSD complexos (3D, Cartoon, Glitch) escondem seu texto editável:
- Dentro de pastas profundas.
- Dentro de Smart Objects aninhados (até 3 níveis).
- Embelezados com camadas de título ("PSD FILE", "EDIT ME") que confundem automações simples.

### 2. A Solução (Recursive Deep Scan)
O algoritmo não confia na estrutura da raiz. Ele varre recursivamente:
1.  **Search:** Varre todas as camadas e entra em `LayerSets` (Pastas).
2.  **Clean:** Identifica e oculta camadas de lixo:
    - **Backgrounds:** Pelo nome (`bg`, `paper`, `preview`).
    - **Labels:** Pelo conteúdo do texto (`psd`, `edit`, `font`, `download`).
3.  **Hunt:** Encontra o melhor candidato a "Hero":
    - **Hero Text:** O texto com maior Tamanho de Fonte.
    - **Hero SO:** O Smart Object com maior Área (fallback).
4.  **Action:**
    - Se achar Texto: Edita + **Reveal All** (para evitar cortes).
    - Se não achar Texto: Entra no Smart Object (Dive) e repete o processo recursivamente.

### 3. Código JSX Core (Referência)

```javascript
function deepScan(container) {
     for(var i=0; i<container.layers.length; i++){
        var l=container.layers[i];
        
        // 1. CLEANER (Hide Garbage)
        if (isGarbage(l)) l.visible = false;

        // 2. RECURSE (Enter Groups)
        if (l.typename == "LayerSet") deepScan(l);

        // 3. IDENTIFY HERO
        if (l.kind == LayerKind.TEXT && size > maxSize) bestHeroText = l;
        if (l.kind == LayerKind.SMARTOBJECT && area > maxArea) bestHeroSO = l;
     }
}
```

---

## 🛠️ ESTRATÉGIAS COMPLEMENTARES

### A. Place Embedded (V12.4)
Nunca usamos `Duplicate Layer`. Sempre usamos `Place Embedded` para garantir 100% de fidelidade visual dos efeitos e blending modes do asset original.

### B. Reveal All (V23)
Ao editar um texto num Smart Object, ele pode ficar maior que o canvas original do SO. O comando `doc.revealAll()` é executado obrigatoriamente após a edição para expandir o canvas e evitar cortes.

### C. Safe Unlock
Antes de ocultar/editar, o script tenta remover travas (`locked = false`) para garantir que camadas protegidas ("Background locked") possam ser manipuladas.

---

## 📊 EVOLUÇÃO DAS VERSÕES

| Versão | Nome | Característica Principal | Status |
|---|---|---|---|
| V12 | Basic | Duplicate Layer (Falha visual) | ❌ |
| V12.4 | Place | Place Embedded (Fidelidade visual) | ✅ |
| V15 | Surgeon | Edição baseada em tamanho de fonte | ⚠️ (Bugs com lixo) |
| V17 | Vacuum | Limpeza agressiva (Quebrava efeitos) | ❌ |
| V19 | Smart | Mergulho em Smart Objects (Falhava em pastas) | ⚠️ |
| V22 | Safe | Limpeza conservadora | ✅ |
| **V24** | **Hunter** | **Scanner Recursivo de Pastas + Reveal All** | **🏆 FINAL** |

---


---

## 📂 LOCAIS PADRÃO

- **Biblioteca de Assets:** `D:\DESIGN\psd_sources` (Text Effects, 3D, Cartoon)
- **Serviço Composer:** `app/services/photoshop/composer_service.py`
- **Mecanismo de Teste:** `temp/ONI_TIRA_TEIMA_V22.py` (Script de referência)

Use este protocolo para qualquer nova automação envolvendo PSDs de terceiros.
