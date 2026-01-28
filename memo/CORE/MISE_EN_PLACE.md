# 🍳 Mise en Place - Metodologia Obrigatória de Preparação de Tarefas

> **"Tudo em seu lugar antes de começar."**  
> Este documento descreve a metodologia OBRIGATÓRIA que deve ser seguida ANTES de iniciar qualquer tarefa de automação visual.

> ⚠️ **IMPORTANTE:** Durante a EXECUÇÃO de cada ação, aplicar também o **Tree of Thoughts (ToT)**.
> Ver: `memo/TREE_OF_THOUGHTS.md`

---

## 📋 HIERARQUIA DE METODOLOGIAS

```
MISE EN PLACE (Plano Geral) ──────────────────────────┐
│                                                      │
│  1. Simular todos os passos                         │
│  2. Analisar gaps                                   │
│  3. Refinar até sem gaps                            │
│  4. Perguntar "Posso começar?"                      │
└──────────────────────────────────────────────────────┘
                      │
                      ▼ (ANTES de cada ação)
┌──────────────────────────────────────────────────────┐
│  👁️ HYBRID VISION SCAN (OBRIGATÓRIO)                 │
│                                                      │
│  1. GET /api/hybrid-vision/desktop?nocache=pre      │
│  2. view_file(annotated_path) ← OLHAR IMAGEM        │
│  3. Extrair coordenadas do JSON                     │
└──────────────────────────────────────────────────────┘
                      │
                      ▼ (Durante execução)
┌──────────────────────────────────────────────────────┐
│  TREE OF THOUGHTS (ToT) - ANTES DE CADA AÇÃO        │
│                                                      │
│  Para CADA ação do plano:                           │
│  1. Gerar N estratégias diferentes                  │
│  2. Escolher a melhor                               │
│  3. Executar                                        │
│  4. Se falhar → Tentar próxima estratégia           │
└──────────────────────────────────────────────────────┘
                      │
                      ▼ (DEPOIS de cada ação)
┌──────────────────────────────────────────────────────┐
│  👁️ HYBRID VISION VERIFY (OBRIGATÓRIO)               │
│                                                      │
│  1. GET /api/hybrid-vision/desktop?nocache=post     │
│  2. view_file(annotated_path) ← CONFIRMAR RESULTADO │
│  3. Ação funcionou? SIM → próxima / NÃO → fallback  │
└──────────────────────────────────────────────────────┘
```

> [!CAUTION]
> **REGRA SUPREMA:** O `annotated_path` é o **ÚNICO VISUALIZADOR PRIORITÁRIO**.
> É **PROIBIDO** executar QUALQUER ação (click, type, keys, draw) sem:
> - SCAN PRÉ (antes da ação)
> - SCAN PÓS (depois da ação)
> 
> **Referência completa:** `memo/_CORE_VISION_PROTOCOL.md`

---

## 📋 O QUE É MISE EN PLACE?

Mise en Place é um termo culinário francês que significa "tudo em seu lugar". Na automação visual, significa:

1. **Analisar** a tarefa completa antes de executar qualquer ação
2. **Preparar** todos os recursos necessários (guias, atalhos, referências)
3. **Simular** cada passo em detalhes (endpoints, verificações, fallbacks)
4. **Identificar** pontos fracos e ajustar o plano
5. **Pedir confirmação** do usuário antes de iniciar

---

## 🚨 QUANDO APLICAR (SEMPRE!)

Esta metodologia se aplica a **TODA tarefa** que envolve:
- Automação de interface gráfica (GUI)
- Múltiplos aplicativos
- Salvamento de arquivos
- Interações complexas

---

## 📝 ESTRUTURA OBRIGATÓRIA DA SIMULAÇÃO (PROTOCOLO MISE V2)

**REGRA DE OURO:** Antes de *qualquer* execução, você DEVE ciar um arquivo físico de simulação.

1.  **Local:** `  memo\mise\`
2.  **Nome:** `mise_en_place_[NomeTarefa]_[Software]_[Hora].md` (Ex: `mise_en_place_Ninja_Turtle_Photoshop_2120.md`)
3.  **Conteúdo:** Cópia fiel da estrutura abaixo (Simulação + Gaps + Checklist).

**Antes de iniciar qualquer tarefa, criar uma tabela com:**

```markdown
## Simulação de Tarefa: [NOME DA TAREFA]

### Fase 1: [Nome da Fase]

| Passo | Endpoint | Visualização | Análise | Fallback |
|-------|----------|--------------|---------|----------|
| 1.1   | `GET /api/xxx` | Screenshot salvo em `temp/` | O que verificar | Se falhar, fazer Y |
| 1.2   | `browser_subagent` | Ver imagem em `temp/oni_screenshot.png` | Encontrar elemento X | Se não achar, usar atalho |

