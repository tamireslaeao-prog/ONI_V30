<#
.SYNOPSIS
    CorelDRAW Automation Adapter - ONI Protocol v2.0
    
.DESCRIPTION
    Módulo robusto para controle do CorelDRAW via teclado simulado.
    Suporta CorelDRAW 2024/2025/2026 com fallback inteligente.
    
.NOTES
    Author: ONI Team
    Version: 2.0
    Protocol: Keyboard-Only Control (Resilient)
    
.LINK
    https://github.com/oni-protocol
#>

#region Module Configuration

$script:CorelConfig = @{
    ProcessName   = 'CorelDRW'
    DefaultDelay  = 500
    RetryAttempts = 3
    WindowTitles  = @(
        'CorelDRAW 2026',
        'CorelDRAW 2025', 
        'CorelDRAW 2024',
        'CorelDRAW',
        'Sem título-1',
        'Sem título-2', 
        'Sem título-3',
        'Untitled-1',
        'Untitled-2'
    )
    SafetyDelays  = @{
        Short     = 100
        Medium    = 300
        Long      = 500
        ExtraLong = 1000
    }
}

$script:WShell = $null
$script:LastCommand = $null
$script:CommandHistory = @()

#endregion

#region Helper Functions

function Write-CorelLog {
    param(
        [string]$Message,
        [ValidateSet('Info', 'Success', 'Warning', 'Error', 'Debug', 'Command')]
        [string]$Level = 'Info',
        [switch]$NoNewline
    )
    
    $colors = @{
        'Info'    = 'Cyan'
        'Success' = 'Green'
        'Warning' = 'Yellow'
        'Error'   = 'Red'
        'Debug'   = 'Gray'
        'Command' = 'Magenta'
    }
    
    $prefix = switch ($Level) {
        'Info' { '[ONI-COREL]' }
        'Success' { '[✓ COREL]' }
        'Warning' { '[⚠ COREL]' }
        'Error' { '[✗ COREL]' }
        'Debug' { '[DBG-COREL]' }
        'Command' { '[→ COREL]' }
    }
    
    $params = @{
        Object          = "$prefix $Message"
        ForegroundColor = $colors[$Level]
    }
    
    if ($NoNewline) { $params['NoNewline'] = $true }
    
    Write-Host @params
}

function Get-CorelProcess {
    [CmdletBinding()]
    param([switch]$Silent)
    
    $process = Get-Process -Name $script:CorelConfig.ProcessName -ErrorAction SilentlyContinue
    
    if ($process) {
        if (-not $Silent) {
            Write-CorelLog "Processo encontrado: PID $($process.Id)" -Level Debug
        }
        return $process
    }
    
    if (-not $Silent) {
        Write-CorelLog "Processo '$($script:CorelConfig.ProcessName)' não encontrado" -Level Warning
    }
    
    return $null
}

function Initialize-WShell {
    if ($null -eq $script:WShell) {
        try {
            $script:WShell = New-Object -ComObject WScript.Shell
            Write-CorelLog "WScript.Shell inicializado" -Level Debug
        }
        catch {
            Write-CorelLog "Falha ao criar WScript.Shell: $_" -Level Error
            throw
        }
    }
    return $script:WShell
}

function Test-WindowActivation {
    param([string]$Title)
    
    $shell = Initialize-WShell
    
    try {
        $result = $shell.AppActivate($Title)
        if ($result) {
            Write-CorelLog "Janela ativada: '$Title'" -Level Debug
            return $true
        }
    }
    catch {
        Write-CorelLog "Erro ao ativar '$Title': $_" -Level Debug
    }
    
    return $false
}

#endregion

#region Public Functions

