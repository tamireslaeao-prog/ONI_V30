# CONHECIMENTO DE MODELAGEM DE CORPO (V1.0)
> **Fonte**: Análise Sequencial - Blender Complete Character Tutorial - Part 2

## 🎯 Objetivo
Dominar o workflow de criação do corpo (Topologia, Proporções, Fluxo) continuando a partir da cabeça (Part 1).

## 🧩 Fase 1: Neck & Shoulders (Pescoco e Ombros)
**Intervalo:** Frames 001 - 200

### 1.1 Análise Inicial e Preparação
- **Base:** Inicia com a cabeça finalizada (Part 1).
- **Topologia do Pescoço:** O "stub" do pescoço deixado na Part 1 possui aproximadamente **16-20 vértices** no loop (8-10 por lado no Mirror).

### 1.2 Workflow "The Mantle" (O Manto)
Em vez de modelar o torso separadamente, o artista estende o pescoço para criar uma "capa" que define o topo do torso.

1.  **Extrusão do Pescoço (Neck Tube):**
    - Selecionar o loop da base do pescoço.
    - Extrusão (E) no eixo Z para definir o comprimento do pescoço.
2.  **Extrusão do Manto (The Mantle):**
    - Extrusão (E) nova a partir da base do pescoço até a linha das axilas.
    - Scale (S) no eixo X para alargar até a largura dos ombros.
    - Isso cria um formato trapezoidal (como um manto) cobrindo o topo do peito/costas.
3.  **Extrusão do Ombro (Shoulder Stump):**
    - Selecionar as faces laterais desse "Manto" (geralmente 2 faces na vertical).
    - Extrusão (E) no eixo X para criar o "toco" do ombro.
    - **Obs:** Isso garante que o fluxo de bordas do deltoide nasça naturalmente do peito e costas.

### 1.3 Refinamento Inicial (Blockout)
- Ajuste dos vértices do "toco" do ombro para arredondar a forma.
- O resultado no Frame 200 é um torso superior "blocagem" com tocos de braço, garantindo loops limpos para a axila.

### 1.4 Técnica de Separação (Descoberta Frames 300-350)
Para trabalhar a topologia complexa do ombro sem estragar a cabeça:
1.  **Separação:** O artista separa a malha da cabeça da malha do corpo (provavelmente tecla `P` -> Selection) ou deleta as faces de conexão.
2.  **Isolamento:** Isso permite refinar o fluxo do "Manto" e do Ombro sem as restrições dos loops faciais.
3.  **Re-conexão (Stitching):** (Frames 500-600)
    - O artista seleciona o loop da base do pescoço e o loop do buraco do torso.
    - Utiliza **Bridge Edge Loops** (ou F para preencher, mas Bridge é mais provável para manter quadriláteros).
    - **Ajuste de Vértices:** Após a conexão, há um trabalho manual (Slide GK) para suavizar a transição, garantindo que a clavícula não fique "bico".

### 1.5 Clavícula e Trapézio (Frames 600-700)
- **Referência Anatômica:** O artista traz imagens de referência de anatomia muscular (costas/trapézio) para o viewport (Frames 630+).
- **Desenho de Topologia:** Ele desenha (Annotate tool) sobre referência para planejar o fluxo dos loops do trapézio e escápula.
- **Ajuste de Fluxo:** Os loops das costas são ajustados para imitar a forma de "V" do trapézio, descendo do pescoço em direção à coluna.
- **Definição da Escápula:** A topologia é manipulada para criar a sugestão da escápula, garantindo que a deformação futura do ombro seja natural.

## 🧩 Fase 2: Torso e Cintura (The Tube)
**Intervalo:** Frames 200 - 400+

### 2.2 Extrusão do Tubo (Cintura e Quadril) - (Frames 700-800)
- **Extrusão Contínua:** A partir da base do torso criada anteriormente, o artista continua a extrusão para baixo (Eixo Z).
- **Acompanhando a Referência:** A cada extrusão, escala-se (S) e rotaciona-se (R) o loop para acompanhar a curvatura da espinha na vista lateral (Right View) e a largura do quadril na vista frontal.
- **Topologia Simples:** Mantém-se a topologia cilíndrica simples (The Tube) sem adicionar detalhes musculares complexos ainda. O foco é volume e silhueta.

### 2.3 Transição para o Quadril e Virilha (Frames 800-900)
- **Referência Muscular:** Novas referências de glúteos e coxas são introduzidas para guiar a forma.
- **Fechamento da Virilha:** A extrusão final do torso deve preparar a divisão para as pernas.
- **Topologia em "V":** A forma do baixo ventre tende a formar um V, onde os loops centrais se encontrarão para fechar a virilha, deixando aberturas laterais para as pernas.

