# 🧠 CONHECIMENTO: MODELAGEM DE CABEÇA ANIME

> **Fonte:** youtube_fNxdOtegry0 (Blender Complete Character Tutorial - Part 1)
> **Técnica:** Cube-based Subdivision + Detached Guide
> **Estilo:** Anime / Stylized Character
> **Status:** Consolidado

---

## 🔑 CONCEITOS CENTRAIS

### 1. Fundação no Cubo
Ao contrário da abordagem padrão de Esfera, este método usa um **Cubo com Subdivision Surface**.
- **Por quê?** Melhor fluxo de topologia visual para cabeças estilizadas.
- **Polígonos:** Começa simples (Cubo), depois subdivide.

### 2. A Técnica "Detached Back Head" (O SEGREDO 🌶️)
Esta é a técnica única enfatizada no vídeo.
1. **Desconectar** a metade de trás da malha da cabeça.
2. **Aplicar** Subdivision Surface permanentemente apenas nesta parte de trás.
3. **Usar como Guia:** Manter esta peça de trás high-poly como superfície de referência.
4. **Benefícios:** Mantém a curvatura esférica perfeita para o crânio enquanto permite trabalho manual de topologia na face.
5. **Re-conectar:** Fundir de volta ao final do processo.

---

## 🛠️ WORKFLOW PASSO-A-PASSO

### Fase 1: Forma Base
1. **Pescoço:** Cilindro com **16 vértices**.
2. **Base da Cabeça:** Cubo com Subdivision Modifier (Nível 2).
3. **Sculpting:**
    - Deletar metade da malha + Mirror Modifier.
    - Alternar para **Sculpt Mode**.
    - Usar **Smooth Brush** para arredondar.
    - Usar **Grab Brush** para combinar com a forma da referência (queixo, bochechas).
4. **Guias:** Usar **Mark Seams** (arestas vermelhas) para desenhar os loops de topologia pretendidos no sculpt.

### Fase 2: Construção da Topologia
1. **Knife Tool (K):** Cortar os loops primários diretamente na malha.
2. **Loop da Boca:**
    - Selecionar área da boca.
    - Split/Bevel para criar o loop do lábio.
    - Merge vertices para limpar.
3. **Loop do Olho:**
    - Posicionar o loop **fora** das linhas da imagem do olho.
    - Usar uma esfera temporária (globo ocular) como guia físico para curvatura perfeita.

---

## 💡 DICAS CRÍTICAS DA TRANSCRIÇÃO

- "O fluxo de topologia de um cubo subdividido tem visual melhor que esfera."
- "Eu uso Mark Seams apenas como guia visual... arestas vermelhas ajudam a identificar o loop."
- "Comece com o character sheet já no lugar."
- "Use a cabeça de trás desconectada como guia toda vez que adicionar um novo Loop cut para garantir sincronização."

---

## 🎨 ESPECIFICIDADES DO ESTILO ANIME
- **Olhos Grandes:** Ocupam área significativa da face (aprox 30% da largura).
- **Boca Pequena:** Técnica de 'Mouth Bag' para cavidade interna.
- **Pele Lisa:** Depende fortemente do Subdivision Modifier para o visual final.

---

*Gerado por ONI Super Cérebro - Módulo Deep Learning (Consolidado)*
