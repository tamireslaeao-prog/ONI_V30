# Mise en Place - Vectorização de Logo (ONI V25)

> **Tarefa:** Vetorizar imagem PNG (`target_logo.png`) e converter para Shapes no Photoshop.
> **Software:** Photoshop 2024 / ONI Vector Factory
> **Data:** 2026-01-26

## Simulação de Tarefa: Vectorization Pipeline

### Fase 1: Análise e Conversão (Raster -> SVG)

| Passo | Endpoint | Visualização | Análise | Fallback |
|-------|----------|--------------|---------|----------|
| 1.1 | `run_command` python vision_factory | `target_logo.png.svg` | O SVG foi gerado corretamente? | Usar `potrace` manual ou `browser_subagent` (Vector Magic) |
| 1.2 | `view_file` SVG | Conteúdo XML | Caminhos (paths) parecem válidos? | Re-executar com parâmetros de contraste |

### Fase 2: Compilação (SVG -> JSX)

| Passo | Endpoint | Visualização | Análise | Fallback |
|-------|----------|--------------|---------|----------|
| 2.1 | `run_command` python vector_factory | Output no terminal | Gerou `render_ultra_target_logo.jsx`? | Verificar `template_jsx_ultra.jsx` |
| 2.2 | `view_file` JSX | Código JSX | Sintaxe válida? Variáveis substituídas? | Edição manual do JSX |

### Fase 3: Renderização (Photoshop - Método Vector Factory)

| Passo | Endpoint | Visualização | Análise | Fallback |
|-------|----------|--------------|---------|----------|
| 3.1 | `GET /api/open?name=Photoshop` | `window_title` | Photoshop aberto? | `Start-Process` |
| 3.2 | `GET /api/photoshop/connect` | Status 200 | Conexão COM ativa? | Reiniciar PS |
| 3.3 | `run_command` (Executar JSX) | Monitorar Tela | Shapes desenhados? | **Fase 4 (Fallback Manual)** |

### Fase 4: Fallback Manual (Protocolo VETORIZAR_PS)

| Passo | Endpoint | Visualização | Análise | Fallback |
|-------|----------|--------------|---------|----------|
| 4.1 | `GET /api/open` (Abri imagem original) | Imagem Raster | Imagem carregada? | - |
| 4.2 | `GET /api/keys?keys=ctrl,click` (Layer Thumb) | Seleção Ativa | "Marching Ants" visíveis? | Magic Wand |
| 4.3 | `GET /api/click` (Context Menu > Make Work Path) | Diálogo Tolerância | Definir 1.0 ou 2.0px | - |
| 4.4 | `GET /api/click` (Solid Color Fill) | Shape Layer | Vetor criado? | - |

### Recursos Anexados
- [x] Script Visão: `Modules/Photoshop/VectorFactory/vision_factory_ultra.py`
- [x] Script Vetor: `Modules/Photoshop/VectorFactory/vector_factory_ultra.py`
- [x] Template JSX: `Modules/Photoshop/VectorFactory/template_jsx_ultra.jsx`
- [x] Imagem Alvo: `D:\DESIGN\psd_sources\target_logo.png`

## Checklist de Pontos Fracos

### 1. Qualidade do Traço
- [ ] O logo tem texto pequeno? (Sim: "PSICOFARMACOS...")
    - *Risco:* OCR falhar ou vetor ficar distorcido.
    - *Solução:* Recriar texto manualmente no Photoshop se a vetorização automática falhar.

### 2. Cores
- [ ] O SVG preserva cores?
    - *Risco:* `vision_factory` pode gerar P&B.
    - *Solução:* `vector_factory` tem suporte a grupos de cor. Verificar se o input SVG tem atributos `fill`.

### 3. Execução JSX
- [ ] O script é seguro?
    - *Risco:* Loops infinitos no Photoshop.
    - *Solução:* O template usa `suspendHistory` e tem limite de shapes.

## Refinamento V2
- Adicionado passo 3.5 para validação visual final.
- Adicionado fallback para texto (recriação manual).

---

**Posso começar?**
