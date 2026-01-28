# 🐱‍👤 PROTOCOLO NINJA: SMART OBJECT TRANSPLANT
> **Origem do Conhecimento:** Video Tutorial (Timestamp 0:53)
> **Data de Assimilação:** 21/01/2026
> **Módulo:** Photoshop PhD

## 📋 O CONCEITO
Em vez de tentar "desconstruir" um efeito complexo (extraindo estilos CSS/JSON), nós **reutilizamos a engenharia original** do criador.
PSDs Premium modernos usam **Smart Objects** (.psb) para encapsular efeitos 3D, sombras e luzes.

**A Regra de Ouro:**
> "Não reinvente a roda. Use o carro inteiro."

---

## 🛠️ O FLUXO DE TRABALHO (WORKFLOW)

### 1. Colheita Intelligente (Smart Harvest)
*Script:* `oni_element_harvester.jsx`
*   **Ação:** Identifica o Grupo Principal ("Hero Element" ou "Text Effect") no arquivo de origem.
*   **Processo:** Duplica o Grupo/Smart Object INTEIRO para o documento de destino.
*   **Vantagem:** Preserva 100% da fidelidade (Blending modes, Clipping masks, 3D renders).

### 2. Edição Ninja (Deep Edit)
*Script:* `oni_smart_text_replacer.jsx`
*   **Ação:** Entra no Smart Object (`Edit Contents`).
*   **Busca:** Localiza a camada de texto Editável (geralmente uma camada de Texto simples sem efeitos, pois os efeitos estão no grupo pai ou aplicados sobre o Smart Object).
*   **Substituição:** Altera o texto (ex: de "Ramadan" para "ONI").
*   **Heurística:** Busca pela camada de texto com **maior tamanho de fonte** (para evitar editar textos secundários).

### 3. Selagem (Seal & Save)
*Script:* `demo_full_gold_oni.py` (Orquestrador)
*   **Ação:** Salva o `.psb` (atualizando o render no arquivo principal).
*   **Finalização:** Salva o arquivo principal (`ONI_HARVEST_TARGET.psd`) silenciando diálogos (`DialogModes.NO`).

---

## 💻 CÓDIGO FONTE (REFERÊNCIA)

### Extrator de Elementos (`oni_element_harvester.jsx`)
```javascript
// ... (Código para duplicar activeLayer para novo Doc)
targetLayer.duplicate(targetDoc, ElementPlacement.PLACEATBEGINNING);
```

### Substituidor de Texto (`oni_smart_text_replacer.jsx`)
```javascript
// ... (Recursão para achar LayerKind.TEXT com maior bounds)
targetLayer.textItem.contents = "NOVO TEXTO";
```

### Orquestrador Python (`demo_full_gold_oni.py`)
```python
bridge.smart_objects.edit_contents()
# ... wait ...
bridge.execute_jsx(REPLACER)
# ... close ...
```

---

## 📈 COMPARAÇÃO: EXTRAÇÃO vs TRANSPLANTE

| Característica | Extração (Style Transfer) | Transplante (Smart Ninja) |
| :--- | :--- | :--- |
| **Fidelidade** | 85-95% (Perde 3D complexo) | **100% (Pixel Perfect)** |
| **Complexidade** | Alta (JSON gigante) | **Baixa (Apenas cópia)** |
| **Flexibilidade** | Alta (Aplica em qualquer layer) | Média (Preserva forma original) |
| **Uso Ideal** | Estilos CSS, Botões, UI | **Texto 3D, Logos Premium, Mockups** |

---

## ✅ STATUS
Este protocolo foi validado com sucesso no teste `ONI_GOLD` (Ramadan Text Effect).
Caminho dos Scripts: `Modules/Photoshop/Tools/`
