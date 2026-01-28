---
description: Advanced Excel automation via COM (PowerShell + VBA)
---

# 📊 ONI EXCEL KNOWLEDGE BASE

> **Nível:** Avançado  
> **Tecnologia:** COM Automation (PowerShell + VBA)  
> **Versão:** 1.0.0  
> **Última Atualização:** 2026-01-17

---

## 🎯 VISÃO GERAL

Este perfil documenta todas as capabilities de automação do Excel dentro do ONIV24, utilizando COM (Component Object Model) via PowerShell e VBA para controle programático total.

### Capabilities

- ✅ **COM Automation:** PowerShell drives `Excel.Application`
- ✅ **VBA Macros:** Batch operations, formatting
- ✅ **Data Analysis:** Pivot tables, formulas, charts
- ✅ **Report Generation:** Templates + data injection
- ✅ **File Manipulation:** Open, edit, save, export
- ✅ **Cross-App Integration:** Excel ↔ Word/Photoshop/AutoCAD

---

## 🔌 CONEXÃO COM EXCEL

### Método 1: PowerShell COM

```powershell
# Criar instância do Excel
$excel = New-Object -ComObject Excel.Application

# Tornar visível (opcional - para debug)
$excel.Visible = $true

# Desabilitar alertas (evitar pop-ups)
$excel.DisplayAlerts = $false

# Criar novo workbook
$workbook = $excel.Workbooks.Add()

# Ou abrir existente
$workbook = $excel.Workbooks.Open("C:\path\to\file.xlsx")
```

### Método 2: VBA (via PowerShell)

```powershell
# Executar macro VBA de um arquivo existente
$workbook = $excel.Workbooks.Open("C:\path\to\macro.xlsm")
$excel.Run("NomeDaMacro")
```

---

## 📝 MANIPULAÇÃO DE DADOS

### Acessar Células

```powershell
# Selecionar worksheet
$sheet = $workbook.Worksheets.Item(1)

# Ou por nome
$sheet = $workbook.Worksheets.Item("Dados")

# Escrever em célula específica
$sheet.Cells.Item(1, 1) = "Header 1"
$sheet.Cells.Item(1, 2) = "Header 2"

# Ler célula
$valor = $sheet.Cells.Item(2, 1).Text

# Usar Range
$sheet.Range("A1").Value2 = "Hello"
$sheet.Range("B1:D1").Value2 = "World"
```

### Manipular Ranges

```powershell
# Selecionar range
$range = $sheet.Range("A1:D10")

# Copiar/Colar
$range.Copy()
$sheet.Range("F1").PasteSpecial()

# Limpar conteúdo
$range.Clear()

# Deletar range
$range.Delete()
```

### Fórmulas

```powershell
# Fórmula simples
$sheet.Range("C1").Formula = "=A1+B1"

# Fórmula com referências absolutas
$sheet.Range("D1").Formula = "=SUM($A$1:$B$10)"

# VLOOKUP
$sheet.Range("E1").Formula = "=VLOOKUP(A1,Sheet2!A:B,2,FALSE)"
```

---

## 🎨 FORMATAÇÃO

### Estilos de Célula

```powershell
# Negrito
$sheet.Range("A1:D1").Font.Bold = $true

# Cor de fonte
$sheet.Range("A1").Font.Color = 255  # Vermelho (RGB: 255,0,0)

# Cor de fundo
$sheet.Range("A1").Interior.Color = 65535  # Amarelo

# Tamanho da fonte
$sheet.Range("A1").Font.Size = 14

# Centralizar
$sheet.Range("A1").HorizontalAlignment = -4108  # xlCenter
```

### Bordas

```powershell
# Adicionar bordas
$range = $sheet.Range("A1:D10")
$range.Borders.LineStyle = 1  # xlContinuous
$range.Borders.Weight = 2     # xlThin
```

### Autofit

```powershell
# Ajustar largura das colunas
$sheet.Columns.Item("A:D").AutoFit()

# Ajustar altura das linhas
$sheet.Rows.Item("1:10").AutoFit()
```

---

## 📊 ANÁLISE DE DADOS

### Criar Pivot Table

```powershell
# Definir range de dados
$dataRange = $sheet.Range("A1:D100")

# Criar pivot cache
$pivotCache = $workbook.PivotCaches().Create(1, $dataRange)  # xlDatabase = 1

# Criar pivot table em novo sheet
$pivotSheet = $workbook.Worksheets.Add()
$pivotTable = $pivotCache.CreatePivotTable($pivotSheet.Range("A1"), "Vendas")

# Configurar campos
$pivotTable.PivotFields("Produto").Orientation = 1   # xlRowField
$pivotTable.PivotFields("Valor").Orientation = 4     # xlDataField
```

### Gráficos

```powershell
# Criar gráfico
$chart = $sheet.Shapes.AddChart().Chart

# Definir tipo (51 = xlColumnClustered)
$chart.ChartType = 51

# Definir range de dados
$chart.SetSourceData($sheet.Range("A1:B10"))

# Título
$chart.HasTitle = $true
$chart.ChartTitle.Text = "Vendas por Mês"
```

### Filtros e Ordenação

```powershell
# Aplicar AutoFilter
$sheet.Range("A1:D100").AutoFilter(1, "Produto A")  # Filtrar coluna 1

# Ordenar
$range = $sheet.Range("A1:D100")
$range.Sort($sheet.Range("A1"), 1)  # xlAscending = 1
```

---

## 💾 OPERAÇÕES DE ARQUIVO

### Salvar

```powershell
# Salvar como novo arquivo
$workbook.SaveAs("C:\output\relatorio.xlsx")

# Salvar modificações
$workbook.Save()

# Salvar como PDF
$workbook.ExportAsFixedFormat(0, "C:\output\relatorio.pdf")  # xlTypePDF = 0
```

