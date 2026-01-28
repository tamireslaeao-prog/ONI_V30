
# 🛡️ PROTOCOLO UNIVERSAL DE MANIPULAÇÃO PHOTOSHOP (V11)
> **Codinome:** "ONI FULL SPECTRUM"
> **Data de Implantação:** 21/01/2026
> **Status:** IMUTÁVEL / PRODUÇÃO

## 📜 Manifesto
Este documento registra a arquitetura do algoritmo V11, projetado para manipular *qualquer* arquivo PSD, independentemente de sua estrutura, bloqueios, janelas pop-up ou metadados de lixo.

---

## 🧠 Arquitetura "Blindada"

### 1. O Conceito de "Full Spectrum Cleanup"
Diferente de scripts comuns que apenas deletam camadas de texto, o V11 entende que o "Lixo" pode assumir várias formas.
- **Texto Direto:** "Edit me", "Preview", "Rate it".
- **Pastas (Groups):** "Info", "Help", "Additional Text".
- **Smart Objects:** "Title", "Preview Object".

**Lógica de Detecção:**
O algoritmo varre recursivamente a árvore de camadas e aplica uma *Blacklist Heurística*. Se detectado, o script tenta:
1. **Desbloquear** a camada/pasta (`allLocked = false`).
2. **Deletar** a camada.
3. Se deletar falhar, **Ocultar** (`visible = false`).

### 2. O Processo Sentinela (Anti-Bloqueio)
O Photoshop é síncrono e bloqueante. Um diálogo de "Fonte Ausente" para a execução.
**Solução V11:**
- Um processo paralelo (`Sentinel`) roda fora da thread principal.
- Ele usa **Hybrid Vision** (visão computacional) para detectar diálogos modais.
- Se encontrar palavras como "OK", "Resolver", "Substituir", ele clica fisicamente (`click`) ou envia `Enter`.

### 3. Estratégia de Edição "Tridente"
O V11 não assume como o PSD foi feito. Ele tenta três abordagens em ordem:

*   **Fase 1: Busca de Smart Objects (Recursiva)**
    *   Procura por palavras-chave: `edit`, `text`, `mockup`, `place`.
    *   Proteção: Ignora Smart Objects que parecem ser "títulos" (lixo), a menos que sejam a única opção.
    *   Ação: Abre o SO, substitui o texto, salva e fecha.

*   **Fase 2: Edição Direta (Style Packs)**
    *   Se nenhum Smart Object for editado, o V11 assume que é um arquivo de "Estilos de Texto".
    *   Varre todas as camadas de texto visíveis (que sobreviveram ao Cleanup).
    *   Substitui o conteúdo diretamente.

*   **Fase 3: Fallback de Fonte (Anti-Crash)**
    *   Ao editar texto, se a fonte original causar erro (ausente/corrompida), o V11 força automaticamente `Arial-BoldMT` para garantir que o texto "ONI" apareça, custe o que custar.

---

## 🛠️ Implementação Técnica

O código fonte oficial reside em:
`app/services/photoshop/universal_bridge_v11.py`

### Dependências
- `win32com.client` (COM Interface)
- `requests` (API ONI)
- `multiprocessing` (Sentinel)

---

## 🎯 Regras de Ouro
1. **Nunca Pare:** Se uma camada estiver bloqueada, desbloqueie. Se falhar, ignore.
2. **Nunca Peça:** Se houver um diálogo, aceite-o (Enter/OK).
3. **Limpe Primeiro:** Nunca edite um arquivo sujo. Remova meta-dados antes de processar.

---
*Documentado por Antigravity (ONI System).*