### 2.4 Refinamento da Virilha e Abertura das Pernas (Frames 900-1000)
- **Refinamento da Abertura da Perna (Frames 900-1000):** Cria-se uma topologia de "fralda" (underwear line) que define onde a perna começa, crucial para deformação correta.
- **Refinamento Pós-Braço (Frames 1750-1800):** 
    - A atenção retorna ao quadril para ajustes finos.
    - Verifica-se a silhueta lateral e a transição glúteo-coxa.
    - Ajuste de loops na virilha para evitar "pinching" durante a animação.
- **Overlay Muscular:** Imagens de anatomia (glúteos, isquiotibiais) são sobrepostas na viewport para alinhar a borda da abertura da perna com a linha muscular real.
- **Loops da Perna:** A abertura da perna é arredondada e ajustada para garantir que, ao extrudar a perna, os polígonos não fiquem distorcidos.

### 2.5 Extrusão das Pernas (Frames 1000-1100)
- **Extrusão do Tubo das Pernas:** A partir da abertura criada, as pernas são extrudadas para baixo.
- **Atenção à Postura (S-Curve):** Na vista lateral, as pernas não descem retas. Elas seguem a curva "S" natural da postura feminina estilizada (coxas para frente, panturrilhas para trás).
- **Rotação de Loops:** A cada extrusão, os loops são rotacionados para manter o fluxo poligonal perpendicular à linha do osso (fêmur).

## 🧩 Fase 3: Arms & Hands (Braços e Mãos)
### 3.1 Modelagem do Braço (Frames 1250-1300+)
- **Técnica de Componente Separado:** O braço não é extrudado diretamente do ombro imediatamente. Ele é modelado como um cilindro separado (bloco) para focar na topologia da articulação.
- **Topologia do Cotovelo (Frames 1350-1400):** 
    - A topologia não é um simples tubo reto. É inserido um "Diamante" (ou fluxo desviado) na ponta do cotovelo.
    - Isso é feito cortando e deslizando arestas para criar geometria extra na parte externa da dobra, evitando que o volume colapse quando o braço dobrar.
- **Ajuste de Vértices:** O cilindro do braço é rotacionado e escalado para alinhar perfeitamente com a referência (Blueprint), com loops mais densos nas articulações (cotovelo/pulso) e mais espaçados no bíceps/antebraço.
- **Refinamento de Proporção (Frames 1400-1500):** 
    - A espessura do pulso é ajustada para ser mais fina que o cotovelo.
    - O comprimento do antebraço e do braço superior é verificado para garantir que o cotovelo alinhe com a cintura (ou conforme referência estilizada).

- **Conexão Braço-Corpo (Frames 1680-1700):**
    - **Ferramenta Chave:** O addon **LoopTools > Bridge** é utilizado para criar a conexão limpa entre os loops do corpo e do braço.
    - **Contagem de Vértices:** Essencial que seja idêntica (ex: 12 vértices no buraco do corpo / 12 na raiz do braço).
    - **Sculpting Pós-Conexão:** Imediatamente após a união, entra-se no Sculpt Mode (Grab/Smooth) para relaxar a tensão na área do ombro/axila e garantir um fluxo orgânico.

### 3.2 Modelagem da Mão (Frames 1900+)
*Análise pendente*

## 🧩 Fase 5: Breasts (Seios - Frames 1850+)
- **Técnica de Blockout:** Diferente de extrudar diretemente do peito, utiliza-se uma **UV Sphere** separada para definir o volume e o formato inicial.
    - **Configuração:** Segments/Rings padrão (ex: 16 ou 32) ajustados para 'Low Poly' mais tarde.
    - **Rotação:** A esfera é rotacionada 90º no eixo X para que o polo da esfera aponte para frente (direção do mamilo).
    - **Posicionamento:** Alinhada com o Blueprint frontal e lateral, garantindo que "pouse" corretamente sobre a caixa torácica.
- **Otimização da Geometria (Frames 1920-1950):**
    - A esfera original é muito densa. O artista seleciona anéis de arestas (Edge Rings) e usa **Checker Deselect** seguido de **Dissolve Edges** para reduzir a contagem de polígonos pela metade ou mais, combinando com a densidade do torso.
    - A parte traseira da esfera (que entra no corpo) é deletada.
- **Modelagem da Forma (Frames 1950-2000):**
    - A esfera é achatada levemente e rotacionada para seguir a curvatura do músculo peitoral.
    - A borda aberta da esfera é ajustada para preparar a conexão com a malha do corpo.
