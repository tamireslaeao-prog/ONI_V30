<#
.SYNOPSIS
    ONI V23 - Nexus Protocol (Advanced VBA Injection Engine)
    
.DESCRIPTION
    Motor avancado de injecao e execucao de codigo VBA no CorelDRAW.
    Suporta multiplos modulos, cache, debugging, rollback automatico e telemetria.
    
.PARAMETER VbaCode
    Codigo VBA a ser injetado (string ou caminho de arquivo)
    
.PARAMETER EntryPoint
    Nome da Sub/Function a ser executada
    
.PARAMETER ModuleName
    Nome do modulo VBA (gerado automaticamente se omitido)
    
.PARAMETER KeepModule
    Mantem o modulo apos execucao (util para debugging)
    
.PARAMETER FromFile
    Indica que VbaCode e um caminho de arquivo
    
.PARAMETER ReturnValue
    Captura valor de retorno de Functions
    
.PARAMETER Timeout
    Timeout em segundos (padrao: 300)
    
.PARAMETER WaitForCorel
    Aguarda CorelDRAW iniciar se nao detectado (segundos)

.EXAMPLE
    .\Invoke-CorelVBA.ps1 -VbaCode "Sub Test(): MsgBox `"OK`": End Sub" -EntryPoint "Test"
    
.EXAMPLE
    .\Invoke-CorelVBA.ps1 -FromFile "script.bas" -EntryPoint "ProcessShapes" -KeepModule
    
.EXAMPLE
    .\Invoke-CorelVBA.ps1 -VbaCode $code -WaitForCorel 30
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$VbaCode,
    
    [Parameter(Mandatory = $false)]
    [string]$EntryPoint = "Main",
    
    [Parameter(Mandatory = $false)]
    [string]$ModuleName,
    
    [Parameter(Mandatory = $false)]
    [switch]$KeepModule,
    
    [Parameter(Mandatory = $false)]
    [switch]$FromFile,
    
    [Parameter(Mandatory = $false)]
    [switch]$ReturnValue,
    
    [Parameter(Mandatory = $false)]
    [int]$Timeout = 300,
    
    [Parameter(Mandatory = $false)]
    [int]$WaitForCorel = 0
)

$ErrorActionPreference = "Stop"
$script:StartTime = Get-Date

#region Helper Functions

function Write-NexusLog {
    param(
        [string]$Message,
        [ValidateSet('Info', 'Success', 'Warning', 'Error', 'Debug')]
        [string]$Level = 'Info'
    )
    
    $colors = @{
        'Info'    = 'Cyan'
        'Success' = 'Green'
        'Warning' = 'Yellow'
        'Error'   = 'Red'
        'Debug'   = 'Gray'
    }
    
    $prefix = switch ($Level) {
        'Info' { "[NEXUS]" }
        'Success' { "[OK]" }
        'Warning' { "[AVISO]" }
        'Error' { "[ERRO]" }
        'Debug' { "[DBG]" }
    }
    
    $timestamp = (Get-Date).ToString("HH:mm:ss.fff")
    Write-Host "$timestamp $prefix $Message" -ForegroundColor $colors[$Level]
}

function Test-CorelRunning {
    $process = Get-Process -Name "CorelDRW" -ErrorAction SilentlyContinue
    return ($null -ne $process)
}

function Wait-ForCorelCOM {
    param([int]$TimeoutSeconds)
    
    if ($TimeoutSeconds -le 0) { return $false }
    
    Write-NexusLog "Aguardando CorelDRAW registrar COM..." -Level Info
    
    $elapsed = 0
    $interval = 2
    
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("CorelDRAW.Application")
            if ($null -ne $corel) {
                Write-NexusLog "CorelDRAW detectado via COM!" -Level Success
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($corel) | Out-Null
                Start-Sleep -Seconds 2
                return $true
            }
        }
        catch {
            # Ainda nao registrado
        }
        
        Write-Host "." -NoNewline -ForegroundColor Gray
        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }
    
    Write-Host ""
    return $false
}

function Get-CorelCOMObject {
    param([int]$RetryCount = 3)
    
    $progIds = @("CorelDRAW.Application.26", "CorelDRAW.Application", "CorelDRAW.Application.25", "CorelDRAW.Application.24")

    for ($i = 1; $i -le $RetryCount; $i++) {
        foreach ($progId in $progIds) {
            try {
                Write-NexusLog "Tentando conectar ao $progId (tentativa $i/$RetryCount)..." -Level Debug
                
                $corel = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
                
                if ($null -ne $corel) {
                    Write-NexusLog "Objeto COM ($progId) obtido com sucesso" -Level Debug
                    return $corel
                }
            }
            catch {
                # Silencioso, tentar proximo
            }
        }
        
        Write-NexusLog "Falha na tentativa ${i} para todos ProgIDs" -Level Debug
        if ($i -lt $RetryCount) {
            Start-Sleep -Seconds 2
        }
    }
    
    return $null
}

function New-CorelCOMObject {
    param([int]$TimeoutSeconds = 30)
    
    Write-NexusLog "Criando nova instancia COM do CorelDRAW..." -Level Info
    
    $progIds = @("CorelDRAW.Application.26", "CorelDRAW.Application", "CorelDRAW.Application.25")
    $corel = $null
    
    foreach ($progId in $progIds) {
        try {
            $corel = New-Object -ComObject $progId
            if ($null -ne $corel) {
                Write-NexusLog "Instancia criada com $progId" -Level Debug
                break
            }
        }
        catch {}
    }

    if ($null -eq $corel) { throw "Falha ao criar instancia COM (todos ProgIDs falharam)" }

    try {
        $corel.Visible = $true
        
        Write-NexusLog "Aguardando inicializacao completa..." -Level Info
        Start-Sleep -Seconds 3
        
        $elapsed = 0
        $interval = 1
        
        while ($elapsed -lt $TimeoutSeconds) {
            try {
                $doc = $corel.ActiveDocument
                if ($null -eq $doc) {
                    $corel.CreateDocument()
                }
                
                Write-NexusLog "CorelDRAW inicializado via COM" -Level Success
                return $corel
            }
            catch {
                Write-Host "." -NoNewline -ForegroundColor Gray
                Start-Sleep -Seconds $interval
                $elapsed += $interval
            }
        }
        
        Write-Host ""
        throw "Timeout aguardando CorelDRAW responder"
    }
    catch {
        throw "Falha na inicializacao pos-criacao: $_"
    }
}

function Test-VBProjectAccess {
    param($Document)
    
    try {
        $null = $Document.VBProject.VBComponents
        return $true
    }
    catch {
        Write-NexusLog "Acesso ao VBProject negado!" -Level Error
        Write-NexusLog "Solucao: CorelDRAW > Ferramentas > Opcoes > VBA > Marcar Confiar no acesso ao modelo de objeto" -Level Warning
        return $false
    }
}

function Get-UniqueModuleName {
    param([string]$BaseName = "ONI_Module")
    
    $timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
    $random = -join ((65..90) + (97..122) | Get-Random -Count 4 | ForEach-Object { [char]$_ })
    return "${BaseName}_${timestamp}_${random}"
}

function Remove-ExistingModule {
    param(
        $VBComponents,
        [string]$Name
    )
    
    try {
        $existing = $VBComponents.Item($Name)
        if ($null -ne $existing) {
            Write-NexusLog "Removendo modulo existente: $Name" -Level Debug
            $VBComponents.Remove($existing)
            Start-Sleep -Milliseconds 100
        }
    }
    catch {
        # Modulo nao existe, OK
    }
}

function Get-VbaCodeContent {
    param(
        [string]$Code,
        [bool]$IsFile
    )
    
    if ($IsFile) {
        if (-not (Test-Path $Code)) {
            throw "Arquivo nao encontrado: $Code"
        }
        
        $content = Get-Content -Path $Code -Raw -Encoding UTF8
        $size = $content.Length
        Write-NexusLog "Codigo carregado de arquivo: $size caracteres" -Level Debug
        return $content
    }
    
    return $Code
}

function Invoke-VbaMacroWithTimeout {
    param(
        $CorelApp,
        [string]$MacroPath,
        [int]$TimeoutSeconds
    )
    
    if ($TimeoutSeconds -le 0) {
        return $CorelApp.GMSManager.RunMacro($MacroPath, "")
    }
    
    $job = Start-Job -ScriptBlock {
        param($appTypeName, $macro)
        
        $app = [System.Runtime.InteropServices.Marshal]::GetActiveObject($appTypeName)
        $result = $app.GMSManager.RunMacro($macro, "")
        
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
        
        return $result
    } -ArgumentList "CorelDRAW.Application", $MacroPath
    
    $completed = Wait-Job -Job $job -Timeout $TimeoutSeconds
    
    if ($null -eq $completed) {
        Remove-Job -Job $job -Force
        throw "Timeout: Macro excedeu ${TimeoutSeconds}s"
    }
    
    $result = Receive-Job -Job $job
    Remove-Job -Job $job
    
    return $result
}

#endregion

#region Main Execution

try {
    Write-NexusLog "===================================================" -Level Info
    Write-NexusLog "ONI V23 - Nexus Protocol Initialized" -Level Info
    Write-NexusLog "===================================================" -Level Info
    
    # 1. Verificar se CorelDRAW esta rodando
    if (-not (Test-CorelRunning)) {
        Write-NexusLog "Processo CorelDRAW.exe nao detectado!" -Level Warning
        
        if ($WaitForCorel -gt 0) {
            Write-NexusLog "Modo de espera ativado ($WaitForCorel segundos)..." -Level Info
            
            if (-not (Wait-ForCorelCOM -TimeoutSeconds $WaitForCorel)) {
                throw "CorelDRAW nao foi iniciado dentro do tempo limite"
            }
        }
        else {
            throw "CorelDRAW nao esta em execucao. Inicie o programa e tente novamente."
        }
    }
    
    # 2. Conectar ao CorelDRAW via COM
    Write-NexusLog "Conectando ao CorelDRAW via COM..." -Level Info
    
    $corel = Get-CorelCOMObject -RetryCount 3
    
    if ($null -eq $corel) {
        Write-NexusLog "GetActiveObject falhou. Tentando New-Object..." -Level Warning
        $corel = New-CorelCOMObject -TimeoutSeconds 30
    }
    
    if ($null -eq $corel) {
        throw "Nao foi possivel obter objeto COM do CorelDRAW. Verifique se o programa esta aberto e respondendo."
    }
    
    Write-NexusLog "Conectado: CorelDRAW v$($corel.VersionMajor).$($corel.VersionMinor)" -Level Success
    
    # 3. Verificar documento ativo
    $doc = $corel.ActiveDocument
    
    if ($null -eq $doc) {
        throw "Nenhum documento aberto no CorelDRAW. Abra ou crie um documento."
    }
    
    Write-NexusLog "Documento: $($doc.Name)" -Level Info
    
    # 4. Verificar Acesso ao VBProject
    if (-not (Test-VBProjectAccess -Document $doc)) {
        throw "Acesso ao VBProject negado"
    }
    
    $vbComps = $doc.VBProject.VBComponents
    
    # 5. Processar Codigo VBA
    $vbaContent = Get-VbaCodeContent -Code $VbaCode -IsFile $FromFile.IsPresent
    
    # 6. Gerar Nome do Modulo
    if ([string]::IsNullOrEmpty($ModuleName)) {
        $ModuleName = Get-UniqueModuleName
    }
    
    Write-NexusLog "Modulo alvo: $ModuleName" -Level Info
    
    # 6.5. Debug VBComponents
    if ($null -eq $vbComps) {
        Write-NexusLog "ALERTA: vbComps estÃ¡ nulo! Tentando re-adquirir..." -Level Warning
        $vbComps = $doc.VBProject.VBComponents
    }
    
    if ($null -eq $vbComps) {
        throw "FATAL: Nao foi possivel acessar VBComponents."
    }
    Write-NexusLog "VBComponents Count: $($vbComps.Count)" -Level Debug

    # 7. Limpeza Preventiva
    Remove-ExistingModule -VBComponents $vbComps -Name $ModuleName
    
    # 8. Criar e Injetar Modulo
    Write-NexusLog "Injetando codigo VBA..." -Level Info
    
    try {
        $newModule = $vbComps.Add(1)  # vbext_ct_StdModule
    }
    catch {
        throw "Erro no vbComps.Add(1): $_"
    }
    $newModule.Name = $ModuleName
    
    $codeModule = $newModule.CodeModule
    $codeModule.AddFromString($vbaContent)
    
    $lineCount = $codeModule.CountOfLines
    Write-NexusLog "Codigo injetado: $lineCount linhas" -Level Success
    
    # 9. Executar Macro
    $macroPath = "${ModuleName}.${EntryPoint}"
    Write-NexusLog "Executando: $macroPath" -Level Info
    
    $executionStart = Get-Date
    
    try {
        $result = Invoke-VbaMacroWithTimeout -CorelApp $corel -MacroPath $macroPath -TimeoutSeconds $Timeout
        
        $executionTime = ((Get-Date) - $executionStart).TotalSeconds
        $executionRounded = [math]::Round($executionTime, 2)
        Write-NexusLog "Execucao concluida em ${executionRounded}s" -Level Success
        
        if ($ReturnValue -and $null -ne $result) {
            Write-NexusLog "Retorno: $result" -Level Info
        }
    }
    catch {
        Write-NexusLog "Erro durante execucao da macro: $_" -Level Error
        throw
    }
    
    # 10. Limpeza
    if (-not $KeepModule) {
        Write-NexusLog "Removendo modulo temporario..." -Level Debug
        $vbComps.Remove($newModule)
    }
    else {
        Write-NexusLog "Modulo mantido para debugging: $ModuleName" -Level Warning
    }
    
    # 11. Estatisticas Finais
    $totalTime = ((Get-Date) - $script:StartTime).TotalSeconds
    $totalRounded = [math]::Round($totalTime, 2)
    Write-NexusLog "===================================================" -Level Success
    Write-NexusLog "Operacao concluida com sucesso!" -Level Success
    Write-NexusLog "Tempo total: ${totalRounded}s" -Level Info
    Write-NexusLog "===================================================" -Level Success
    
    if ($ReturnValue) {
        return $result
    }
}
catch {
    Write-NexusLog "===================================================" -Level Error
    Write-NexusLog "FALHA NA OPERACAO" -Level Error
    Write-NexusLog "===================================================" -Level Error
    Write-NexusLog "Erro: $($_.Exception.Message)" -Level Error
    
    Write-NexusLog "Stack Trace:" -Level Debug
    Write-NexusLog $_.ScriptStackTrace -Level Debug
    
    # Cleanup em caso de erro
    if ($null -ne $newModule -and -not $KeepModule) {
        try {
            $vbComps.Remove($newModule)
            Write-NexusLog "Modulo removido apos erro" -Level Debug
        }
        catch { }
    }
    
    exit 1
}
finally {
    # Liberar objetos COM
    if ($null -ne $corel) {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($corel) | Out-Null
    }
    
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

#endregion
