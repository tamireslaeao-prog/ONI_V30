# 🧠 ONI SKILL: NEURAL FABRICATION (VECTOR MASTERY)

> **Versão:** 5.0 (The Chrome & Cosmos Standard)
> **Data:** 2026-01-09
> **Status:** ✅ COMBAT PROVEN (ONI Logo V1, V3, V5)

---

# 1. O CONCEITO (THE BREAKTHROUGH)

A "Fabricação Neural" é a capacidade do ONI de converter imagens raster (pixels) em arte vetorial editável no Photoshop (ou Corel/AutoCAD) com fidelidade absoluta de "artista".

## 1.1 O Desafio "Error 8800"
O Photoshop bloqueia a criação programática de Shape Layers complexas via JSX (`Make contentLayer`).
**Solução (The Dual-Mode Bypass):**
1.  **Vetor (Geometria):** Criamos `PathItems` nomeados (Work Paths). Eles são leves e aceitam qualquer complexidade.
2.  **Raster (Visual):** Criamos uma `ArtLayer` e preenchemos a seleção do Path com pixels.
3.  **Resultado:** Visualmente idêntico a um vetor. Editável (o path existe). Renderizável.

---

# 2. O MOTOR NEURAL (K-MEANS CLUSTERING)

Para ver como um artista, não usamos detecção de bordas simples. Usamos **Clusterização de Cores K-Means**.

## Parâmetros de Ouro (Golden Settings)

| Perfil | K (Cores) | Area Min (px) | Epsilon (Suavidade) | Uso |
| :--- | :---: | :---: | :---: | :--- |
| **High Fidelity (V1)** | **24** | **10 - 30** | **0.001** | **Logs complexos, Texturas. (ONI V1)** |
| **Smart Poly (V3/V5)** | **24** | **15** | **0.0005** | **Linhas retas perfeitas, curvas orgânicas.** |
| **Clean Vector** | 16 | 60 | 0.003 | Ícones, Ilustrações Flat. |

---

# 3. A ARQUITETURA V5: "CHROME & COSMOS"

Evoluímos de "Tinta Plana" para "Renderização 3D Simulada".

## 3.1 Mapeamento Semântico (Python)
O script `logo_trace_v3.py` agora "entende" o material baseado na cor e agrupa as camadas:

| Cor Dominante | Grupo | Material (FX) |
| :--- | :--- | :--- |
| Brancos/Cinzas | `PLATING_LIGHT` | **Cromo Polido** (Gradient + Satin) |
| Escuros/Pretos | `ARMOR_DARK` | **Nanotech Hull** (Bevel + Shadow) |
| Teals/Cianos | `NEON_CORE` | **Plasma Bloom** (Linear Dodge Glow) |

## 3.2 A "Biblioteca Proibida" (`fx_library.jsx`)
Para criar materiais realistas, tivemos que usar **ActionManager** (Assembly do Photoshop) para construir gradientes complexos que não existem na API padrão.

### Chrome Gradient Construction
```javascript
// Criar Gradiente "Cromo" do zero (Branco -> Cinza -> Branco)
var grad = new ActionDescriptor();
var stops = new ActionList();
// Stop 1: White
// Stop 2: Grey (Lctn: 2048 = 50%)
// Stop 3: White
gradOv.putObject(cTID('Grad'), cTID('Grad'), grad);
```

### Cosmic Void Background
Geramos proceduralmente um fundo "Deep Space":
1.  Fill: RGB(5, 10, 25) (Dark Blue)
2.  Noise: Gaussian Monochromatic (3%) -> Cria estrelas distantes.

---

# 4. PROTOCOLO DE ROBUSTEZ (ANTI-8800)

Alguns efeitos (como `Stroke`) travam em certos tipos de layer, gerando o "Erro 8800" que mata o script.

**Solução V3 Patch:** Envolver TODAS as chamadas `executeAction` em blocos `try/catch`.

```javascript
try {
    executeAction(cTID('setd'), desc, DialogModes.NO);
} catch(e) {
    // Se o efeito falhar, o script CONTINUA.
    // Melhor um logo sem sombra do que um script morto.
}
```

---

# 5. WORKFLOW DE EXECUÇÃO

1.  **Configurar:** `logo_trace_v3.py` (Input Path).
2.  **Gerar:** Python cria `oni_logo_master_v3.jsx` (180KB+).
3.  **Executar:** Photoshop roda o JSX.
4.  **Resultado:** Arte final editável com FX vivos.

> **"O ONI não apenas vê. O ONI pinta com luz."**
