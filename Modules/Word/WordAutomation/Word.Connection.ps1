# ============================================================================
# Word.Connection.ps1
# Word COM connection management functions
# ============================================================================

function Connect-Word {
    <#
    .SYNOPSIS
    Establishes COM connection to Microsoft Word
    
    .EXAMPLE
    $word = Connect-Word
    #>
    
    try {
        # Try to connect to existing instance
        $word = [Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application")
        Write-Host "[OK] Connected to existing Word instance" -ForegroundColor Green
    }
    catch {
        # Create new instance
        try {
            $word = New-Object -ComObject Word.Application
            $word.Visible = $true
            Write-Host "[OK] Created new Word instance" -ForegroundColor Green
        }
        catch {
            Write-Error "Failed to connect to Word. Ensure Microsoft Word is installed."
            return $null
        }
    }
    
    return $word
}

function Disconnect-Word {
    <#
    .SYNOPSIS
    Releases COM connection and optionally closes Word
    #>
    param(
        $Word,
        [switch]$Close
    )
    
    if ($Word) {
        if ($Close) {
            $Word.Quit()
            Write-Host "[OK] Word closed" -ForegroundColor Green
        }
        
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($Word) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        Write-Host "[OK] Disconnected from Word" -ForegroundColor Green
    }
}

Export-ModuleMember -Function Connect-Word, Disconnect-Word
