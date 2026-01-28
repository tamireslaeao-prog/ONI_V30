# ============================================================================
# ONI CHROME QUICK START GUIDE
# ============================================================================

# ONI Chrome Module - Master Control for Web Automation

Este módulo fornece controle total sobre o Google Chrome para automação web.

## 📂 Estrutura

```
Modules/Chrome/
├── Scripts/
│   ├── ONI_Chrome_Harvester.ps1    # Extrai bookmarks, extensões, histórico
│   ├── ONI_Chrome_Controller.ps1   # Controle básico (abrir, fechar, focar)
│   └── ONI_Chrome_Scraper.ps1      # Web scraping com verificação visual
├── Assets/                          # Screenshots e dados coletados
├── Profiles/                        # Perfis dedicados para automação
└── assets_db.json                   # Banco de dados de bookmarks/extensões
```

## 🚀 Comandos Rápidos

### Harvester - Extrair dados do Chrome
```powershell
# Extrair bookmarks e extensões do perfil padrão
.\Scripts\ONI_Chrome_Harvester.ps1

# Usar perfil específico
.\Scripts\ONI_Chrome_Harvester.ps1 -ChromeProfilePath "C:\Users\user\AppData\Local\Google\Chrome\User Data\Profile 1"
```

### Controller - Controlar o Chrome
```powershell
# Abrir uma URL
.\Scripts\ONI_Chrome_Controller.ps1 -Action open -Url "https://google.com"

# Pesquisar no Google
.\Scripts\ONI_Chrome_Controller.ps1 -Action search -Url "iphone 15 preço"

# Abrir em modo incógnito
.\Scripts\ONI_Chrome_Controller.ps1 -Action open -Url "https://example.com" -Incognito

# Focar janela do Chrome
.\Scripts\ONI_Chrome_Controller.ps1 -Action focus

# Tirar screenshot via ONI Vision
.\Scripts\ONI_Chrome_Controller.ps1 -Action screenshot

# Coletar dados da página atual
.\Scripts\ONI_Chrome_Controller.ps1 -Action collect

# Nova aba
.\Scripts\ONI_Chrome_Controller.ps1 -Action new-tab

# Fechar Chrome
.\Scripts\ONI_Chrome_Controller.ps1 -Action close
```

### Scraper - Coletar dados de páginas
```powershell
# Extrair dados de uma URL
.\Scripts\ONI_Chrome_Scraper.ps1 -Url "https://mercadolivre.com.br" -Action extract

# Clicar em elemento por texto
.\Scripts\ONI_Chrome_Scraper.ps1 -Url "https://google.com" -Action click -Selector "Gmail"

# Digitar em campo
.\Scripts\ONI_Chrome_Scraper.ps1 -Url "https://google.com" -Action type -Selector "iphone 15"

# Esperar mais tempo para carregar
.\Scripts\ONI_Chrome_Scraper.ps1 -Url "https://site-lento.com" -WaitSeconds 10
```

## 🔗 Integração com ONI API

O módulo Chrome usa a API ONI para:
- `hybrid-vision/web` - Análise visual de páginas
- `click` - Cliques em coordenadas
- `type` - Digitação
- `keys` - Atalhos de teclado
- `focus` - Foco de janela

**Requisito:** Servidor ONI rodando em `http://localhost:8000`

## 📊 Dados Extraídos pelo Harvester

### Bookmarks
- Nome
- URL
- Pasta/Hierarquia
- Data de adição

### Extensões
- ID
- Nome
- Versão
- Descrição

### Preferências
- Motor de busca padrão
- Configurações

## 🎯 Casos de Uso

1. **Pesquisa de Preços**
   ```powershell
   .\Scripts\ONI_Chrome_Scraper.ps1 -Url "https://mercadolivre.com.br/iphone" -Action extract
   ```

2. **Monitoramento de Sites**
   ```powershell
   .\Scripts\ONI_Chrome_Controller.ps1 -Action open -Url "https://site.com"
   .\Scripts\ONI_Chrome_Controller.ps1 -Action screenshot
   ```

3. **Automação de Login** (requer perfil com cookies)
   ```powershell
   .\Scripts\ONI_Chrome_Controller.ps1 -Action open -Url "https://app.com" -Profile "MinhaConta"
   ```

## ⚠️ Notas

- O Chrome deve estar instalado em `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Perfis de automação são criados em `Modules\Chrome\Profiles\`
- Screenshots e dados coletados vão para `Modules\Chrome\Assets\`
