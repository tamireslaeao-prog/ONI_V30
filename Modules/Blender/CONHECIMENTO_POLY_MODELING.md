# 🎓 CONHECIMENTO: POLY MODELING FACES (SEM SCULPT)

> **Fonte:** YouTube - "Poly Modeling Faces NO SCULPT REQUIRED"
> **ID:** YCX54Nffuys
> **Frames Analisados:** ~10,594
> **Data:** 2026-01-18

---

## 📋 SUMÁRIO EXECUTIVO

Este tutorial ensina modelagem de personagens **sem sculpting**, usando apenas técnicas de **poly modeling** tradicionais. Ideal para computadores menos potentes ou quem não tem mesa digitalizadora.

---

## 🔑 TÉCNICAS PRINCIPAIS APRENDIDAS

### 1. SETUP DE REFERÊNCIA
- Usar dois planos de imagem: **FRONTAL** e **LATERAL**
- Alinhar os planos em vistas ortográficas
- Os olhos, nariz e boca devem estar alinhados entre as duas referências
- Usar transparência nos planos para ver a geometria por trás

### 2. LOOPS ANATÔMICOS (O SEGREDO!)

O tutorial enfatiza que **edge loops corretos são fundamentais** para animação.

```
LOOPS OBRIGATÓRIOS:
┌─────────────────────────────────────┐
│  1. EYE LOOP (Orbicularis Oculi)    │
│     - Circunda completamente o olho │
│     - Permite fechar pálpebra       │
│                                     │
│  2. MOUTH LOOP (Orbicularis Oris)   │
│     - Circunda a boca               │
│     - Permite abrir/fechar lábios   │
│                                     │
│  3. NASOLABIAL LOOP                 │
│     - Do nariz até o canto da boca  │
│     - Para expressões de sorriso    │
│                                     │
│  4. BROW LOOP                       │
│     - Sobre as sobrancelhas         │
│     - Para expressões de raiva/      │
│       surpresa                      │
└─────────────────────────────────────┘
```

### 3. BLOCKING (ORDEM DE CONSTRUÇÃO)

O tutorial mostra uma **ordem específica** para construir a face:

1. **Perfil** - Começar pelo contorno lateral
2. **Boca** - Criar o loop da boca primeiro
3. **Bochechas** - Preencher a área das bochechas
4. **Olhos** - Criar cavidades e loops oculares
5. **Nariz** - Ponte e narinas
6. **Testa** - Conectar ao topo da cabeça
7. **Queixo** - Definir a mandíbula

### 4. TÉCNICA DO "GRID FILL"

- Criar faces na sequência, polígono-a-polígono
- Usar `F` para criar faces entre vértices selecionados
- Manter quads (4 lados) sempre que possível
- Evitar triângulos exceto em áreas de baixa deformação

### 5. EXTRUSÃO CONTROLADA

```
Workflow de Extrusão:
1. Selecionar edge loop
2. E → Extrudar
3. S → Escalar para ajustar tamanho
4. G → Mover para posição correta
5. Repetir para próximo loop
```

---

## 🎯 APLICAÇÃO NO ONI

### Melhorias para V19:

1. **Ordem de Construção Corrigida:**
   - Iniciar pela BOCA (não pelo cubo)
   - Criar loops antes de features
   
2. **Eye Socket Correto:**
   ```python
   # Criar loop orbital ANTES do olho
   eye_loop_verts = select_circular_edge(center=(0.25, -0.5, 0.05), radius=0.12)
   bmesh.ops.inset_region(bm, faces=eye_faces, thickness=0.03, depth=-0.05)
   ```

3. **Mouth Cavity Integrada:**
   ```python
   # O MOUTH LOOP deve ser criado no mesh da cabeça
   # NÃO como objeto separado!
   mouth_loop = select_edge_loop(z_range=(-0.45, -0.55), y_max=-0.5)
   bmesh.ops.inset_region(bm, faces=mouth_faces, thickness=0.02, depth=0.01)
   bmesh.ops.extrude_face_region(bm, geom=mouth_faces)
   # Push vertices INWARD
   for v in extruded_verts:
       v.co.y += 0.05  # INTO THE HEAD
   ```

4. **Nasolabial Fold:**
   ```python
   # Conectar nariz à boca via edge loop
   # Isso permite sorriso realista
   nasolabial_verts = [v for v in bm.verts if 
                       abs(v.co.x) > 0.1 and abs(v.co.x) < 0.18 and
                       v.co.z < -0.3 and v.co.z > -0.5]
   sculpt_smooth_safe(bm, nasolabial_verts, iterations=2)
   ```

---

## 📐 PROPORÇÕES FACIAIS (Do Tutorial)

| Feature | Proporção |
|---------|-----------|
| Olhos | 1/3 da altura da face |
| Nariz | 1/3 entre olhos e queixo |
| Boca | 1/3 do nariz ao queixo |
| Largura olho | = Distância entre olhos |
| Orelhas | Alinhadas entre sobrancelha e nariz |

---

## 🔧 FERRAMENTAS DO BLENDER USADAS

| Ferramenta | Atalho | Uso |
|------------|--------|-----|
| Extrude | E | Criar novos loops |
| Inset | I | Criar loops internos |
| Fill | F | Criar faces |
| Merge | M | Juntar vértices |
| Knife | K | Cortar edges |
| Loop Cut | Ctrl+R | Adicionar edge loops |
| Smooth | Shift+S | Suavizar vértices |
| Proportional Edit | O | Edição orgânica |

---

## ⚠️ ERROS COMUNS A EVITAR

1. ❌ NÃO começar com esfera/cubo sem planejar loops
2. ❌ NÃO criar features como objetos separados
3. ❌ NÃO usar triângulos em áreas de deformação
4. ❌ NÃO ignorar a ordem de construção
5. ❌ NÃO esquecer de conectar loops entre features

---

## ✅ CHECKLIST PRÉ-MODELAGEM

- [ ] Referências frontal e lateral alinhadas
- [ ] Escala correta definida
- [ ] Planejar loops antes de começar
- [ ] Definir ponto de partida (boca/olho)
- [ ] Ter 3 fallbacks no ToT

---

## 🎬 FRAMES CHAVE ANALISADOS

| Frame | Conteúdo | Aprendizado |
|-------|----------|-------------|
| 200 | Referência Setup | Alinhamento front/side |
| 500 | Environment Setup | Planos de imagem posicionados |
| 1000 | Head Topology | Eye loops visíveis, nose bridge |
| 2000 | Cheek/Nose | Fill da bochecha, edge loops |
| 3000 | Ear Detail | Ear topology com loops |

---

## 🔄 PRÓXIMOS PASSOS

1. **Criar V19** implementando ordem de construção correta
2. **Testar** loops para animação (fechar olho, abrir boca)
3. **Refinar** proporções baseado nas regras do tutorial
4. **Documentar** resultados em walkthrough

---

**Status:** ✅ CONHECIMENTO ABSORVIDO E SINTETIZADO
