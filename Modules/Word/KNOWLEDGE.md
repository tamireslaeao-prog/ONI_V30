---
description: Word automation for report generation and document processing
---

# 📄 ONI WORD KNOWLEDGE BASE

> **Nível:** Avançado  
> **Tecnologia:** COM Automation (PowerShell + VBA)  
> **Versão:** 1.0.0  
> **Última Atualização:** 2026-01-17

---

## 🎯 VISÃO GERAL

Este perfil documenta automação completa do Microsoft Word via COM, focando em geração de relatórios, processamento de documentos, e conversão de formatos.

### Capabilities

- ✅ **COM Automation:** PowerShell drives `Word.Application`
- ✅ **Template System:** .dotx templates + data merge
- ✅ **Markdown → Word:** Convert .md to formatted .docx
- ✅ **Metadata Extraction:** Extract data from existing .docx
- ✅ **Mail Merge:** Batch document generation
- ✅ **PDF Export:** Professional document output

---

## 🔌 CONEXÃO COM WORD

### Criar Instância

```powershell
# Criar instância do Word
$word = New-Object -ComObject Word.Application

# Tornar visível (opcional - para debug)
$word.Visible = $true

# Criar novo documento
$doc = $word.Documents.Add()

# Ou usar template
$doc = $word.Documents.Add("C:\templates\relatorio.dotx")

# Ou abrir existente
$doc = $word.Documents.Open("C:\path\to\file.docx")
```

---

## ✏️ MANIPULAÇÃO DE CONTEÚDO

### Inserir Texto

```powershell
# Usar Selection (cursor)
$selection = $word.Selection
$selection.TypeText("Hello World")
$selection.TypeParagraph()  # Nova linha

# Inserir no final
$doc.Content.InsertAfter("Texto no final")

# Inserir em posição específica
$range = $doc.Range(0, 0)  # Início do documento
$range.InsertBefore("Texto no início")
```

### Estilos e Formatação

```powershell
# Aplicar estilo de parágrafo
$selection.Style = "Heading 1"

# Negrito, Itálico, Sublinhado
$selection.Font.Bold = $true
$selection.Font.Italic = $true
$selection.Font.Underline = 1  # wdUnderlineSingle

# Tamanho e cor
$selection.Font.Size = 14
$selection.Font.Color = 255  # Vermelho

# Centralizar
$selection.ParagraphFormat.Alignment = 1  # wdAlignParagraphCenter
```

### Listas

```powershell
# Lista com marcadores
$selection.Range.ListFormat.ApplyBulletDefault()

# Lista numerada
$selection.Range.ListFormat.ApplyNumberDefault()

# Customizar
$selection.Range.ListFormat.ApplyListTemplate($word.ListGalleries.Item(1).ListTemplates.Item(1))
```

---

## 📑 TRABALHANDO COM BOOKMARKS

### Criar e Usar Bookmarks

```powershell
# Criar bookmark
$range = $selection.Range
$doc.Bookmarks.Add("NomeCliente", $range)

# Substituir conteúdo de bookmark
if ($doc.Bookmarks.Exists("NomeCliente")) {
    $bookmark = $doc.Bookmarks.Item("NomeCliente")
    $bookmark.Range.Text = "João da Silva"
}

# Loop por todos os bookmarks
foreach ($bm in $doc.Bookmarks) {
    Write-Host "Bookmark: $($bm.Name)"
}
```

---

## 🖼️ INSERIR ELEMENTOS

### Imagens

```powershell
# Inserir imagem
$range = $selection.Range
$shape = $doc.InlineShapes.AddPicture("C:\images\logo.png", $false, $true, $range)

# Redimensionar
$shape.Width = 200
$shape.Height = 100

# Ou manter proporção
$shape.LockAspectRatio = -1  # TRUE
$shape.Width = 300
```

### Tabelas

```powershell
# Criar tabela (3 linhas x 4 colunas)
$range = $selection.Range
$table = $doc.Tables.Add($range, 3, 4)

# Preencher células
$table.Cell(1, 1).Range.Text = "Header 1"
$table.Cell(1, 2).Range.Text = "Header 2"

# Formatar header
$table.Rows.Item(1).Range.Font.Bold = $true
$table.Rows.Item(1).Range.Shading.BackgroundPatternColor = 15773696  # Azul claro

# Bordas
$table.Borders.Enable = $true

# AutoFit
$table.AutoFitBehavior(2)  # wdAutoFitContent
```

### Seções e Quebras

```powershell
# Quebra de página
$selection.InsertBreak(7)  # wdPageBreak

# Quebra de seção
$selection.InsertBreak(2)  # wdSectionBreakNextPage

# Orientação de página
$doc.Sections.Item(1).PageSetup.Orientation = 1  # wdOrientLandscape
```

