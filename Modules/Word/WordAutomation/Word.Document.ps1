# ============================================================================
# Word.Document.ps1
# Document operations (New, Open, Save)
# ============================================================================

function New-WordDocument {
    <#
    .SYNOPSIS
    Creates new Word document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [string]$Template = "",
        [switch]$Visible = $true
    )
    
    $doc = $Word.Documents.Add($Template)
    $Word.Visible = $Visible
    
    Write-Host "[OK] Document created" -ForegroundColor Green
    
    return $doc
}

function Open-WordDocument {
    <#
    .SYNOPSIS
    Opens existing Word document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Word,
        
        [Parameter(Mandatory = $true)]
        [string]$Path
    )
    
    if (-not (Test-Path $Path)) {
        Write-Error "Document not found: $Path"
        return $null
    }
    
    $doc = $Word.Documents.Open($Path)
    Write-Host "[OK] Document opened: $Path" -ForegroundColor Green
    
    return $doc
}

function Save-WordDocument {
    <#
    .SYNOPSIS
    Saves Word document
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [string]$Path,
        [string]$Format = "docx"
    )
    
    $formats = @{
        "docx" = 16
        "pdf"  = 17
        "html" = 8
        "txt"  = 2
        "rtf"  = 6
    }
    
    if ($Path) {
        $formatCode = $formats[$Format.ToLower()]
        if ($formatCode) {
            $Document.SaveAs([ref]$Path, [ref]$formatCode)
        }
        else {
            $Document.SaveAs([ref]$Path)
        }
        Write-Host "[OK] Document saved: $Path" -ForegroundColor Green
    }
    else {
        $Document.Save()
        Write-Host "[OK] Document saved" -ForegroundColor Green
    }
}

Export-ModuleMember -Function New-WordDocument, Open-WordDocument, Save-WordDocument
