param(
    [string]$WorkspacePath,
    [string]$Guid,
    [string]$Shortcut,
    [string]$OutputPath
)

# Function to clean up temp folders
function Clean-Temp {
    param($Path)
    if (Test-Path $Path) { Remove-Item $Path -Recurse -Force }
}

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) "CorelShortcutInjection"
Clean-Temp $tempDir
New-Item -ItemType Directory -Path $tempDir | Out-Null

try {
    # 1. Extract Workspace
    Write-Host "Extracting $WorkspacePath..." -ForegroundColor Cyan
    
    # Handle .cdws extension for Expand-Archive
    $zipSource = $WorkspacePath
    if ($WorkspacePath.EndsWith(".cdws")) {
        $zipSource = $WorkspacePath -replace "\.cdws$", ".zip"
        Copy-Item $WorkspacePath $zipSource -Force
    }

    Expand-Archive -Path $zipSource -DestinationPath $tempDir -Force

    $xmlPath = Join-Path $tempDir "content\workspace.xml"
    
    if (-not (Test-Path $xmlPath)) {
        throw "workspace.xml not found in archive!"
    }

    # 2. Load XML
    # Note: Using XmlDocument for easier manipulation
    $xml = New-Object System.Xml.XmlDocument
    $xml.Load($xmlPath)

    # 3. Find or Create 'items' collection
    $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
    # Corel XML usually doesn't have a default namespace in the root of workspace.xml based on inspection
    
    $uiConfig = $xml.SelectSingleNode("//uiConfig")
    if ($null -eq $uiConfig) { throw "Root <uiConfig> not found!" }

    $itemsNode = $uiConfig.SelectSingleNode("items")
    if ($null -eq $itemsNode) {
        Write-Host "Creating <items> node..."
        $itemsNode = $xml.CreateElement("items")
        $uiConfig.AppendChild($itemsNode) | Out-Null
    }

    # 4. Check if shortcut already exists for this GUID (Update vs Insert)
    # Strategy: We assume itemData with this GUID defines the shortcut
    $createNode = $true
    
    # We look for an existing itemData with this GUID
    $xpath = "//itemData[@guid='$Guid']"
    $existingItem = $itemsNode.SelectSingleNode($xpath)

    if ($existingItem) {
        Write-Host "Found existing item definition for GUID. Updating..."
        $createNode = $false
        $targetItem = $existingItem
    }
    else {
        Write-Host "Creating new item definition for GUID..."
        $targetItem = $xml.CreateElement("itemData")
        $targetItem.SetAttribute("guid", $Guid)
        $itemsNode.AppendChild($targetItem) | Out-Null
    }

    # 5. Inject keySequence
    # Remove existing keySequence if any
    $existingKeySeq = $targetItem.SelectSingleNode("keySequence")
    if ($existingKeySeq) {
        $targetItem.RemoveChild($existingKeySeq) | Out-Null
    }

    $keySeqNode = $xml.CreateElement("keySequence")
    $keySeqNode.InnerText = $Shortcut
    $targetItem.AppendChild($keySeqNode) | Out-Null

    # 6. Save XML
    Write-Host "Saving modified XML..." -ForegroundColor Cyan
    $xml.Save($xmlPath)

    # 7. Re-zip
    Write-Host "Creating new workspace file at $OutputPath..." -ForegroundColor Cyan
    if (Test-Path $OutputPath) { Remove-Item $OutputPath -Force }
    
    $tempZip = Join-Path $tempDir "package.zip"
    
    # Important: Compress the CONTENTS of the temp dir, not the dir itself
    Compress-Archive -Path "$tempDir\META-INF", "$tempDir\content", "$tempDir\previews", "$tempDir\mimetype" -DestinationPath $tempZip -Force
    
    Move-Item $tempZip $OutputPath -Force

    Write-Host "Success! Created $OutputPath" -ForegroundColor Green

}
catch {
    Write-Error "Failed: $_"
}
finally {
    Clean-Temp $tempDir
}
