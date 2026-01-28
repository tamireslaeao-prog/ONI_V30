# 🪟 WINDOWS KNOWLEDGE BASE

> **Módulo:** Modules/Windows
> **Versão:** V24
> **Status:** System Control Ready

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Atalho |
|------|--------|
| Executar | Win+R |
| Desktop | Win+D |
| Alternar janelas | Alt+Tab |
| Fechar janela | Alt+F4 |
| Task Manager | Ctrl+Shift+Esc |

### Comandos Bridge
```powershell
Import-Module .\ONI.Windows.psm1

# Informações do sistema
& $ONI.Core.GetSystemInfo

# Processos
& $ONI.Process.List "chrome"
& $ONI.Process.Kill "notepad"

# Serviços
& $ONI.Service.Start "wuauserv"

# Performance
& $ONI.Performance.GetCPU
& $ONI.Performance.GetMemory
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI.Windows.psm1` - Módulo PowerShell (668 linhas!)
- `Scripts/ONI_Windows_Automator.ps1`
- `Scripts/ONI_Windows_Harvester.ps1`
- `Scripts/ONI_Windows_Sentinel.ps1`

### Módulos Disponíveis
- **$ONI.Core:** Log, IsAdmin, GetSystemInfo
- **$ONI.Process:** List, Kill, Start, GetByPort, Monitor
- **$ONI.Service:** Start, Stop, Restart, GetStatus, SetStartup
- **$ONI.FileSystem:** Search, Copy, Delete, GetSize, FindDuplicates, CleanTemp
- **$ONI.Registry:** Get, Set, Delete, Export, Import
- **$ONI.Network:** GetAdapters, Ping, GetOpenPorts, FlushDNS, TestPort
- **$ONI.Performance:** GetCPU, GetMemory, GetDisk, GetTopProcesses, Monitor
- **$ONI.Task:** Create, Delete, List, Run
- **$ONI.Features:** List, Enable, Disable

---

## 💡 Dicas Avançadas

### Monitoramento em Tempo Real
```powershell
& $ONI.Performance.Monitor -Interval 2 -Duration 60
```

### Limpeza de Arquivos Temp
```powershell
& $ONI.FileSystem.CleanTemp
```

### Testar Porta
```powershell
& $ONI.Network.TestPort -Target "localhost" -Port 8000
```

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| Access Denied | Executar como Admin |
| Service not found | Verificar nome exato do serviço |
| RequireAdmin falha | Usar elevação de privilégios |
