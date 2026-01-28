# ============================================================================
# ONI.Gen.ps1 - ONI Generative Core
# Version: 1.0
# Description: Core functions for randomness and seeding
# ============================================================================

function New-ONISeed {
    <#
    .SYNOPSIS
    Generates a new ONI seed
    #>
    param(
        [string]$StylePrefix = "GEN"
    )

    $timestamp = Get-Date -Format "yyyyMMdd"
    $random = Get-Random
    
    # Create rudimentary hash
    $base = "$timestamp$random"
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $hash = [BitConverter]::ToString($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($base)))
    $hash = $hash.Replace("-", "").Substring(0, 4)
    
    return "ONI-$StylePrefix-$timestamp-$hash"
}

function Get-RandomChoice {
    <#
    .SYNOPSIS
    Selects a random item from a list
    #>
    param(
        [Parameter(Mandatory = $true)]
        $Items
    )
    
    if ($Items -is [System.Collections.IEnumerable]) {
        return $Items | Get-Random
    }
    return $Items
}

Export-ModuleMember -Function New-ONISeed, Get-RandomChoice

Write-Host "ONI.Gen module loaded" -ForegroundColor Green
