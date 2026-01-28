# 🔩 CONHECIMENTO: HARD SURFACE PRO (SODA CAN)

> **Fonte:** Hard_Surface_Pro (tutorial_hardsurface.webm)
> **Frames Analisados:** Amostragem de 10 keyframes (Total 627)
> **Foco:** Modelagem Hard Surface com Sub-D (Subdivision Surface)

---

## 🛠️ WORKFLOW DE MODELAGEM (Passo a Passo)

### 1. Setup de Referência (Blueprint)
- Importar imagem de referência ("Blender Berry") como *Reference Image*.
- Alinhar perfeitamente com os eixos ortográficos (Front/Top).
- **Dica Visual:** Use o menu de propriedades da imagem para ajustar opacidade e posição.

### 2. Modelagem por Simetria (Symmetrize)
- Em vez de Mirror Modifier, o tutorial mostra o uso de **Symmetrize** (Mesh > Symmetrize).
- Útil para modelar detalhes complexos (como o anel da lata) em apenas um lado e espelhar a geometria destrutivamente ou via modifier.
- **Quick Favorites:** O autor adicionou Symmetrize aos favoritos rápidos (`Q`) para agilidade.

### 3. Topologia para Hard Surface
- **Desafio:** Manter a curvatura da lata enquanto modela detalhes planos (lacre/anel).
- **Técnica:**
    - Começar com um plano ou cilindro com contagem de vértices adequada (ex: 32 ou 64).
    - Usar **Vertex Slide** (`Shift+V` ou `G, G`) para mover vértices ao longo das arestas existentes sem deformar a silhueta.
    - Manter **Quads** (faces de 4 lados) é crítico para o *Subdivision Surface* funcionar sem artefatos de sombreamento (pinching).

### 4. Modifier Stack (A Pilha)
- **Subdivision Surface (Sub-D):**
    - Levels Viewport: 2
    - *Optimal Display* ativado para limpar a visualização no viewport.
- O objetivo é criar uma malha "Low Poly" de controle que, ao ser subdividida, gera curvas perfeitamente suaves e reflexos "pro" (sem distorções).

---

## 🔧 FERRAMENTAS & ATALHOS CHAVE

| Ferramenta | Função | Obs |
|------------|--------|-----|
| **Vertex Slide** | Ajustar loops mantendo a forma | Essencial para hard surface |
| **Symmetrize** | Espelhar geometria | Diferente de Mirror Modifier |
| **Subdivision** | Suavizar malha final | O "segredo" do look profissional |
| **Duplicate** | `Shift + D` | Para criar variações ou backups |

---

## 💡 LIÇÕES APRENDIDAS (Deep Learning)

1. **Curvas Complexas:** Ao modelar cortes em superfícies curvas (tampa da lata), a topologia precisa "fluir" ao redor do detalhe. Loops de suporte são necessários para segurar as bordas duras quando o Sub-D é aplicado.
2. **Precisão:** Hard Surface exige mais rigor matemático que modelagem orgânica. Vértices desalinhados causam reflexos tortos.
3. **Controle de Densidade:** Use *Vertex Slide* para agrupar arestas onde você quer cantos mais vivos (sharp) e espalhá-las onde quer curvatura suave.

---

*Síntese gerada pelo ONI Super Cérebro a partir da análise visual de frames do tutorial.*
