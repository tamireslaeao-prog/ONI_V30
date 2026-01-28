# 🖐️ CONHECIMENTO: MODELAGEM DE MÃOS E PÉS (SINTÉTICO)

> **Status:** Conhecimento Sintético (Gerado Expert Mode)
> **Contexto:** Tutorial Part 3 ausente. Este guia baseia-se nas melhores práticas de modelagem estilizada (Disney/Pixar style) compatível com o workflow das Partes 1 e 2.

---

## ✋ MODELAGEM DA MÃO (Workflow Recomendado)

### 1. Estratégia: Box Modeling (Blocagem)
Para personagens estilizados, iniciar com um cubo ou extrusão do pulso é mais eficiente que *Poly Build*.

- **Base da Palma:**
    - Iniciar com um Cubo escalado (chatado).
    - Adicionar 2 *Loop Cuts* verticais e 1 horizontal para definir a largura dos dedos.
    - A palma deve ter um arco suave (não plana).

### 2. Dedos (Extrusão e Topologia)
- **Estrutura Base:**
    - Extrusão de 4 faces frontais para os dedos (Indicador, Médio, Anelar, Mínimo).
    - **Regra dos 3 Loops:** Cada articulação (junta) deve ter 3 loops para deformar corretamente.
        - *Loop de suporte* (Cima)
        - *Loop da junta* (Meio - Pivô)
        - *Loop de suporte* (Baixo)
    - Comprimento: Seguir arcos de proporção (Dedo médio maior, mínimo menor).

- **O Polegar (O mais difícil):**
    - Extrusão a partir da lateral da base da palma (não da frente).
    - Rotação de ~45º a 60º em relação à palma.
    - Atenção ao "Musculo Tenar" (gordinho da base do polegar) - requer geometria extra para volume.

### 3. Conexão com o Pulso
- **Contagem de Vértices:**
    - O braço (Part 2) geralmente termina com 8 a 12 vértices no pulso.
    - A mão precisa ser reduzida para coincidir com esse número.
    - **Técnica de Redução:** Usar a palma da mão para fundir loops dos dedos (4 dedos x 4 arestas = 16 vértices -> Reduzir para 8 ou 10 no pulso).
- **Topology Flow:** Garantir loops contínuos que circundam o pulso ("Pulseira").

---

## 🦶 MODELAGEM DO PÉ (Workflow Recomendado)

### 1. Estratégia: Extrusão do Tornozelo
Como o corpo já vai até o tornozelo (Part 2), estender é o caminho natural.

- **Blocagem Inicial:**
    - Extrusão para baixo (Calcanhar) e para frente (Peito do pé).
    - Formato de "Cunha" ou "Triângulo".
    - Definir a sola do pé plana (mas com arco interno levantado).

### 2. Dedos do Pé
- Para personagens com sapato: Pode-se modelar apenas a "forma de meia" (sem dedos individuais).
- Para descalço:
    - Extrusão similar à mão, mas muito mais curtos.
    - O "Dedão" é o eixo principal.
    - Topologia mais simples que a mão (menos deformação necessária).

### 3. O Calcanhar e Tendão de Aquiles
- **Topologia em "U":** Criar um loop que desce pelo tornozelo, contorna o calcanhar e sobe.
- Evitar triângulos no tendão para não "quebrar" o sombreamento.

---

## ⚠️ PONTOS CRÍTICOS (Checklist)

1. **Tamanho da Mão:** Em personagens estilizados femininos, a mão aberta deve cobrir aproximadamente o rosto (do queixo à testa).
2. **Arcos Naturais:** Dedos não são retos; eles seguem um arco suave quando relaxados.
3. **Unhas:** Deixar geometria preparada (inset nas pontas dos dedos) se for esculpir detalhes depois.
4. **Clean Quad Topology:** Manter tudo em Quads, especialmente nas juntas.

---

*Gerado por ONI Super Cérebro - Módulo de Autocompletar Conhecimento*
