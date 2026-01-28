---
description: skill_desktop_turbo
---
// turbo-all

# 🖥️ SKILL MODULE: DESKTOP MASTER (v3.2 - AutoCAD Bridge)

> **Contexto:** Carregar ao interagir com Windows, Office, Paint, Photoshop, AutoCAD, Explorer.
> **Foco:** Sistema de Arquivos, Coordenadas, Desenho, Janelas Nativas.
> **AutoCAD:** Use `memo/ONI_AUTOCAD_MASTERY.md` para tarefas de engenharia.

---

# 0. 🔍 PATH DISCOVERY (DYNAMIC RESOLUTION)
> **Vital Update:** Hardcoded paths (e.g., "Blender 4.0") are DEPRECATED.

**Protocolo de Descoberta:**
Sempre que precisar encontrar o executável do Blender ou After Effects, use o script de resolução dinâmica:

```powershell
$AppInfo = powershell -ExecutionPolicy Bypass -File "app/core/Resolve-AppPaths.ps1" | ConvertFrom-Json
$BlenderPath = $AppInfo.Blender
$AEPath = $AppInfo.AfterEffects
```

**Regra:** Se o script retornar `$null`, pergunte ao usuário. Caso contrário, confie no script.

---

# 1. 📐 REGRAS DE COORDENADAS E DESENHO

## Obrigatório: Base em `canvas_limits`
**NUNCA use coordenadas arbitrárias.** Sempre calcular com base no JSON `canvas_limits` retornado pelo Hybrid Vision.

### Exemplo de JSON:
```json
{ "x": 150, "y": 200, "width": 1280, "height": 720, "center_x": 790, "center_y": 560 }
```

### Fórmulas de Cálculo:
- **Centro:** `(center_x, center_y)`
- **Topo Esq:** `(x + margem, y + margem)`
- **Meio Esq:** `(x + width*0.25, center_y)`
- **Meio Dir:** `(x + width*0.75, center_y)`

## Validação Pré-Clique
1. A coordenada está dentro do retângulo do canvas (`x` até `x+width`)?
2. Corresponde visualmente ao que vejo no `annotated_path`?

---

# 2. 🔀 MULTI-APP SWITCHING (Troca de Janelas)

**Sequência Obrigatória:**
1. **ABRIR:** `open?name=app` (Garante que o processo existe)
2. **VERIFICAR:** `hybrid-vision` (O app apareceu na barra de tarefas?)
3. **FOCAR:** `focus?title=Janela` (raz o app para frente)
4. **CONFIRMAR:** `hybrid-vision` (Tenho certeza visual que estou no app?)

**Erro Comum:** Enviar teclas para o app errado porque esqueceu do passo 3 (Focus).

---

# 3. 💾 FILE SYSTEM OPERATIONS (Protocolo PWF)

Para criar/editar arquivos (Word, Notepad, RTF, Excel):

1. **NÃO use** o menu "Arquivo > Novo" da interface. É lento e propenso a erros de diálogo.
2. **CRIE** o arquivo no disco via comando:
   `write_to_file "C:\Caminho\Relatorio.rtf"`
3. **ABRA** o processo direcionado:
   `Start-Process "C:\Caminho\Relatorio.rtf"`
4. **EDITE** visualmente o documento aberto.
5. **SALVE** com `Ctrl+S`.
   *Como o arquivo já tem nome no disco, o diálogo "Salvar Como" NÃO aparecerá.*

---

# 4. 🎨 ARTMASTER (Desenho & Criatividade)

## Ferramentas
- `/api/artmaster`: Para formas perfeitas (Círculos, Retângulos).
- `/api/mouse/safe-drag`: Para traços livres ou sliders.

## Ciclo de Desenho
1. Calcular coordenadas.
2. Executar traço.
3. **Verificar Visualmente** (Hybrid Vision).
4. Se errou: `Ctrl+Z` (Rollback) e ajustar coordenadas.

### 6. Visual Brush Control (Photoshop)
**Concept:** Natural "Human-Like" Interaction (No Typing).
**Mechanism:**
1. **Size/Hardness:** Move to Center -> Right Click -> Drag Sliders (Size Y:~610, Hardness Y:~660) -> Enter.
2. **Color:** Click Docked Color Panel Spectrum (Top Right, X:~1620-1790, Y:~140).
3. **Script Reference:** `app/scripts/demo_v5_corrected.ps1`
**Usage:**
```powershell
./app/scripts/demo_v5_corrected.ps1 # Runs complete visual demo with corrected offsets
```

---

## II. File System OperationsWS & EXPLORER SHORTCUTS

| Ação | Atalho | Endpoint |
|------|--------|----------|
| **Menu Contexto** | `Shift + F10` | (Prefira este ao clique direito) |
| Alternar Janela | `Alt + Tab` | `/api/keys?keys=alt,tab` |
| Fechar Janela | `Alt + F4` | `/api/keys?keys=alt,f4` |
| Mostrar Desktop | `Win + D` | `/api/keys?keys=win,d` |
| Explorador | `Win + E` | `/api/keys?keys=win,e` |
| Barra Endereço | `Ctrl + L` | `/api/keys?keys=ctrl,l` |
| Renomear | `F2` | `/api/keys?keys=f2` |