### Recursos Anexados
- [x] Guia do App: `app/skills/[app]_complete_guide.json`
- [x] Menus: `app/skills/[app]_menus.json`
- [x] Imagens de referência: `app/skills/[app]_*.png`
```

---

## 📂 DIRETÓRIO DE SKILLS DISPONÍVEIS

Antes de começar, consultar os arquivos de referência em `app/skills/`:

### Guias de Aplicativos (JSON)
| Arquivo | Aplicativo | Conteúdo |
|---------|------------|----------|
| `coreldraw_complete_guide.json` | CorelDRAW | Atalhos, técnicas, workflows |
| `coreldraw_menus.json` | CorelDRAW | Estrutura de menus e hotkeys |
| `photoshop.json` | Photoshop | Ferramentas e atalhos |
| `after_effects_guide.json` | After Effects | Animação e efeitos |
| `blender_guide.json` | Blender | Modelagem 3D |
| `excel_guide.json` | Excel | Fórmulas e macros |
| `word_complete_guide.json` | Word | Formatação e estilos |
| `windows_complete_guide.json` | Windows | Sistema operacional |

### Imagens de Referência (PNG)
| Arquivo | Descrição |
|---------|-----------|
| `core_ferramentas.png` | Barra de ferramentas CorelDRAW |
| `core_menu_arquivo.png` | Menu Arquivo CorelDRAW |
| `core_menu_editar.png` | Menu Editar CorelDRAW |
| `core_menu_exibir.png` | Menu Exibir CorelDRAW |
| `core_menu_layout.png` | Menu Layout CorelDRAW |
| `core_menu_objeto.png` | Menu Objeto CorelDRAW |

---

## 🔍 CHECKLIST DE PONTOS FRACOS

Para cada fase da simulação, verificar:

### 1. Foco de Janela
- [ ] O app correto estará em foco?
- [ ] Como recuperar se perder o foco?
- [ ] Usar `/api/open` em vez de `Alt+Tab`

### 2. Estados Intermediários
- [ ] Há diálogos modais esperados? (Ex: "Escolher Perfil", "Salvar Como")
- [ ] Como detectar e tratar cada diálogo?
- [ ] Quais atalhos funcionam em cada estado?

### 3. Coordenadas e Cliques
- [ ] As coordenadas vêm de onde? (OCR, browser_subagent, fixas?)
- [ ] Usar `calibrate-coord` antes de clicar?
- [ ] **SCP OBRIGATÓRIO:** O protocolo de `Safety Calibration` está previsto antes de desenhos/ações críticas?
- [ ] Mover mouse primeiro, verificar, depois clicar

### 4. Arquivos e Caminhos
- [ ] Caminhos são absolutos?
- [ ] Arquivo será salvo onde?
- [ ] Como verificar que o arquivo foi criado?

### 5. Timeouts e Esperas
- [ ] Apps pesados têm tempo de loading suficiente?
- [ ] Corel/Photoshop: mínimo 5-10s de espera
- [ ] Chrome: mínimo 3s após navegação

## 🔄 CICLO DE REFINAMENTO ITERATIVO (OBRIGATÓRIO)

> ⚠️ **CRÍTICO:** Uma simulação NÃO está completa até passar por este ciclo!

### Fluxo Obrigatório:

```
┌─────────────────────────────────────────────────────────────┐
│  1. SIMULAR                                                  │
│     Criar tabela completa com todos os passos               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. ANALISAR GAPS                                           │
│     - Verificar cada passo contra o checklist               │
│     - Identificar pontos fracos                             │
│     - Listar TODOS os problemas potenciais                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. CORRIGIR SIMULAÇÃO                                      │
│     - Incorporar mitigações DENTRO da tabela                │
│     - Adicionar passos de verificação onde faltam           │
│     - Atualizar fallbacks com soluções específicas          │
│     - Gerar NOVA versão da simulação (v2, v3...)           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. VERIFICAR REFINAMENTO                                   │
│     TODOS os gaps foram resolvidos?                         │
│     ├─ NÃO → Voltar para passo 2                           │
│     └─ SIM → Prosseguir para passo 5                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. PERGUNTAR: "Posso começar?"                             │
│     - Apresentar simulação FINAL (corrigida)                │
│     - Aguardar "OK" explícito do usuário                    │
│     - SÓ ENTÃO iniciar execução                             │
└─────────────────────────────────────────────────────────────┘
```

### Exemplo de Refinamento:

**Versão 1.0 (Gap identificado):**
| Passo | Endpoint | Fallback |
|-------|----------|----------|
| 2.7 | `GET /api/click?button=right` | - |

**Gap:** Menu contexto Win11 pode estar incompleto

**Versão 2.0 (Corrigida):**
| Passo | Endpoint | Fallback |
|-------|----------|----------|
| 2.6 | `GET /api/keys?keys=shift,f10` | - |
| 2.7 | `GET /api/do?action=wait&delay=0.5` | - |
| 2.8 | `browser_subagent` | Verificar menu CLÁSSICO |

### ❌ PROIBIDO:
- Identificar gaps e NÃO incorporar na simulação
- Perguntar "Posso começar?" com gaps não resolvidos
- Pular o ciclo de refinamento

### ✅ OBRIGATÓRIO:
- Cada gap identificado DEVE virar uma correção na tabela
- A simulação final NÃO PODE ter gaps conhecidos
- Versionar simulações (v1.0, v2.0) quando há mudanças significativas

---

## 📁 CAMINHO CORRETO PARA SCREENSHOTS

**SEMPRE usar o diretório do projeto para screenshots:**

```
temp\
```

**NÃO usar:**
```
C:\temp\  # ❌ Diretório global
file:///C:/temp/  # ❌ Pode não ser acessível
```

**Para browser_subagent:**
```python
browser_subagent(
    Task="Navigate to file:///temp/oni_screenshot.png ...",
    ...
)
```

---

## 🔄 EXEMPLO COMPLETO: Chrome → Salvar Imagem → Corel

### Fase 1: Chrome - Buscar Imagem

| Passo | Endpoint | Visualização | Análise | Fallback |
|-------|----------|--------------|---------|----------|
| 1.1 | `GET /api/screenshot-enhanced?nocache=...` | Salvo em `temp/oni_screenshot.png` | `active_window_process` = ? | - |
| 1.2 | `browser_subagent` em `temp/` | Ver imagem | É Profile Picker ou Chrome aberto? | - |
| 1.3 | Se Picker: Encontrar "Visitante" | Ver coords | Coords do botão Guest | Usar teclado `Tab+Enter` |
| 1.4 | `GET /api/do?action=move` | - | Mover antes de clicar | - |
| 1.5 | `GET /api/click` | - | Clicar | Se falhar, repetir 1.3-1.5 |
| 1.6 | `GET /api/type?text=cachorro` | - | Digitar busca | - |
| 1.7 | `GET /api/keys?keys=enter` | - | Confirmar busca | - |
| 1.8 | `GET /api/do?action=wait&delay=3` | - | Esperar página | - |
| 1.9 | `browser_subagent` | Ver resultados | Encontrar "Imagens" | - |

### Recursos Anexados para Chrome
- [x] `windows_complete_guide.json` - Para diálogos de "Salvar como"

### Fase 2: Corel - Importar Imagem

| Passo | Endpoint | Visualização | Análise | Fallback |
|-------|----------|--------------|---------|----------|
| 2.1 | `GET /api/open?name=CorelDRAW&wait=10` | - | Abrir Corel | - |
| 2.2 | `GET /api/screenshot-enhanced?nocache=...` | `temp/` | `process_name` = CorelDRW? | - |
| 2.3 | `GET /api/keys?keys=ctrl,n` | - | Novo documento | - |
| 2.4 | `GET /api/keys?keys=enter` | - | Confirmar diálogo | - |
| 2.5 | `GET /api/keys?keys=ctrl,i` | - | Abrir Import | Usar menu: `Alt+A, I` |
| 2.6 | `GET /api/type?text=...\cachorro.jpg&use_clipboard=true` | - | Digitar caminho | - |
| 2.7 | `GET /api/keys?keys=enter` | - | Confirmar Import | - |
| 2.8 | `GET /api/click?x=960&y=600` | - | Posicionar no canvas | - |

### Recursos Anexados para Corel
- [x] `coreldraw_complete_guide.json` - Atalhos principais
- [x] `coreldraw_menus.json` - Menu Arquivo > Importar = `Ctrl+I`
- [x] `core_menu_arquivo.png` - Referência visual do menu

---

## ✅ CHECKLIST FINAL ANTES DE INICIAR

- [ ] Simulação completa criada?
- [ ] Todos os endpoints listados?
- [ ] Pontos fracos identificados?
- [ ] Fallbacks definidos?
- [ ] Recursos de referência consultados?
- [ ] **👁️ Protocolo de Visão incluído na simulação?** (SCAN PRÉ/PÓS para cada ação)
- [ ] Perguntei "Posso começar?" ao usuário?
- [ ] Usuário respondeu "OK"?

**SE TODOS MARCADOS ✅ → Pode iniciar execução**

---

## 🔁 DURANTE A EXECUÇÃO (OBRIGATÓRIO)

Para **CADA** ação do plano, seguir este ciclo:

```
1. 🔍 SCAN PRÉ:    GET /api/hybrid-vision/desktop?nocache=pre_{timestamp}
2. 👁️ OLHAR:      view_file(annotated_path) ← VISUALIZAR IMAGEM
3. 📝 VALIDAR:    Elemento alvo existe? Coordenadas corretas?
4. ⚡ EXECUTAR:   A ação (click, type, keys)
5. ✅ SCAN PÓS:   GET /api/hybrid-vision/desktop?nocache=post_{timestamp}
6. 👁️ CONFIRMAR: view_file(annotated_path) ← RESULTADO ESPERADO?
7. 🔄 DECIDIR:    Sucesso → próxima ação | Falha → fallback
```

---

## 🧠 MEMORIZAR

Esta metodologia é **PERMANENTE** e deve ser aplicada a **TODAS** as tarefas daqui para frente.
Nenhuma tarefa de automação visual deve iniciar sem antes completar o Mise en Place.

**Data de implementação:** 2025-12-29
**Versão:** 3.0 (Adicionado Protocolo de Visão Obrigatória - Hybrid Vision SCAN PRÉ/PÓS)
