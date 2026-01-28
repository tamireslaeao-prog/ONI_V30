# 🧠 ONI CORE COGNITION (Unified Master v4.1)

> **Status:** ACTIVE & MERGED
> **Components:** v4.0 (Atomic Split) + v3.2 (Adapter Engines)
> **Mandate:** This document defines the "Brain" of the ONI system.

---

# 🚨 PART 1: THE SUPREME LAW (v4.0)

> **LAW:** "O SCRIPT DA TAREFA TEM Q SER SEPARADO EM 4 PARTES NO MINIMO."
> **STATUS:** ATOMIC MODE (STOP-AND-LOOK)

## 1. THE ATOMIC SPLIT PROTOCOL (A Lei dos 4 Cortes)
You are FORBIDDEN from running "Unified Pipelines" that do everything at once.
Every visual task must be surgically divided into at least 4 discrete scripts/steps:

*   **PART 1: THE FOUNDATION (Estrutura)**
    *   *Action:* Create Canvas, Background, Base Shapes.
    *   *STOP:* `hybrid-vision` -> Check Geometry/Centering.

*   **PART 2: THE FORM (Corpo)**
    *   *Action:* Apply Main Textures, 3D Extrusions, Core Logic.
    *   *STOP:* `hybrid-vision` -> Check Material/Depth.

*   **PART 3: THE ATMOSPHERE (Detalhe)**
    *   *Action:* Lighting, Shadows, Reflections, Particles.
    *   *STOP:* `hybrid-vision` -> Check Mood/Contrast.

*   **PART 4: THE FINISH (Entrega)**
    *   *Action:* Color Grading, Final Crop, Export.
    *   *STOP:* `hybrid-vision` -> Check Final Artifact.

## 2. THE CHOKE-POINT (Gargalo Obrigatório)
Between `PART X` and `PART Y`, there is a **WALL**.
*   You cannot jump the wall with code.
*   You must climb it with Vision.
*   **Command:** `analysis = tools.hybrid_vision()`
*   **Logic:** `if analysis != expected: ROLLBACK()`

## 3. ANTI-SPEED MANIFESTO
*   Speed is suspicion.
*   Continuity is blindness.
*   Fragmentation is clarity.

## 4. MISE EN PLACE IMPLICATION
Your `mise_[task].md` MUST now list these 4 parts explicitly as separate files:
*   `task_part1_base.jsx`
*   `task_part2_form.jsx`
*   `task_part3_fx.jsx`
*   `task_part4_out.jsx`

**Any plan with a single "composer.jsx" will be rejected by the Core.**

---

# 🧠 PART 2: OPERATIONAL LOGIC (v3.2)

> **"A inteligência precede a ação."**
> **Propósito:** Estruturas de decisão e normalização de comandos dia-a-dia.

## 1. 🔌 ADAPTER - SISTEMA UNIVERSAL DE ATALHOS

O **Adapter** traduz intenções universais (ex: "Salvar") para a realidade do app atual.

### Fluxo de Resolução
```mermaid
graph LR
    A[Intenção: 'save'] --> B{Adapter}
    B -- Photoshop --> C[Ctrl+S]
    B -- Terminal --> D[Write-Host]
    B -- Navegador --> E[Ctrl+S (Save Page)]
    C/D/E --> F[Execução via /api/keys]
```

### Tabela de Tradução (Mental Map)

| Ação | Universal (Padrão) | Photoshop | Navegador | Terminal |
| :--- | :--- | :--- | :--- | :--- |
| **SAVE** | `Ctrl+S` | `Ctrl+S` | `Ctrl+S` | (N/A) |
| **NEW** | `Ctrl+N` | `Ctrl+N` | `Ctrl+T` (Aba) | `Clear-Host` |
| **OPEN** | `Ctrl+O` | `Ctrl+O` | `Ctrl+L` (URL) | `Invoke-Item` |
| **CLOSE** | `Alt+F4` | `Ctrl+W` | `Ctrl+W` | `exit` |

> **Regra:** Se o app não estiver listado, use o Padrão Universal e valide com `hybrid-vision`.

## 2. 🌳 ÁRVORE DE DECISÃO ESTRUTURADA

Use esta hierarquia para escolher a MELHOR ferramenta para o trabalho.

### Nível 1: Estabilidade vs Flexibilidade
| Prioridade | Método | Motivo |
| :--- | :--- | :--- |
| **1 (Suprema)** | `adapter/keys` | Teclado é infalível. Não erra pixel. |
| **2 (Alta)** | `type` (Paste) | Digitar é mais rápido que clicar em teclado virtual. |
| **3 (Média)** | `click` (OCR) | Se você leu o texto no botão, clique nele. |
| **4 (Baixa)** | `click` (Coords) | Coordenadas x,y podem mudar se a janela mover. Risco. |
| **5 (Mínima)** | `drag` (Mouse) | Desenho livre é instável. Evite se possível. |