function Connect-Corel {
    <#
    .SYNOPSIS
        Conecta e foca a janela do CorelDRAW.
        
    .DESCRIPTION
        Tenta localizar e ativar a janela do CorelDRAW usando múltiplas estratégias:
        1. Via título da janela do processo
        2. Via lista de títulos conhecidos
        3. Via nome do processo
        
    .PARAMETER Force
        Força reconexão mesmo se já conectado
        
    .PARAMETER Timeout
        Timeout em segundos (padrão: 30)
        
    .EXAMPLE
        Connect-Corel
        
    .EXAMPLE
        Connect-Corel -Force -Timeout 60
        
    .OUTPUTS
        Boolean indicando sucesso
    #>
    
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [switch]$Force,
        [int]$Timeout = 30
    )
    
    Write-CorelLog "Iniciando conexão com CorelDRAW..." -Level Info
    
    $shell = Initialize-WShell
    $startTime = Get-Date
    $connected = $false
    
    # Estratégia 1: Via processo
    Write-CorelLog "Estratégia 1: Buscando processo..." -Level Debug
    $process = Get-CorelProcess
    
    if ($process -and $process.MainWindowTitle) {
        $title = $process.MainWindowTitle
        Write-CorelLog "Título da janela: '$title'" -Level Debug
        
        if (Test-WindowActivation -Title $title) {
            $connected = $true
        }
    }
    
    # Estratégia 2: Títulos conhecidos
    if (-not $connected) {
        Write-CorelLog "Estratégia 2: Tentando títulos conhecidos..." -Level Debug
        
        foreach ($title in $script:CorelConfig.WindowTitles) {
            if ((Get-Date) - $startTime).TotalSeconds -gt $Timeout) {
            Write-CorelLog "Timeout atingido" -Level Warning
            break
        }
            
        if (Test-WindowActivation -Title $title) {
            $connected = $true
            break
        }
            
        Start-Sleep -Milliseconds 100
    }
}
    
# Estratégia 3: Fallback via nome do processo
if (-not $connected) {
    Write-CorelLog "Estratégia 3: Fallback via processo..." -Level Debug
        
    if (Test-WindowActivation -Title $script:CorelConfig.ProcessName) {
        $connected = $true
    }
}
    
# Resultado
if ($connected) {
    Write-CorelLog "Conectado com sucesso!" -Level Success
    Start-Sleep -Milliseconds $script:CorelConfig.SafetyDelays.Long
    return $true
}
else {
    Write-CorelLog "Falha na conexão. Verifique se o CorelDRAW está aberto." -Level Error
    return $false
}
}

function Clear-CorelState {
    <#
    .SYNOPSIS
        Limpa o estado atual do CorelDRAW.
        
    .DESCRIPTION
        Envia sequência de ESC para cancelar operações em andamento
        e retorna ao estado neutro (Pick Tool).
        
    .PARAMETER Deep
        Executa limpeza profunda (mais ESC's)
        
    .EXAMPLE
        Clear-CorelState
        
    .EXAMPLE
        Clear-CorelState -Deep
    #>
    
    [CmdletBinding()]
    param(
        [switch]$Deep
    )
    
    Write-CorelLog "Limpando estado do CorelDRAW..." -Level Info
    
    $shell = Initialize-WShell
    $escCount = if ($Deep) { 5 } else { 3 }
    
    for ($i = 1; $i -le $escCount; $i++) {
        $shell.SendKeys("{ESC}")
        Write-CorelLog "ESC enviado ($i/$escCount)" -Level Debug
        Start-Sleep -Milliseconds $script:CorelConfig.SafetyDelays.Medium
    }
    
    # Ativar Pick Tool (Ctrl+Space é comum no Corel)
    Write-CorelLog "Ativando Pick Tool..." -Level Debug
    $shell.SendKeys("^( )")  # Ctrl+Space
    Start-Sleep -Milliseconds $script:CorelConfig.SafetyDelays.Long
    
    Write-CorelLog "Estado limpo" -Level Success
}

function Send-CorelShortcut {
    <#
    .SYNOPSIS
        Envia atalho de teclado para o CorelDRAW.
        
    .DESCRIPTION
        Envia teclas de atalho com controle de timing e retry.
        
    .PARAMETER Keys
        Teclas a enviar (formato SendKeys: {F6}, ^c, etc)
        
    .PARAMETER Description
        Descrição do comando (para logging)
        
    .PARAMETER Delay
        Delay após envio em ms (padrão: 500)
        
    .PARAMETER Retry
        Número de tentativas em caso de falha
        
    .EXAMPLE
        Send-CorelShortcut -Keys "{F6}" -Description "Rectangle Tool"
        
    .EXAMPLE
        Send-CorelShortcut -Keys "^c" -Description "Copy" -Delay 300
        
    .OUTPUTS
        Boolean indicando sucesso
    #>
    
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Keys,
        
        [string]$Description,
        
        [int]$Delay = 500,
        
        [int]$Retry = 1
    )
    
    $shell = Initialize-WShell
    $desc = if ($Description) { $Description } else { $Keys }
    
    for ($attempt = 1; $attempt -le $Retry; $attempt++) {
        try {
            Write-CorelLog "Comando: $desc" -Level Command -NoNewline
            
            $shell.SendKeys($Keys)
            
            Write-Host " [✓]" -ForegroundColor Green
            
            # Adicionar ao histórico
            $script:CommandHistory += @{
                Timestamp   = Get-Date
                Type        = 'Shortcut'
                Keys        = $Keys
                Description = $desc
            }
            
            Start-Sleep -Milliseconds $Delay
            return $true
        }
        catch {
            Write-Host " [✗]" -ForegroundColor Red
            Write-CorelLog "Erro ao enviar '$desc' (tentativa $attempt/$Retry): $_" -Level Warning
            
            if ($attempt -lt $Retry) {
                Start-Sleep -Milliseconds 500
            }
        }
    }
    
    Write-CorelLog "Falha após $Retry tentativa(s)" -Level Error
    return $false
}