---

## 🔄 BUSCAR E SUBSTITUIR

### Find & Replace

```powershell
# Buscar e substituir texto
$findText = "[NOME]"
$replaceText = "João da Silva"

$find = $selection.Find
$find.Text = $findText
$find.Replacement.Text = $replaceText
$find.Execute($null, $null, $null, $null, $null, $null, $true, 1, $true, $null, 2)
# Parâmetros: Forward=True, Wrap=wdFindContinue, Replace=wdReplaceAll

# Buscar e substituir em todo documento
$doc.Content.Find.Execute($findText, $false, $true, $false, $false, $false, $true, 1, $false, $replaceText, 2)
```

---

## 📄 TEMPLATES E MAIL MERGE

### Usar Template

```powershell
# Abrir template
$doc = $word.Documents.Add("C:\templates\carta.dotx")

# Substituir placeholders
$placeholders = @{
    "[NOME]" = "João da Silva"
    "[EMAIL]" = "joao@example.com"
    "[DATA]" = (Get-Date -Format "dd/MM/yyyy")
}

foreach ($placeholder in $placeholders.Keys) {
    $doc.Content.Find.Execute($placeholder, $false, $true, $false, $false, $false, $true, 1, $false, $placeholders[$placeholder], 2)
}

# Salvar como novo documento
$doc.SaveAs("C:\output\carta_joao.docx")
```

### Mail Merge Simples

```powershell
# Dados (normalmente de Excel ou CSV)
$clientes = @(
    @{Nome="João"; Email="joao@example.com"},
    @{Nome="Maria"; Email="maria@example.com"}
)

# Template
$template = "C:\templates\carta.dotx"

foreach ($cliente in $clientes) {
    $doc = $word.Documents.Add($template)
    
    # Substituir bookmarks
    if ($doc.Bookmarks.Exists("Nome")) {
        $doc.Bookmarks.Item("Nome").Range.Text = $cliente.Nome
    }
    if ($doc.Bookmarks.Exists("Email")) {
        $doc.Bookmarks.Item("Email").Range.Text = $cliente.Email
    }
    
    # Salvar
    $outputPath = "C:\output\carta_$($cliente.Nome).docx"
    $doc.SaveAs($outputPath)
    $doc.Close()
}

Write-Host "[OK] $($clientes.Count) cartas geradas!" -ForegroundColor Green
```

---

## 📥📤 CONVERSÃO DE FORMATOS

### Markdown → Word

```powershell
# Ler Markdown
$markdown = Get-Content "C:\docs\relatorio.md" -Raw

# Processar (simplificado)
$lines = $markdown -split "`n"

$doc = $word.Documents.Add()
$selection = $word.Selection

foreach ($line in $lines) {
    if ($line -match "^# (.+)$") {
        # Heading 1
        $selection.TypeText($matches[1])
        $selection.Style = "Heading 1"
        $selection.TypeParagraph()
    }
    elseif ($line -match "^## (.+)$") {
        # Heading 2
        $selection.TypeText($matches[1])
        $selection.Style = "Heading 2"
        $selection.TypeParagraph()
    }
    elseif ($line -match "^\*\*(.+?)\*\*") {
        # Bold
        $text = $line -replace "\*\*(.+?)\*\*", '$1'
        $selection.TypeText($text)
        $selection.Font.Bold = $true
        $selection.TypeParagraph()
    }
    else {
        # Texto normal
        if ($line.Trim() -ne "") {
            $selection.TypeText($line)
            $selection.TypeParagraph()
        }
    }
}

$doc.SaveAs("C:\output\relatorio.docx")
```

### Word → PDF

```powershell
# Exportar como PDF
$doc.ExportAsFixedFormat("C:\output\relatorio.pdf", 17)  # wdExportFormatPDF = 17

# Ou usando SaveAs com formato PDF
$doc.SaveAs("C:\output\relatorio.pdf", 17)
```

---

## 🔍 EXTRAÇÃO DE METADADOS

### Ler Propriedades

```powershell
# Abrir documento
$doc = $word.Documents.Open("C:\docs\relatorio.docx")

# Propriedades built-in
$title = $doc.BuiltInDocumentProperties.Item("Title").Value
$author = $doc.BuiltInDocumentProperties.Item("Author").Value
$created = $doc.BuiltInDocumentProperties.Item("Creation Date").Value

Write-Host "Título: $title"
Write-Host "Autor: $author"
Write-Host "Criado em: $created"

# Contar palavras
$wordCount = $doc.ComputeStatistics(0)  # wdStatisticWords
Write-Host "Palavras: $wordCount"

$doc.Close($false)
```

### Extrair Todo Texto

```powershell
$doc = $word.Documents.Open("C:\docs\relatorio.docx")

