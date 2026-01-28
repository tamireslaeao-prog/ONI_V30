# 🏭 ONI VECTOR MASTERY PROFILE

> **Trigger:** `ONI VECTOR [Alvo]`
> **Status:** 🏆 PRODUCTION READY (Multicolor & High Precision)
> **Engine:** OpenCV K-Means + JSX Vector Compiler
> **Location:** `Desktop\ONIV24\Modules\Photoshop\VectorFactory`

---

## 🧠 O Que é Este Sistema?

O **ONI VECTOR** é um pipeline "Neural-to-Vector" que permite ao sistema digerir imagens puramente visuais (Raster/PNG), seja de IAs Generativas ou rascunhos, e reconstruí-las matematicamente dentro do Photoshop como Shapes vetoriais editáveis.

Diferente de "Live Trace" convencionais, o ONI VECTOR aplica **FX de Elite** (Chrome, Neon, Glass) automaticamente durante a compilação.

## 🏗️ Arquitetura do Pipeline

1.  **👁️ Vision Module (`vision_factory.py`)**
    *   **Algoritmo:** K-Means Clustering (`K=8`).
    *   **Função:** Separa a imagem em ilhas de cor distintas.
    *   **Refinamento:** Aplica Dilatação (fechar gaps) e Alta Precisão Poligonal (`epsilon=0.001`).
    *   **Output:** SVG Multicolorido com Hex Codes originais.

2.  **🔧 Vector Compiler (`vector_factory.py`)**
    *   **Parse:** Lê o SVG e extrai coordenadas e cores.
    *   **Fabrication:** Gera código JSX (`createNeuralShape`) para desenhar cada caminho no Photoshop.
    *   **Injection:** Insere o payload vetorial no Template Master.

3.  **🎨 FX Engine (`template.jsx`)**
    *   **Função:** `applyPremiumColorFX()`
    *   **Estilo:** "Colored Glass/Tech".
    *   **Detalhes:**
        *   *Inner Bevel "Chisel Hard":* Para volume sólido.
        *   *Inner Glow:* Para bordas "cyber".
        *   *No Overlays:* Preserva a cor original extraída pelo Vision Module.

## 🚀 Como Usar (Comandos Persistentes)

### 1. Via CLI (Recomendado)
```bash
oni_vector "C:\caminho\para\imagem.png"
```
*Gera o script e vetoriza automaticamente.*

### 2. Via Gatilho Natural
> "ONI VECTOR Logo de uma padaria cyberpunk"
> "ONI VECTOR C:\meus_logos\rascunho.jpg"

---

## 📂 Estrutura de Arquivos (Não Apagar)

*   `oni_vector.bat` (Gatilho Mestre na Raiz)
*   `Modules\Photoshop\VectorFactory\`
    *   `vision_factory.py` (O Olho)
    *   `vector_factory.py` (O Compilador)
    *   `full_pipeline.py` (O Orquestrador)
    *   `template.jsx` (A "Fôrma" do Photoshop)

---

## ⚠️ Manutenção

*   **Se a cor sair "feia":** Aumente `n_colors` em `vision_factory.py`.
*   **Se o vetor ficar "quadrado":** Diminua o `epsilon` (0.001 -> 0.0005) em `vision_factory.py`.
*   **Se o Photoshop travar:** Diminua a resolução da imagem de entrada (resize antes do K-Means).