function Send-CorelInput {
    <#
    .SYNOPSIS
        Digita texto/valores em campos ativos do CorelDRAW.
        
    .DESCRIPTION
        Envia texto caractere por caractere com controle de timing.
        
    .PARAMETER Text
        Texto a digitar
        
    .PARAMETER Delay
        Delay após digitação em ms (padrão: 300)
        
    .PARAMETER Enter
        Pressiona Enter após digitar
        
    .PARAMETER Tab
        Pressiona Tab após digitar
        
    .PARAMETER CharDelay
        Delay entre caracteres em ms (0 = envio direto)
        
    .EXAMPLE
        Send-CorelInput -Text "100" -Enter
        
    .EXAMPLE
        Send-CorelInput -Text "Arial" -Tab -CharDelay 50
        
    .OUTPUTS
        Boolean indicando sucesso
    #>
    
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,
        
        [int]$Delay = 300,
        
        [switch]$Enter,
        
        [switch]$Tab,
        
        [int]$CharDelay = 0
    )
    
    $shell = Initialize-WShell
    
    try {
        Write-CorelLog "Input: '$Text'" -Level Command -NoNewline
        
        if ($CharDelay -gt 0) {
            # Envio caractere por caractere
            foreach ($char in $Text.ToCharArray()) {
                $shell.SendKeys($char)
                Start-Sleep -Milliseconds $CharDelay
            }
        }
        else {
            # Envio direto
            $shell.SendKeys($Text)
        }
        
        if ($Enter) {
            Start-Sleep -Milliseconds 100
            $shell.SendKeys("{ENTER}")
            Write-Host " [ENTER ✓]" -ForegroundColor Green
        }
        elseif ($Tab) {
            Start-Sleep -Milliseconds 100
            $shell.SendKeys("{TAB}")
            Write-Host " [TAB ✓]" -ForegroundColor Green
        }
        else {
            Write-Host " [✓]" -ForegroundColor Green
        }
        
        # Adicionar ao histórico
        $script:CommandHistory += @{
            Timestamp = Get-Date
            Type      = 'Input'
            Text      = $Text
            Enter     = $Enter.IsPresent
            Tab       = $Tab.IsPresent
        }
        
        Start-Sleep -Milliseconds $Delay
        return $true
    }
    catch {
        Write-Host " [✗]" -ForegroundColor Red
        Write-CorelLog "Erro ao enviar input: $_" -Level Error
        return $false
    }
}