# Texto completo
$text = $doc.Content.Text

# Salvar como TXT
$text | Out-File "C:\output\relatorio.txt" -Encoding UTF8

$doc.Close($false)
```

---

## 🔄 WORKFLOWS COMPLETOS

### 1. Gerar Relatório de Auditoria

```powershell
# Criar documento
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add("C:\templates\relatorio_auditoria.dotx")

# Dados da auditoria
$data = @{
    Titulo = "Auditoria ONIV24"
    Data = Get-Date -Format "dd/MM/yyyy HH:mm"
    Executor = $env:USERNAME
    TotalArquivos = 1562
    TamanhoTotal = "12.2 GB"
}

# Substituir bookmarks
foreach ($key in $data.Keys) {
    if ($doc.Bookmarks.Exists($key)) {
        $doc.Bookmarks.Item($key).Range.Text = $data[$key]
    }
}

# Adicionar tabela de resultados
$selection = $word.Selection
$selection.EndKey(6)  # Ir para o final (wdStory)

$selection.TypeParagraph()
$selection.TypeText("Resultados:")
$selection.Style = "Heading 2"
$selection.TypeParagraph()

# Criar tabela
$table = $doc.Tables.Add($selection.Range, 4, 3)
$table.Cell(1, 1).Range.Text = "Categoria"
$table.Cell(1, 2).Range.Text = "Quantidade"
$table.Cell(1, 3).Range.Text = "Status"

$table.Cell(2, 1).Range.Text = "PSDs"
$table.Cell(2, 2).Range.Text = "505"
$table.Cell(2, 3).Range.Text = "✓ OK"

# Formatar
$table.Rows.Item(1).Range.Font.Bold = $true
$table.AutoFitBehavior(2)

# Salvar
$doc.SaveAs("C:\output\relatorio_auditoria.docx")
$doc.ExportAsFixedFormat("C:\output\relatorio_auditoria.pdf", 17)

$doc.Close()
$word.Quit()

[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
[System.GC]::Collect()

Write-Host "[OK] Relatório gerado!" -ForegroundColor Green
```

### 2. Batch Converter Markdown → Word

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false

Get-ChildItem "C:\docs\*.md" | ForEach-Object {
    $markdown = Get-Content $_.FullName -Raw
    $doc = $word.Documents.Add()
    
    # Processar markdown (simplificado)
    $selection = $word.Selection
    $lines = $markdown -split "`n"
    
    foreach ($line in $lines) {
        if ($line -match "^# (.+)$") {
            $selection.TypeText($matches[1])
            $selection.Style = "Heading 1"
            $selection.TypeParagraph()
        }
        elseif ($line.Trim() -ne "") {
            $selection.TypeText($line)
            $selection.TypeParagraph()
        }
    }
    
    # Salvar
    $outputPath = $_.FullName -replace "\.md$", ".docx"
    $doc.SaveAs($outputPath)
    $doc.Close()
    
    Write-Host "[OK] Convertido: $($_.Name)" -ForegroundColor Green
}

$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null

Write-Host "[COMPLETO] Conversão finalizada!" -ForegroundColor Cyan
```

---

## 🧪 DEBUGGING

### Error Handling

```powershell
try {
    $word = New-Object -ComObject Word.Application
    $doc = $word.Documents.Open("C:\docs\relatorio.docx")
    
    # Processar...
    
} catch {
    Write-Host "[ERRO] $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Sempre limpar
    if ($doc) { $doc.Close($false) }
    if ($word) { $word.Quit() }
    [System.GC]::Collect()
}
```

---

## 📚 REFERÊNCIAS RÁPIDAS

### Constantes Úteis

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `wdAlignParagraphCenter` | 1 | Centralizar |
| `wdAlignParagraphLeft` | 0 | Alinhar esquerda |
| `wdAlignParagraphRight` | 2 | Alinhar direita |
| `wdPageBreak` | 7 | Quebra de página |
| `wdSectionBreakNextPage` | 2 | Quebra de seção |
| `wdExportFormatPDF` | 17 | Formato PDF |
| `wdFormatDocumentDefault` | 16 | Formato .docx |
| `wdSaveChanges` | -1 | Salvar ao fechar |
| `wdDoNotSaveChanges` | 0 | Não salvar |

### Módulos ONI Relacionados

- `Modules/Word/ONI_Report_Generator.ps1` - Gerador de relatórios
- `Modules/Word/Markdown_to_Word.py` - Conversor MD → DOCX
- `Modules/Word/Templates/` - Templates .dotx
- `Modules/Word/QuickStart.md` - Setup rápido

---

**Última Atualização:** 2026-01-17
**Autor:** ONI Team
**Versão:** 1.0.0
