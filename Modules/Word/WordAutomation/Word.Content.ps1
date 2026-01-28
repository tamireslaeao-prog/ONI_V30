# ============================================================================
# Word.Content.ps1
# Content creation functions (text, headings, paragraphs)
# ============================================================================

function ConvertFrom-HexColor {
    param([string]$HexColor)
    $hex = $HexColor.TrimStart('#')
    return @{
        R = [Convert]::ToInt32($hex.Substring(0, 2), 16)
        G = [Convert]::ToInt32($hex.Substring(2, 2), 16)
        B = [Convert]::ToInt32($hex.Substring(4, 2), 16)
    }
}

function Add-WordText {
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$Text,
        
        [string]$Style = "Normal",
        [string]$FontName = "",
        [int]$FontSize = 0,
        [string]$FontColor = "",
        [switch]$Bold,
        [switch]$Italic,
        [string]$Alignment = "Left"
    )
    
    $selection = $Document.Application.Selection
    
    if ($Style) {
        try {
            $selection.Style = $Document.Styles[$Style]
        }
        catch {
            Write-Warning "Style '$Style' not found, using Normal"
        }
    }
    
    if ($FontName) { $selection.Font.Name = $FontName }
    if ($FontSize -gt 0) { $selection.Font.Size = $FontSize }
    if ($Bold) { $selection.Font.Bold = 1 }
    if ($Italic) { $selection.Font.Italic = 1 }
    if ($FontColor) {
        $rgb = ConvertFrom-HexColor -HexColor $FontColor
        $selection.Font.Color = $rgb.R + ($rgb.G * 256) + ($rgb.B * 65536)
    }
    
    $alignments = @{
        "Left"    = 0
        "Center"  = 1
        "Right"   = 2
        "Justify" = 3
    }
    if ($alignments.ContainsKey($Alignment)) {
        $selection.ParagraphFormat.Alignment = $alignments[$Alignment]
    }
    
    $selection.TypeText($Text)
    $selection.TypeParagraph()
}

function Add-WordHeading {
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$Text,
        
        [int]$Level = 1
    )
    
    $styleName = "Heading $Level"
    Add-WordText -Document $Document -Text $Text -Style $styleName
}

function Add-WordParagraph {
    param(
        [Parameter(Mandatory = $true)]
        $Document,
        
        [Parameter(Mandatory = $true)]
        [string]$Text,
        
        [double]$SpaceBefore = 0,
        [double]$SpaceAfter = 0,
        [double]$LineSpacing = 1.0,
        [string]$Alignment = "Left"
    )
    
    $selection = $Document.Application.Selection
    
    if ($SpaceBefore -gt 0) {
        $selection.ParagraphFormat.SpaceBefore = $SpaceBefore
    }
    if ($SpaceAfter -gt 0) {
        $selection.ParagraphFormat.SpaceAfter = $SpaceAfter
    }
    
    $selection.ParagraphFormat.LineSpacingRule = 0
    $selection.ParagraphFormat.LineSpacing = $LineSpacing * 12
    
    Add-WordText -Document $Document -Text $Text -Alignment $Alignment
}

Export-ModuleMember -Function Add-WordText, Add-WordHeading, Add-WordParagraph