function Invoke-CorelSequence {
    <#
    .SYNOPSIS
        Executa sequência de comandos com validação.
        
    .DESCRIPTION
        Permite executar múltiplos comandos em sequência com rollback automático.
        
    .PARAMETER Commands
        Array de hashtables com comandos
        
    .PARAMETER StopOnError
        Para execução ao primeiro erro
        
    .EXAMPLE
        $cmds = @(
            @{ Type='Shortcut'; Keys='{F6}'; Description='Rectangle Tool' },
            @{ Type='Input'; Text='100'; Enter=$true },
            @{ Type='Input'; Text='200'; Enter=$true }
        )
        Invoke-CorelSequence -Commands $cmds
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [hashtable[]]$Commands,
        
        [switch]$StopOnError
    )
    
    Write-CorelLog "Iniciando sequência de $($Commands.Count) comando(s)..." -Level Info
    
    $results = @()
    $errorCount = 0
    
    foreach ($cmd in $Commands) {
        $success = $false
        
        switch ($cmd.Type) {
            'Shortcut' {
                $params = @{
                    Keys = $cmd.Keys
                }
                if ($cmd.Description) { $params['Description'] = $cmd.Description }
                if ($cmd.Delay) { $params['Delay'] = $cmd.Delay }
                
                $success = Send-CorelShortcut @params
            }
            
            'Input' {
                $params = @{
                    Text = $cmd.Text
                }
                if ($cmd.Enter) { $params['Enter'] = $true }
                if ($cmd.Tab) { $params['Tab'] = $true }
                if ($cmd.Delay) { $params['Delay'] = $cmd.Delay }
                if ($cmd.CharDelay) { $params['CharDelay'] = $cmd.CharDelay }
                
                $success = Send-CorelInput @params
            }
            
            default {
                Write-CorelLog "Tipo de comando desconhecido: $($cmd.Type)" -Level Warning
            }
        }
        
        $results += $success
        
        if (-not $success) {
            $errorCount++
            
            if ($StopOnError) {
                Write-CorelLog "Erro detectado. Parando sequência." -Level Error
                break
            }
        }
    }
    
    Write-CorelLog "Sequência concluída: $($Commands.Count - $errorCount)/$($Commands.Count) sucesso(s)" -Level Info
    
    return $results
}

function Get-CorelCommandHistory {
    <#
    .SYNOPSIS
        Retorna histórico de comandos enviados.
        
    .PARAMETER Last
        Número de comandos recentes
        
    .EXAMPLE
        Get-CorelCommandHistory -Last 10
    #>
    
    [CmdletBinding()]
    param([int]$Last = 0)
    
    if ($Last -gt 0) {
        return $script:CommandHistory | Select-Object -Last $Last
    }
    
    return $script:CommandHistory
}

function Clear-CorelCommandHistory {
    <#
    .SYNOPSIS
        Limpa histórico de comandos.
    #>
    
    $script:CommandHistory = @()
    Write-CorelLog "Histórico limpo" -Level Info
}

#endregion

#region Module Initialization

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  CorelDRAW Automation Adapter - ONI Protocol v2.0     ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

#endregion


function Set-CorelAdapterSpeed {
    <#
    .SYNOPSIS
        Sets the speed of the Corel adapter (Normal vs Turbo).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("Normal", "Turbo", "Reflex")]
        [string]$Mode
    )

    switch ($Mode) {
        "Normal" { 
            $script:CorelConfig.DefaultDelay = 500
            $script:CorelConfig.SafetyDelays.Short = 100
            $script:CorelConfig.SafetyDelays.Medium = 300
            $script:CorelConfig.SafetyDelays.Long = 500
            Write-CorelLog "Speed: NORMAL (500ms)" -Level Info
        }
        "Turbo"  { 
            $script:CorelConfig.DefaultDelay = 100
            $script:CorelConfig.SafetyDelays.Short = 20
            $script:CorelConfig.SafetyDelays.Medium = 50
            $script:CorelConfig.SafetyDelays.Long = 100
            Write-CorelLog "Speed: TURBO (100ms)" -Level Warning
        }
        "Reflex" { 
            # Extreme Speed
            $script:CorelConfig.DefaultDelay = 20
            $script:CorelConfig.SafetyDelays.Short = 10
            $script:CorelConfig.SafetyDelays.Medium = 20
            $script:CorelConfig.SafetyDelays.Long = 50
            Write-CorelLog "Speed: REFLEX (20ms)" -Level Warning
        }
    }
}

#region Exports

Export-ModuleMember -Function @(
    'Connect-Corel',
    'Clear-CorelState',
    'Send-CorelShortcut',
    'Send-CorelInput',
    'Invoke-CorelSequence',
    'Get-CorelCommandHistory',
    'Clear-CorelCommandHistory',
    'Set-CorelAdapterSpeed'
)

#endregion

