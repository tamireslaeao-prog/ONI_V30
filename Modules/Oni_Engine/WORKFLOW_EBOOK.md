---
description: Workflow completo para criação de eBooks NPG a partir de SRT de aulas
---

# Workflow: Criação de eBook NPG (Padrão Neuropsiquiatria Geriátrica)

Este workflow documenta o processo completo de criação de eBooks no padrão NPG a partir de arquivos SRT de aulas.

## Pré-requisitos
- Arquivo SRT da aula (`temp/AULA X/aulaX.srt`)
- Pasta de imagens da aula (`temp/AULA X/imagens/`)
- Logo NPG (`logo.png`)
- Python com bibliotecas `markdown` e `weasyprint` instaladas

---

## Fase 1: Análise e Extração de Conteúdo

### 1.1. Leitura Completa do SRT
```powershell
# Visualizar o arquivo SRT completo
view_file "path/to/aulaX.srt"
```

**Objetivo:** Entender a estrutura da aula e identificar seções principais.

### 1.2. Identificação de Seções
Mapear as principais seções da aula (ex: Introdução, Epidemiologia, Fisiopatologia, Quadro Clínico, Diagnóstico, Tratamento, Conclusões).

---

## Fase 2: Criação do Conteúdo Estruturado

### 2.1. Dividir em 3 Partes (Recomendado)
Criar 3 arquivos markdown separados para facilitar a edição:

**Parte 1: Introdução + Conceitos Fundamentais**
- Definições
- Epidemiologia
- Fisiopatologia

**Parte 2: Apresentação Clínica**
- Quadro Clínico
- Formas de Apresentação
- Neuroimagem

**Parte 3: Diagnóstico e Tratamento**
- Critérios Diagnósticos
- Tratamento
- Mensagens Take-Home

### 2.2. Criar Diretório de Saída
```powershell
mkdir "temp/OUTPUT_AULAX"
```

### 2.3. Escrever as 3 Partes
Criar arquivos:
- `ebook_part1.md`
- `ebook_part2.md`
- `ebook_part3.md`

**Padrão de Escrita:**
- Baseado no SRT (verbatim quando possível)
- Markdown formatado (headers H1, H2, H3, H4)
- Blockquotes para citações importantes
- Tabelas para dados estruturados
- Listas para enumerações

---

## Fase 3: Incorporação de Imagens

### 3.1. Listar Imagens Disponíveis
```powershell
list_dir "temp/AULA X/imagens/Aula X - [Nome]"
```

### 3.2. Copiar Imagens para OUTPUT
Copie as imagens para a pasta de saída local.

### 3.3. Copiar Logo
Copie o logo NPG para a pasta de saída.

### 3.4. Inserir Referências de Imagem no Markdown
Adicionar tags de imagem nos locais apropriados:

```markdown
![Descrição da Imagem](nome_da_imagem.png)
```

**Estratégia de Distribuição:**
- Introdução: 1-2 imagens (definição, conceitos)
- Epidemiologia: 1-2 imagens (dados, gráficos)
- Fisiopatologia: 2-3 imagens (mecanismos, cascata)
- Quadro Clínico: 2-3 imagens (apresentações, critérios)
- Neuroimagem: 3-4 imagens (sequências de RM, escalas)
- Diagnóstico: 1-2 imagens (critérios, algoritmos)
- Tratamento: 1-2 imagens (estudos, guidelines)

---

## Fase 4: Junção e Unificação

### 4.1. Mesclar as 3 Partes em um Arquivo Único
Use python para ler os 3 arquivos e unificar em `ebook_structured.md`.

### 4.2. Verificar Encoding
Confirmar que o arquivo final está em UTF-8 correto (sem caracteres estranhos).

### 4.3. Remover Marcadores de Edição
Remover qualquer texto como "FIM DA PARTE X" ou marcadores temporários.

---

## Fase 5: Geração do PDF

### 5.1. Criar Script de Geração (`generate_aulaX.py`)
Utilize o módulo `oni_video_gen.py` ou `ebook_generator.py` do Oni_Engine para automatizar a conversão MD->HTML->PDF usando WeasyPrint.

### 5.2. Executar Script de Geração
```powershell
python "app/scripts/generate_aulaX.py"
```

---

## Fase 6: Revisão e Correção

### 6.1. Verificar PDF Gerado
- [ ] Logo NPG visível no topo
- [ ] Título e subtítulo corretos
- [ ] Todas as imagens aparecem
- [ ] Caracteres UTF-8 corretos (ã, ç, ó, etc.)
- [ ] Paginação automática funcionando
- [ ] Sem marcadores de edição visíveis

---

## Checklist Final

- [ ] SRT lido completamente
- [ ] 3 partes criadas com conteúdo verbatim
- [ ] Imagens identificadas e copiadas
- [ ] Referências de imagem inseridas no markdown
- [ ] Logo copiado para OUTPUT
- [ ] Partes mescladas com encoding UTF-8
- [ ] Marcadores de edição removidos
- [ ] Script de geração criado e testado
- [ ] PDF gerado com sucesso
- [ ] PDF revisado e aprovado

---

## Arquivos Finais Gerados

```
temp/OUTPUT_AULAX/
├── ebook_part1.md          # Parte 1 (separada)
├── ebook_part2.md          # Parte 2 (separada)
├── ebook_part3.md          # Parte 3 (separada)
├── ebook_structured.md     # Todas as partes unificadas
├── ebook.html              # HTML intermediário
├── logo.png                # Logo NPG
├── [Imagem1].png           # Imagens da aula
├── [Imagem2].png
├── ...
└── AulaX_[Nome].pdf        # PDF FINAL
```

---

**Workflow criado e validado em:** Aula 6 - Comprometimento Cognitivo Vascular (13/01/2026)