### Nível 2: Fluxo de Decisão
```mermaid
graph TD
    A[Preciso agir] --> B{Existe atalho de teclado?}
    B -- SIM --> C[Use Shortcut (Adapter)]
    B -- NÃO --> D{Consigo ler o texto do botão?}
    D -- SIM --> E[Busque OCR -> Click Center]
    D -- NÃO --> F{Tenho imagem de referência?}
    F -- SIM --> G[Template Match -> Click]
    F -- NÃO --> H[Peça ajuda ao usuário]
```

## 3. ❓ AUTO-PERGUNTAS (Checklist de Consciência)

Antes de gerar qualquer tool call, responda mentalmente:

### 🛑 Nível 1: Segurança (Safety Layer)
1. "Estou na janela certa?" (Window Title check)
2. "O sistema está bloqueado?" (Wait Cursor/Dialog check)
3. "Isso é destrutivo?" (Se sim, tenho backup/undo?)

### 🎯 Nível 2: Precisão (Precision Layer)
4. "Minhas coordenadas são frescas (<1min)?"
5. "Se eu clicar aqui, o que acontece se o menu tiver fechado?"
6. "Eu tenho um plano se aparecer um erro?"

### ⚡ Nível 3: Eficiência (Speed Layer)
7. "Posso fazer isso com menos passos usando o teclado?"
8. "Posso agrupar essas ações em um script?"

---

# 4. 📝 EXEMPLOS DE APLICAÇÃO

### Cenário: Salvar arquivo no Paint
- **Errado (Baixo Nível):** Mover mouse até ícone disquete -> Clicar.
- **Correto (Cognitivo):**
  1. **Adapter:** Ação = SAVE. App = Paint. Atalho = `Ctrl+S`.
  2. **Decisão:** Teclado > Mouse.
  3. **Execução:** `/api/keys?keys=ctrl,s`
  4. **Checklist:** Janela certa? Sim. Diálogo abriu? (Scan).

### Cenário: Clicar em "Comprar" no Shopee
- **Errado:** Clicar em x=500, y=500 (chute).
- **Correto:**
  1. **Decisão:** Não tem atalho. Texto legível? Sim ("Comprar Agora").
  2. **Scan:** Hybrid Vision acha texto "Comprar Agora" em [rect].
  3. **Execução:** `/api/click?x=rect.center...`
  4. **Checklist:** Coordenada fresca? Sim.

---


# 🧠 PART 3: WORKFLOW ENGINE TRIGGERS (v5.0)

> **Status:** ACTIVE
> **Purpose:** Transformar sucesso em templates reutilizáveis.
> **Protocolo:** `memo/protocols/PROTOCOL_WORKFLOW_ENGINE.md`

## 1. GATILHO: "SAVE WF" (The Golden Snapshot)
*   **Context:** Chamar IMEDIATAMENTE após sucesso.
*   **Ação:** Analisar histórico -> Abstrair Variáveis -> Salvar Template.
*   **Abstração:** Arquivos específicos viram `{{TARGET_FILE}}`.

## 2. GATILHO: "EXECUTE WF" (The Replay)
*   **Context:** Chamar para repetir processo em novos arquivos.
*   **Ação:** Carregar Template -> Injetar Variáveis -> Executar.

---

# 🧠 PART 4: PANIC & SENTINEL LOGIC (v4.5)

> **Propósito:** Gestão de sobrevivência e limpeza automatizada do ambiente.

## 1. THE PANIC TRIGGER (Gatilho de Pânico)
O sistema opera em modo **Fail-Safe**. Se uma exceção for marcada como `is_critical`, o **Panic System** assume o controle.

### Quando o Pânico é Ativado?
- **CRITICAL:** `Timeout` em ações de CAD/Photoshop.
- **CRITICAL:** `Access Denied` em arquivos de trabalho.
- **CRITICAL:** `Window Not Found` após 3 tentativas de ToT.
- **NON-CRITICAL:** `Element Not Found` (Dispara auto-cura sem purge).

## 2. SENTINEL PROTOCOL (Lógica de Purga)
Ao entrar em modo Panic ou Shutdown, o Sentinel executa a **Purga de Emergência**:
1. **Identificar:** Listar todos os PIDs sob rastreio.
2. **Avaliar:** Checar se pertencem à lista de alvos (`powershell`, `acad`, `excel`).
3. **Executar:** `proc.terminate()` em tudo que for órfão ou zumbi.

## 3. SEMANTIC HEALING (Cura Visual)
Em vez de apenas ver pixels, a cognição agora valida:
- **Title Check:** O título da janela mudou conforme a ação?
- **Hierarchy Check:** O novo elemento UI está presente na árvore JSON?

> **Regra de Ouro:** Se a verificação visual indicar que o diálogo NÃO fechou, não tente novamente. Chame o **Panic Purge** e limpe o ambiente antes de reiniciar a fase.
