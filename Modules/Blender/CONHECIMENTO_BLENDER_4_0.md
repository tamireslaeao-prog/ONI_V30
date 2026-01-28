# 🧠 CONHECIMENTO: BLENDER 4.0 FUNDAMENTALS
> **Fonte:** Beginner Blender 4.0 Tutorial (2023)
> **Ref:** 4haAdmHqGOw (YouTube)
> **Data:** 2025-01-01

---

## 🎯 RESUMO EXECUTIVO
Tutorial focado nos fundamentos essenciais do Blender 4.0, cobrindo desde a navegação inicial até modelagem básica e modificadores. O fluxo de trabalho enfatiza atalhos de teclado e a distinção crítica entre *Object Mode* e *Edit Mode*.

---

## 1. 🧭 NAVEGAÇÃO & INTERFACE (THE BIG THREE)
A tríade sagrada da navegação no Blender:

| Ação | Comando (Mouse) | Comando (Teclado) | Descrição |
|------|-----------------|-------------------|-----------|
| **Orbit** | Middle Mouse Button (MMB) | - | Girar a câmera ao redor do foco |
| **Pan** | Shift + MMB | Shift + Numpad 4/6/8/2 | Mover a câmera lateralmente |
| **Zoom** | Scroll Wheel ou Ctrl + MMB | Numpad +/- | Aproximar/Afastar |

> **Dica Pro:** Pressione `~` (Tilde) para abrir o menu radial de vistas (Top, Bottom, Left, Right).

---

## 2. 🧊 MODO OBJETO vs MODO EDIÇÃO

### Object Mode (Tab)
- Manipula o objeto como um todo.
- Escalonamento aqui altera a "escala global" (pode causar problemas com texturas/bevels depois).
- **Atalhos:**
    - `G`: Grab (Mover)
    - `R`: Rotate (Girar)
    - `S`: Scale (Escalar)

### Edit Mode (Tab)
- Manipula a geometria interna (Vértices, Arestas, Faces).
- Alterações aqui modificam a malha real.
- **Seleção:**
    - `1`: Vértices (Pontos)
    - `2`: Arestas (Linhas)
    - `3`: Faces (Polígonos)

---

## 3. 🛠️ MODELAGEM BÁSICA
Ferramentas essenciais para manipular geometria:

### Extrude (E)
- "Estica" a geometria criando novas faces.
- Fundamental para transformar formas 2D em 3D ou alongar membros.
- **Uso:** Selecione face > `E` > Arraste.

### Inset (I)
- Cria uma nova face dentro da face selecionada.
- Útil para criar bordas ou preparar loops.

### Bevel (Ctrl + B)
- Arredonda arestas duras.
- Role o scroll do mouse para aumentar segmentos (suavidade).

### Loop Cut (Ctrl + R)
- Adiciona anéis de arestas ao redor da geometria.
- Role o scroll para adicionar múltiplos cortes.

---

## 4. 🔧 MODIFICADORES (MODIFIERS)
O poder não-destrutivo do Blender. Ficam na aba azul (chave de boca).

### Subdivision Surface (Subdiv)
- **Atalho:** `Ctrl+1` (Nível 1), `Ctrl+2` (Nível 2)...
- Divide cada face em 4, suavizando a malha.
- **Shade Smooth:** Clique direito no objeto > "Shade Smooth" para esconder facetas.

### Solidify
- Dá espessura a objetos planos (como tecidos ou cascas).

---

## 5. 💡 DICAS CRÍTICAS DE FLUXO (PITFALLS)
- **Apply Scale (`Ctrl+A`):** Se ferramentas como Bevel ou texturas parecerem esticadas, você provavelmente escalou no Object Mode. Aplique a escala para corrigir (torna a escala 1,1,1).
- **Normals:** Se o sombreamento parecer estranho (preto/errado), verifique a orientação das normais (`Shift+N` no Edit Mode para recalcular fora).
- **X-Ray (Alt+Z):** Permite selecionar vértices através do objeto (atrás dele).

---

## ✅ CHECKLIST DE APRENDIZADO
- [ ] Confortável com Orbit/Pan/Zoom?
- [ ] Sabe alternar entre Edit/Object mode sem pensar?
- [ ] Entende Extrude vs Grab?
- [ ] Sabe aplicar Shade Smooth + Subdiv?