- **Conexão Seio-Corpo (Frames 2050-2200):**
    - **Preparação do Torso:** No modo de edição do corpo, faces são deletadas na região do peitoral para criar um "soquete" ou buraco onde o seio será encaixado.
    - **Alinhamento:** O buraco recortado no corpo deve ter uma contagem de vértices similar ou adaptável à borda aberta da esfera do seio.
    - **Junção de Objetos:** Em *Object Mode*, seleciona-se o seio e depois o corpo, e usa-se **Ctrl+J (Join)** para torná-los um único objeto.
    - **Soldagem (Bridge):** Seleciona-se o loop de arestas do buraco do peito e o loop da base do seio. Usa-se **LoopTools > Bridge** (ou Menu Edge > Bridge Edge Loops) para criar as faces de conexão.
    - **Limpeza de Topologia (Frames 2310-2380):**
         - Ajuste manual de vértices usando **Vertex Slide (Shift+V)** para melhorar o fluxo das arestas.
         - Uso frequente de **Merge (M)** (Often 'At First' or 'At Last') para colapsar geometria desnecessária ou triângulos formados durante a ponte, mantendo a malha limpa (quads).
    - **Refinamento Escultural (Frames 2380-2400):**
         - Volta-se ao **Sculpt Mode** para ajustar o volume global.
         - Uso da ferramenta **Elastic Deform** (ou Grab) para dar "peso" ao seio (simular gravidade) e suavizar a transição axila-peitoral.
    - **Ajuste da Axila e Perfil (Frames 2410-2500):**
         - Verificação constante da silhueta lateral contra o *Background Reference* (desenho 2D).
         - Limpeza específica de pólos na região da axila (onde o seio encontra o braço) para evitar artefatos de sombreamento (shading artifacts) com o *Subdivision Surface* ativado.
    - **Polimento Final do Torso (Frames 2510-2600):**
         - Verificação do fluxo da Clavícula e do Músculo Peitoral.
         - Ajustes finais de proporção frontal e lateral.
         - Uso leve de *Elastic Deform* para garantir que a tensão da malha pareça natural (sem partes "esticadas").
    - **Refinamento do Abdômen e Cintura (Frames 2610-2700):**
         - Adição de cortes horizontais extras (*Loop Cuts*) na região do estômago para suportar melhor a deformação e definir a silhueta da cintura.
         - Escultura da região da crista ilíaca (osso do quadril) para dar definição óssea sutil, quebrando a forma "cilíndrica" simples do tronco.
    - **Ajuste Isolado com Máscaras (Frames 2710-2740):**
         - Uso de **Sculpt Masks** (pintar área de vermelho) para isolar os seios. Isso permite ajustar o torso ao redor sem deformar o seio, ou vice-versa.

## 🧩 Fase 4: Legs & Feet (Pernas e Pés) (Frames 2750+)
- **Extrusão da Perna (Frames 2750-2800):**
    - Seleciona-se o loop da abertura da perna (criado na Fase 3).
    - Extrusão vertical (**E, Z**) descendo até o tornozelo em etapas (Coxa -> Joelho -> Panturrilha -> Tornozelo).
    - A cada extrusão, ajusta-se a escala (**S**) e posição (**G**) para alinhar com o *Background Reference* (Frontal e Lateral).
    - Atenção especial à curvatura da coxa e da panturrilha.
- **Definição do Joelho e Panturrilha (Frames 2810-2900):**
    - Ajuste fino da curvatura da panturrilha na vista lateral (Side View).
    - **Topologia do Joelho:** Adição de cortes extras (*Loop Cuts*) na frente e atrás do joelho para permitir a dobra correta. Geralmente cria-se uma estrutura em "diamante" ou 3 loops próximos para evitar distorção na animação.
- **Refinamento Final das Pernas (Frames 2910-2980):**
    - Uso de *Sculpt Mode* (Elastic Deform) para ajustar a silhueta da panturrilha e a "fossa poplítea" (atrás do joelho).
    - Verificação da conexão entre as pernas (gap da coxa) na vista traseira.
    - Verificação da conexão entre as pernas (gap da coxa) na vista traseira.
    - O tutorial encerra a Parte 2 com o corpo modelado até o tornozelo, pronto para a conexão com Pés e Mãos (que geralmente são tutoriais separados ou Part 3).

## Conclusão da Parte 2 (Body)
Ao final desta etapa, o personagem deve ter:
1. **Torso completo** com topologia limpa para deformação (anéis no ombro, peito e virilha).
2. **Braços e Pernas** conectados, com atenção às proporções e silhueta.
3. **Mãos e Pés** ainda não detalhados (apenas "tocos" ou cilindros básicos), aguardando a próxima fase.
4. **Escala e Proporção** verificadas constantemente contra o *Background Reference*.