### Fechar e Limpar

```powershell
# Fechar workbook (sem salvar)
$workbook.Close($false)

# Fechar Excel
$excel.Quit()

# Liberar objetos COM (IMPORTANTE!)
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($sheet) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
```

---

## 🔄 WORKFLOWS COMUNS

### 1. Gerar Relatório de Vendas

```powershell
# Conectar
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

# Abrir dados brutos
$workbook = $excel.Workbooks.Open("C:\dados\vendas_raw.xlsx")
$sheet = $workbook.Worksheets.Item(1)

# Processar dados
$lastRow = $sheet.UsedRange.Rows.Count
$sheet.Range("E2:E$lastRow").Formula = "=C2*D2"  # Total = Quantidade * Preço

# Formatar
$sheet.Range("A1:E1").Font.Bold = $true
$sheet.Range("A1:E1").Interior.Color = 15773696  # Azul claro
$sheet.Columns.Item("A:E").AutoFit()

# Criar gráfico
$chart = $sheet.Shapes.AddChart().Chart
$chart.ChartType = 51
$chart.SetSourceData($sheet.Range("A1:B$lastRow"))

# Salvar
$workbook.SaveAs("C:\output\relatorio_vendas.xlsx")
$workbook.Close($false)
$excel.Quit()

# Limpar
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
[System.GC]::Collect()

Write-Host "[OK] Relatório gerado!" -ForegroundColor Green
```

### 2. Importar CSV e Formatar

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $true

# Importar CSV
$workbook = $excel.Workbooks.Open("C:\dados\dados.csv")
$sheet = $workbook.Worksheets.Item(1)

# Converter para XLSX
$sheet.Columns.Item("A:Z").AutoFit()
$sheet.Range("A1:Z1").Font.Bold = $true

# Salvar como XLSX
$workbook.SaveAs("C:\output\dados.xlsx", 51)  # xlOpenXMLWorkbook = 51
$workbook.Close($false)
$excel.Quit()

[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
```

### 3. Mesclar Múltiplos Arquivos

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.DisplayAlerts = $false

# Criar workbook mestre
$master = $excel.Workbooks.Add()
$masterSheet = $master.Worksheets.Item(1)

$row = 1

# Processar cada arquivo
Get-ChildItem "C:\dados\*.xlsx" | ForEach-Object {
    $workbook = $excel.Workbooks.Open($_.FullName)
    $sheet = $workbook.Worksheets.Item(1)
    
    # Copiar dados
    $usedRange = $sheet.UsedRange
    $usedRange.Copy()
    $masterSheet.Range("A$row").PasteSpecial()
    
    $row += $usedRange.Rows.Count
    
    $workbook.Close($false)
}

# Salvar consolidado
$master.SaveAs("C:\output\consolidado.xlsx")
$master.Close($false)
$excel.Quit()

[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
Write-Host "[OK] Arquivos mesclados!" -ForegroundColor Green
```

---

## 🔗 INTEGRAÇÃO COM OUTROS APPS

### Excel → Word (Mail Merge)

```powershell
# Dados do Excel
$excel = New-Object -ComObject Excel.Application
$workbook = $excel.Workbooks.Open("C:\dados\clientes.xlsx")
$sheet = $workbook.Worksheets.Item(1)

# Processar para Word
$word = New-Object -ComObject Word.Application
$doc = $word.Documents.Add("C:\templates\carta.dotx")

# Inserir dados
for ($i = 2; $i -le 10; $i++) {
    $nome = $sheet.Cells.Item($i, 1).Text
    $email = $sheet.Cells.Item($i, 2).Text
    
    # Substituir bookmarks
    $word.Selection.Find.Execute("[NOME]", $false, $false, $false, $false, $false, $true, 1, $false, $nome, 2)
}

$doc.SaveAs("C:\output\cartas.docx")
$doc.Close()
$word.Quit()

$workbook.Close($false)
$excel.Quit()
```

---

## 🧪 DEBUGGING E TROUBLESHOOTING

### Verificar se Excel está aberto

```powershell
try {
    $excel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application")
    Write-Host "[OK] Excel já está aberto" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Excel não está aberto, criando nova instância..." -ForegroundColor Yellow
    $excel = New-Object -ComObject Excel.Application
}
```

### Handling Errors

```powershell
try {
    $excel = New-Object -ComObject Excel.Application
    $workbook = $excel.Workbooks.Open("C:\arquivo.xlsx")
    
    # Processar...
    
} catch {
    Write-Host "[ERRO] $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Sempre limpar, mesmo com erro
    if ($workbook) { $workbook.Close($false) }
    if ($excel) { $excel.Quit() }
    [System.GC]::Collect()
}
```

---

## 📚 REFERÊNCIAS RÁPIDAS

### Constantes Úteis

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `xlAscending` | 1 | Ordem crescente |
| `xlDescending` | 2 | Ordem decrescente |
| `xlCenter` | -4108 | Centralizar |
| `xlLeft` | -4131 | Alinhar à esquerda |
| `xlRight` | -4152 | Alinhar à direita |
| `xlContinuous` | 1 | Linha contínua (bordas) |
| `xlOpenXMLWorkbook` | 51 | Formato .xlsx |
| `xlTypePDF` | 0 | Exportar como PDF |

### Módulos ONI Relacionados

- `Modules/Excel/ONI_Excel_Report.ps1` - Gerador de relatórios
- `Modules/Excel/Excel_Automation.vba` - Macros VBA
- `Modules/Excel/QuickStart.md` - Setup rápido

---

**Última Atualização:** 2026-01-17
**Autor:** ONI Team
**Versão:** 1.0.0
