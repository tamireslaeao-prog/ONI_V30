# ONI AutoCAD PGP Injector v1.0
# "The Hack" - Injects Agent-Specific Shortcuts for Total Control

param(
    [string]$PgpPath = "C:\Users\user\AppData\Roaming\Autodesk\AutoCAD 2021\R24.0\enu\Support\acad.pgp"
)

$ErrorActionPreference = "Stop"

# 1. Validation
if (-not (Test-Path $PgpPath)) {
    Write-Error "PGP File not found at: $PgpPath"
    exit 1
}

# 2. Backup
$BackupPath = "$PgpPath.bak_OHI_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $PgpPath $BackupPath -Force
Write-Host "Backup created: $BackupPath" -ForegroundColor Gray

# 3. Define The ONI Standard Keymap
# "Safe, Explicit, Unambiguous Control"
$OniKeys = @"

; -----------------------------------------------------------------------------
;  ONI AUTOMATION STANDARD (DO NOT EDIT MANUALLY)
;  Injected by ONI Agent for 'Total Control' Protocol.
; -----------------------------------------------------------------------------

; -- CORE --
ONI_S,      *QSAVE
ONI_O,      *OPEN
ONI_C,      *CLOSE
ONI_Q,      *QUIT
ONI_U,      *UNDO
ONI_R,      *REDO

; -- VIEW --
ONI_Z,      *ZOOM
ONI_ZE,     *ZOOM EXTENTS
ONI_P,      *PAN
ONI_RG,     *REGENALL
ONI_TOP,    *PLAN
ONI_ISO,    *VPOINT 1,-1,1

; -- DRAW --
ONI_L,      *LINE
ONI_PL,     *PLINE
ONI_REC,    *RECTANG
ONI_CIR,    *CIRCLE
ONI_ARC,    *ARC
ONI_TXT,    *MTEXT
ONI_H,      *HATCH

; -- MODIFY --
ONI_M,      *MOVE
ONI_CP,     *COPY
ONI_RO,     *ROTATE
ONI_SC,     *SCALE
ONI_TR,     *TRIM
ONI_EX,     *EXTEND
ONI_OF,     *OFFSET
ONI_ER,     *ERASE
ONI_EX,     *EXPLODE
ONI_J,      *JOIN

; -- LAYERS --
ONI_LAY,    *LAYER
ONI_LI,     *LAYISO
ONI_LU,     *LAYUNISO
ONI_LF,     *LAYOFF
ONI_LON,    *LAYON

; -- CLEANUP --
ONI_PU,     *PURGE

; -----------------------------------------------------------------------------
"@

# 4. Injection
$CurrentContent = Get-Content $PgpPath -Raw
if ($CurrentContent -match "; ONI AUTOMATION STANDARD") {
    Write-Warning "ONI Keys already detected. Skipping Append."
}
else {
    Add-Content -Path $PgpPath -Value $OniKeys
    Write-Host "ONI Keys Injected Successfully." -ForegroundColor Green
}

# 5. Hot Reload (REINIT)
# Tries to connect to running AutoCAD to reload immediately
Import-Module "$PSScriptRoot/AutoCAD_Adapter.psm1" -Force -ErrorAction SilentlyContinue
try {
    $acad = Connect-AutoCAD
    if ($acad) {
        # REINIT bitcode 16 = Reload PGP
        Send-Command -ACAD $acad -Command "(command `"REINIT`" 16)"
        Write-Host "AutoCAD Config Reloaded (REINIT 16)." -ForegroundColor Cyan
    }
}
catch {
    Write-Warning "Could not reload usage in active AutoCAD. Restart required."
}
