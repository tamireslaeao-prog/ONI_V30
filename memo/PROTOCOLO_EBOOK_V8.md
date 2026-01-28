# 📘 PROTOCOLO DE GERAÇÃO DE EBOOKS ACADÊMICOS (PADRÃO V8)

> **Versão:** 1.0
> **Data:** 21/01/2026
> **Status:** ✅ VALIDADO (Aulas 1-10)
> **Objetivo:** Transformar aulas em vídeo (SRT + Slides) em eBooks PDFs profissionais, acadêmicos e padronizados.

---

## 1. 🛠️ REQUISITOS E FERRAMENTAS

### Arquivos Necessários (Inputs)
1.  **Arquivo de Legenda Original (`.srt`)**: Contém a transcrição "crua" da aula.
2.  **Imagens dos Slides**: Pasta contendo os prints/slides da aula (PNG/JPG).
3.  **Logo**: Arquivo `logo.png` (Padrão V8).

### Scripts do Sistema
*   **`replicate_tone_correction.py`**: O "motor" de geração. Contém o CSS V8, configurações do `WeasyPrint` e lógica de numeração de páginas.
    *   *Localização:* `desktop/ONIV25/temp/replicate_tone_correction.py`

---

## 2. 📋 FLUXO DE TRABALHO (STEP-BY-STEP)

### FASE 1: Preparação do Ambiente
1.  Crie uma pasta de saída: `OUTPUT_AULA[X]` (ex: `OUTPUT_AULA11`).
2.  Dentro dela, crie uma subpasta `images`.
3.  Copie todas as imagens relevantes da aula para `OUTPUT_AULA[X]/images`.
4.  Copie o arquivo `logo.png` para a raiz de `OUTPUT_AULA[X]`.

### FASE 2: Engenharia de Texto (O "Coração" do Processo)
Crie um arquivo chamado `ebook_structured.md`. O conteúdo deve ser criado a partir do SRT, mas **drasticamente transformado**:

1.  **Limpeza Pesada:**
    *   Remover todos os timestamps.
    *   Remover vícios de linguagem ("né", "então", "a gente").
    *   **Corrigir alucinações auditivas:** Atenção crítica a termos médicos (ex: *mioclonias* não *1000 colonias*, *Creutzfeldt-Jakob* não *Crohn*).

2.  **Estruturação Acadêmica (Markdown):**
    *   **Título (H1):** `# Nome da Aula`
    *   **Subtítulo (H2):** `## Tema Específico`
    *   **Divisores:** Use `---` para quebras de seção.
    *   **Capítulos:** Organize o fluxo em `# CAPÍTULO 1: ...`, `# CAPÍTULO 2: ...`.
    *   **Subseções:** Use `## 1.1. ...`, `## 1.2. ...`.

3.  **Elementos Visuais V8:**
    *   **Citações/Definições:** Use `> Texto` para criar caixas de destaque cinza.
    *   **Listas:** Use balas (`-`) ou números para enumerar itens.
    *   **Negrito:** Use `**termo**` para conceitos-chave.
    *   **Tabelas:** Crie tabelas Markdown para dados comparativos.

4.  **Inserção de Imagens:**
    *   Sintaxe: `![Legenda Descritiva](images/arquivo_do_slide.png)`
    *   *Dica:* Insira a imagem logo após o tópico que ela ilustra.

### FASE 3: Geração do PDF
1.  Abra o script `replicate_tone_correction.py`.
2.  Verifique/Ajuste o loop `for i in range(...)` para incluir o número da nova aula.
    *   *Exemplo:* `for i in range(11, 12):` (para processar apenas a Aula 11).
3.  Execute o script:
    ```powershell
    python replicate_tone_correction.py
    ```
4.  O script irá:
    *   Ler `ebook_structured.md`.
    *   Aplicar o CSS V8 (Fontes Segoe UI, Cabeçalhos Azuis, Rodapés, Justificação).
    *   Gerar o PDF na pasta.

### FASE 4: Controle de Qualidade (Checklist V8)
Abra o PDF gerado e verifique:
- [ ] **Capa/Título:** H1 azul com borda inferior?
- [ ] **Imagens:** Estão renderizadas e não quebradas?
- [ ] **Layout:** O texto está justificado?
- [ ] **Terminologia:** Erros "bizarros" de transcrição foram removidos?
- [ ] **Logo:** Aparece no cabeçalho/topo?
- [ ] **Tamanho:** O arquivo tem um tamanho razoável (1-10MB)?

### FASE 5: Deploy
1.  Mova o PDF aprovado para a pasta final: `MOD 01 V1`.
2.  Nomeie seguindo o padrão: `Aula[X]_[Nome_Descritivo]_V8_FINAL.pdf`.

---

## 3. 🎨 GUIA DE ESTILO (V8 CSS)

O estilo visual é definido hardcoded no script Python. Se precisar alterar:
*   **H1:** Azul Escuro (`#0d47a1`), 22pt, Borda inferior grossa.
*   **H2:** Azul Médio (`#1565c0`), 16pt, Borda fina.
*   **Blockquote:** Fundo cinza claro (`#f5f5f5`), Borda lateral azul (`#2196f3`), Itálico.
*   **Corpo:** Fonte Segoe UI/Arial, 11pt, Justificado, Leading 1.5.

---

## 4. HISTÓRICO DE PRODUÇÃO
*   **Aulas 1-7:** Processadas em lote (Batch).
*   **Aula 8:** Recriada do zero (Correção severa de SRT).
*   **Aula 9:** Criada do zero (HAND/Sífilis).
*   **Aula 10:** Criada do zero (Delirium).
