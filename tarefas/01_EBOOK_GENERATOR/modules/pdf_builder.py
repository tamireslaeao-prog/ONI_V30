import os
import markdown
from weasyprint import HTML, CSS

def build_pdf(input_dir, output_dir, assets_dir):
    """
    Builds the PDF from content.md in input_dir.
    Images are resolved relative to input_dir.
    Style is loaded from assets_dir/style.css.
    Returns the path to the generated PDF.
    """
    
    # 1. Paths
    md_file = os.path.join(input_dir, 'content.md')
    css_file = os.path.join(assets_dir, 'style.css')
    output_pdf = os.path.join(output_dir, 'eBook_Final.pdf')
    
    # 2. Read Markdown
    if not os.path.exists(md_file):
        raise FileNotFoundError(f"Content file missing: {md_file}")
        
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    # 3. Pre-process Content (Dynamic Path Injection)
    # Replaces 'images/mold_placeholder.svg' with the actual absolute path from output
    # This solves the issue where the mold is in OUTPUT but referenced in INPUT markdown
    mold_abs_path = os.path.join(output_dir, "molde_aula10.svg").replace("\\", "/")
    md_content = md_content.replace("images/MOLD_PLACEHOLDER.svg", f"file:///{mold_abs_path}")
    
    # 4. Convert to HTML
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # 5. Wrap in HTML Boilerplate
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Montserrat:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');
        </style>
    </head>
    <body>
        <div class="main-content">
            {html_body}
        </div>
    </body>
    </html>
    """
    
    # 6. Render PDF
    # base_url=input_dir allows standard "images/photo.jpg" to work if the folder is in input
    print(f"      ... Rendering with base_url: {input_dir}")
    HTML(string=html_content, base_url=input_dir).write_pdf(
        output_pdf,
        stylesheets=[CSS(css_file)]
    )
    
    return output_pdf
