---
description: Generate a structured eBook (PDF) from video lectures with extracted slides
---

# ONI VIDEO TO EBOOK WORKFLOW

## Prerequisites
- Video file (.ts, .mp4) OR SRT transcription file
- Pre-extracted slide PNGs (optional - script can extract from video)
- FFmpeg configured in `Modules/Oni_Engine/config.py`
- Python packages: `weasyprint`, `pillow`, `markdown`

---

## Phase 1: Input Analysis

### 1.1 Check Available Files
```powershell
# List contents of input folder
Get-ChildItem "temp/aula X"
```

**Expected files:**
- `*.srt` - Transcription file (required)
- `*.ts` or `*.mp4` - Video file (optional if slides pre-extracted)
- Subfolder with `*.png` - Pre-extracted slides (optional)

---

## Phase 2: Slide Processing

### 2.1 Extract Slides from Video (if needed)
```powershell
python "app/scripts/extract_slides.py"
```
- Uses FFmpeg scene detection (`select='gt(scene,0.015)'`)
- Outputs to `temp/OUTPUT_AULA_X/images/`

### 2.2 Crop Slides (CRITICAL - Remove headers/logos/webcam)
```powershell
python "app/scripts/crop_slides.py"
```

**IMPORTANT: Adjust crop parameters per video layout:**
```python
# For video with webcam on right:
crop_right = int(width * 0.80)   # Remove right 20% (webcam)
crop_top = int(height * 0.22)    # Remove top 22% (blue header bar)
crop_bottom = int(height * 0.82) # Remove bottom 18% (NPG logo/footer)

# For pre-extracted slides (no webcam):
crop_right = width  # Keep full width
crop_top = int(height * 0.12)    # Remove top 12% (header)
crop_bottom = int(height * 0.88) # Remove bottom 12% (footer)
```

- Outputs to `temp/OUTPUT_AULA_X/images_cropped/`
- **Verify cropped images visually before proceeding!**

---

## Phase 3: Content Authoring (THE GIGANTE PART)

### 3.1 Read Full SRT Transcription
Read the ENTIRE SRT file (can be 5000+ lines). Extract all key topics.

### 3.2 Create Structured Markdown
**CRITICAL: The eBook must be COMPREHENSIVE and DIDACTIC, not a summary!**

Follow the NPG format with FULL content extraction:

```markdown
# [Título da Aula]
## [Módulo]

---

## Prefácio
- Contextualização da aula
- Lista de tópicos a serem cobertos
- Referência à próxima aula (se dividida)

![Tópicos da Aula](images_cropped/slide_001.png)

---

## Capítulo 1: [Tópico Principal]

### 1.1 [Subtópico]
[Conteúdo DETALHADO extraído da transcrição]

### 1.2 [Subtópico]
[Tabelas sempre que possível]

| Coluna 1 | Coluna 2 | Coluna 3 |
|----------|----------|----------|
| Dado 1   | Dado 2   | Dado 3   |

> **Mensagem-Chave**: [Ponto importante em destaque]

![Legenda da Imagem](images_cropped/slide_XXX.png)

---

## Capítulo 2: [Próximo Tópico Principal]
[Continuar com TODAS as informações do SRT...]

---

## Conclusão
- Tabela de resumo dos conceitos-chave
- Preview da próxima aula

---
*© 2025 NPG - Neuropsiquiatria Geriátrica. Todos os direitos reservados.*
```

### 3.3 Image Placement Rules
- Insert images at contextually relevant positions
- Use descriptive captions
- Path format: `images_cropped/slide_XXX.png`
- View sample slides to identify which ones match each chapter

---

## Phase 4: PDF Generation

### 4.1 Create Generator Script
Copy and adapt from existing scripts in `Modules/Oni_Engine/templates/`.

### 4.2 NPG CSS Essentials (Include in script)
```css
@page { size: A4; margin: 12mm; }
.header { background: linear-gradient(135deg, #4285f4, #0d47a1); }
img { max-width: 100%; page-break-inside: avoid; }
p, li { orphans: 3; widows: 3; }
h2, h3, h4 { page-break-after: avoid; }
table th { background-color: #4285f4; color: white; }
blockquote { background-color: #e8f0fe; border-left: 5px solid #4285f4; }
```

---

## Output Files

```
temp/OUTPUT_AULA_X/
├── ebook_structured.md    # Source markdown (~300+ lines for GIGANTE)
├── ebook.html             # Intermediate HTML
├── AulaX_[Tema].pdf       # Final styled PDF
└── images_cropped/        # Cropped slide images
```

---

## Troubleshooting

### Permission Denied on PDF
- Close the PDF file in viewer
- Or change output filename in script

### Images Not Appearing
- Check `base_url` in WeasyPrint call points to `OUTPUT_DIR`
- Verify image paths are relative to MD location

### Whitespace/Page Break Issues
- Add `orphans: 3; widows: 3;` to CSS
- Use `page-break-inside: avoid` on images
- Add `page-break-after: avoid` on headings

### Images Still Have Headers/Logos
- Adjust crop parameters in `crop_slides.py`
- Top crop: 0.18-0.22 (for header bar)
- Bottom crop: 0.82-0.88 (for logos)
- Right crop: 0.80 (if webcam present)

### Content Too Short (Not GIGANTE)
- Read MORE of the SRT file (all 5000+ lines)
- Extract EVERY concept, not just main points
- Add tables, blockquotes, subchapters
- Include clinical implications, historical context
- Target: ~300+ lines in ebook_structured.md
