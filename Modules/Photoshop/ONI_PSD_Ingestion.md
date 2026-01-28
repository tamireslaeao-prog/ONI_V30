# 🏭 ONI ASSET MACHINE: MANUAL DE OPERAÇÃO

> **STATUS:** CRÍTICO
> **DIRETIVA:** `DO NOT DELETE SOURCE PSDs`

## 1. A Importância dos Arquivos Fonte (Source PSDs)
Você perguntou se "memorizei" o estilo e se pode deletar o arquivo original (`ORANGEV2.psd`).
**A RESPOSTA É NÃO! NÃO DELETE! 🛑**

### Por quê?
O `ORANGEV2.psd` não é apenas um "Estilo de Camada" (que são apenas números de sombra/brilho). Ele é uma **COMPOSIÇÃO** complexa (Engine) que contém:
*   💡 **Grupos de Iluminação Global** (Lights)
*   🧱 **Texturas de Alta Resolução** (Overlays, Grunge)
*   🏗️ **Smart Objects Aninhados** (A mágica da substituição)
*   🎨 **Backgrounds Renderizados**

Se você deletar o arquivo, eu perco a "fôrma do bolo". Eu tenho a receita (JSON), mas sem a fôrma (PSD), o bolo sai torto. **O PSD é a Engine.**

---

## 2. Como Adicionar Mais "Poder" (Novos PSDs)
Sim! Se você me der mais PSDs desse nível, eu consigo usar TODOS eles.

### O Protocolo de Ingestão:
1.  **Coloque o PSD em:** `C:\Users\user\Desktop\ONI V24\data\psd_sources\`
2.  **Regra de Ouro:** O PSD deve ter um **Smart Object** editável onde fica o texto/logo.
3.  **Me avise:** "ONI, adicionei o arquivo `GLOW_NEON_X.psd` na pasta."

Eu vou:
1.  Analisar a estrutura (scan).
2.  Identificar o Smart Object alvo.
3.  Criar o script de injeção para ele.

### Exemplo de Uso Futuro:
Para gerar um logo novo com estilo novo:
```text
"ONI, gere o logo 'CYBER' usando o template 'GLOW_NEON_X'"
```
Eu abro o `GLOW_NEON_X`, injeto "CYBER", e te entrego o Masterpiece pronto.

---

## 3. Resumo Técnico
*   **JSON (.json):** É apenas o mapa/índice. Leve.
*   **PSD Fonte (.psd):** É a fábrica. Pesado. **Mantenha-o.**
*   **ASL (Styles):** Posso extrair estilos simples, mas perde-se a iluminação e background.

**MANTENHA OS PSDs NA PASTA `psd_sources`. ELES SÃO SUA MUNIÇÃO.**
