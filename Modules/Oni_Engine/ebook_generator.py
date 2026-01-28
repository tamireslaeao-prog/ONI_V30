
# ============================================================================
# GERADOR DE EBOOK A PARTIR DE TRANSCRIÇÕES DE VÍDEO
# Converte transcrições em eBooks formatados: MD → HTML → PDF
# ============================================================================

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from datetime import datetime

try:
    import markdown
except ImportError:
    markdown = None
    print("[WARN] 'markdown' library not installed. eBook features limited.")

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    HTML = CSS = FontConfiguration = None
    print("[WARN] 'weasyprint' library not installed. PDF generation disabled.")


# ----------------------------------------------------------------------------
# 1. TranscriptProcessor
# ----------------------------------------------------------------------------

class TranscriptProcessor:
    """Processa e estrutura transcrições de vídeo."""
    
    def __init__(self):
        self.chapters = []
        self.metadata = {}
    
    def load_transcription(self, transcription_data: Dict) -> None:
        """Carrega dados de transcrição do Whisper."""
        self.raw_transcription = transcription_data
        self.segments = transcription_data.get("segments", [])
        self.full_text = transcription_data.get("text", "")
    
    def detect_chapters(
        self, 
        pause_threshold: float = 3.0,
        min_chapter_duration: float = 30.0
    ) -> List[Dict]:
        """
        Detecta capítulos baseado em pausas longas na fala.
        
        Args:
            pause_threshold: Segundos de pausa para considerar nova seção
            min_chapter_duration: Duração mínima de um capítulo
        """
        chapters = []
        current_chapter = {
            "start": 0,
            "segments": [],
            "text": ""
        }
        
        for i, segment in enumerate(self.segments):
            current_chapter["segments"].append(segment)
            current_chapter["text"] += " " + segment["text"]
            
            # Verificar pausa até próximo segmento
            if i < len(self.segments) - 1:
                next_segment = self.segments[i + 1]
                pause = next_segment["start"] - segment["end"]
                
                if pause >= pause_threshold:
                    duration = segment["end"] - current_chapter["start"]
                    if duration >= min_chapter_duration:
                        current_chapter["end"] = segment["end"]
                        current_chapter["duration"] = duration
                        chapters.append(current_chapter)
                        
                        # Novo capítulo
                        current_chapter = {
                            "start": next_segment["start"],
                            "segments": [],
                            "text": ""
                        }
        
        # Último capítulo
        if current_chapter["segments"]:
            last_seg = current_chapter["segments"][-1]
            current_chapter["end"] = last_seg["end"]
            current_chapter["duration"] = current_chapter["end"] - current_chapter["start"]
            chapters.append(current_chapter)
        
        self.chapters = chapters
        return chapters
    
    def generate_chapter_titles(self, chapters: Optional[List[Dict]] = None) -> List[str]:
        """
        Gera títulos inteligentes para capítulos baseado no conteúdo.
        Usa as primeiras palavras-chave significativas.
        """
        if chapters is None:
            chapters = self.chapters
        
        titles = []
        for i, chapter in enumerate(chapters, 1):
            # Pegar primeiras palavras significativas
            words = chapter["text"].strip().split()[:10]
            
            # Remover palavras comuns
            stop_words = {"e", "a", "o", "de", "da", "do", "em", "para", "com", "um", "uma"}
            meaningful = [w for w in words if w.lower() not in stop_words]
            
            if meaningful:
                title = " ".join(meaningful[:5])
                # Capitalizar
                title = title.capitalize()
                # Limitar tamanho
                if len(title) > 50:
                    title = title[:47] + "..."
            else:
                title = f"Seção {i}"
            
            titles.append(title)
        
        return titles
    
    def clean_text(self, text: str) -> str:
        """Limpa e formata texto da transcrição."""
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text)
        
        # Capitaliza início de frases
        text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        # Primeira letra maiúscula
        if text:
            text = text[0].upper() + text[1:]
        
        # Remove espaços antes de pontuação
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        return text.strip()


# ----------------------------------------------------------------------------
# 2. EBookGenerator
# ----------------------------------------------------------------------------

class EBookGenerator:
    """Gera eBooks formatados em MD, HTML e PDF."""
    
    def __init__(self):
        self.metadata = {
            "title": "eBook Gerado Automaticamente",
            "author": "Transcrição Automática",
            "date": datetime.now().strftime("%d/%m/%Y"),
            "description": ""
        }
        self.content = []
        self.chapters = []
    
    def set_metadata(
        self, 
        title: str, 
        author: str = "Auto-gerado",
        description: str = ""
    ) -> None:
        """Define metadados do eBook."""
        self.metadata.update({
            "title": title,
            "author": author,
            "description": description,
            "date": datetime.now().strftime("%d/%m/%Y")
        })
    
    def add_chapter(self, title: str, content: str, timestamp: Optional[str] = None) -> None:
        """Adiciona um capítulo ao eBook."""
        self.chapters.append({
            "title": title,
            "content": content,
            "timestamp": timestamp
        })
    
    def generate_markdown(self, output_path: str) -> str:
        """Gera eBook em formato Markdown."""
        md_content = []
        
        # Cabeçalho
        md_content.append(f"# {self.metadata['title']}\n")
        md_content.append(f"**Autor:** {self.metadata['author']}  ")
        md_content.append(f"**Data:** {self.metadata['date']}  \n")
        
        if self.metadata['description']:
            md_content.append(f"\n## Sobre\n\n{self.metadata['description']}\n")
        
        # Índice
        md_content.append("\n---\n\n## Índice\n")
        for i, chapter in enumerate(self.chapters, 1):
            md_content.append(f"{i}. [{chapter['title']}](#{self._slugify(chapter['title'])})")
            if chapter.get('timestamp'):
                md_content.append(f" *({chapter['timestamp']})*")
            md_content.append("\n")
        
        md_content.append("\n---\n")
        
        # Capítulos
        for i, chapter in enumerate(self.chapters, 1):
            md_content.append(f"\n## {i}. {chapter['title']}\n")
            if chapter.get('timestamp'):
                md_content.append(f"*Timestamp: {chapter['timestamp']}*\n\n")
            md_content.append(f"{chapter['content']}\n")
            md_content.append("\n---\n")
        
        # Salvar
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(md_content))
        
        return output_path
    
    def generate_html(self, output_path: str, css_style: str = "default") -> str:
        """Gera eBook em formato HTML com CSS."""
        
        # CSS personalizado
        css = self._get_css_style(css_style)
        
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.metadata['title']}</title>
    <style>{css}</style>
</head>
<body>
    <div class="container">
        <!-- Capa -->
        <div class="cover">
            <h1 class="title">{self.metadata['title']}</h1>
            <p class="author">por {self.metadata['author']}</p>
            <p class="date">{self.metadata['date']}</p>
        </div>
        
        <!-- Sobre -->
        {f'<div class="about"><h2>Sobre este eBook</h2><p>{self.metadata["description"]}</p></div>' if self.metadata['description'] else ''}
        
        <!-- Índice -->
        <div class="toc">
            <h2>Índice</h2>
            <ul>
"""
        
        for i, chapter in enumerate(self.chapters, 1):
            timestamp = f" <span class='timestamp'>({chapter['timestamp']})</span>" if chapter.get('timestamp') else ""
            html_content += f"                <li><a href='#chapter-{i}'>{i}. {chapter['title']}</a>{timestamp}</li>\n"
        
        html_content += """            </ul>
        </div>
        
        <!-- Capítulos -->
        <div class="content">
"""
        
        for i, chapter in enumerate(self.chapters, 1):
            timestamp_html = f"<p class='timestamp'>⏱️ Timestamp: {chapter['timestamp']}</p>" if chapter.get('timestamp') else ""
            html_content += f"""
            <div class="chapter" id="chapter-{i}">
                <h2>{i}. {chapter['title']}</h2>
                {timestamp_html}
                <div class="chapter-content">
                    {self._markdown_to_html(chapter['content'])}
                </div>
            </div>
"""
        
        html_content += """
        </div>
        
        <!-- Rodapé -->
        <footer>
            <p>Gerado automaticamente a partir de transcrição de vídeo</p>
        </footer>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_pdf(self, html_path: str, output_path: str) -> str:
        """Gera PDF a partir do HTML usando WeasyPrint."""
        font_config = FontConfiguration()
        
        # CSS adicional para PDF
        pdf_css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
                @top-right {
                    content: counter(page);
                    font-size: 10pt;
                    color: #666;
                }
            }
            .cover {
                page-break-after: always;
            }
            .chapter {
                page-break-before: always;
            }
        ''', font_config=font_config)
        
        html = HTML(filename=html_path)
        html.write_pdf(output_path, stylesheets=[pdf_css], font_config=font_config)
        
        return output_path
    
    def _markdown_to_html(self, text: str) -> str:
        """Converte Markdown simples para HTML."""
        # Parágrafos
        paragraphs = text.split('\n\n')
        html_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
        return '\n'.join(html_paragraphs)
    
    def _slugify(self, text: str) -> str:
        """Converte texto em slug para âncoras."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def _get_css_style(self, style_name: str) -> str:
        """Retorna CSS para o eBook."""
        styles = {
            "default": """
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Georgia', serif;
                    line-height: 1.8;
                    color: #333;
                    background: #f5f5f5;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }
                .cover {
                    text-align: center;
                    padding: 100px 0;
                    border-bottom: 3px solid #2c3e50;
                    margin-bottom: 60px;
                }
                .title {
                    font-size: 48px;
                    color: #2c3e50;
                    margin-bottom: 20px;
                    font-weight: bold;
                }
                .author {
                    font-size: 24px;
                    color: #7f8c8d;
                    font-style: italic;
                    margin-bottom: 10px;
                }
                .date {
                    font-size: 16px;
                    color: #95a5a6;
                }
                .about {
                    background: #ecf0f1;
                    padding: 30px;
                    margin-bottom: 40px;
                    border-left: 4px solid #3498db;
                }
                .about h2 {
                    color: #2c3e50;
                    margin-bottom: 15px;
                }
                .toc {
                    background: #f8f9fa;
                    padding: 30px;
                    margin-bottom: 40px;
                    border-radius: 8px;
                }
                .toc h2 {
                    color: #2c3e50;
                    margin-bottom: 20px;
                    font-size: 28px;
                }
                .toc ul {
                    list-style: none;
                }
                .toc li {
                    padding: 10px 0;
                    border-bottom: 1px solid #ddd;
                }
                .toc a {
                    color: #3498db;
                    text-decoration: none;
                    font-size: 18px;
                    transition: color 0.3s;
                }
                .toc a:hover {
                    color: #2980b9;
                }
                .timestamp {
                    color: #7f8c8d;
                    font-size: 14px;
                    font-style: italic;
                }
                .chapter {
                    margin-bottom: 60px;
                }
                .chapter h2 {
                    color: #2c3e50;
                    font-size: 32px;
                    margin-bottom: 20px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #3498db;
                }
                .chapter-content {
                    margin-top: 20px;
                }
                .chapter-content p {
                    margin-bottom: 20px;
                    text-align: justify;
                    font-size: 16px;
                }
                footer {
                    text-align: center;
                    padding: 40px 0;
                    color: #95a5a6;
                    border-top: 2px solid #ecf0f1;
                    margin-top: 60px;
                    font-size: 14px;
                }
            """
        }
        return styles.get(style_name, styles["default"])


# ----------------------------------------------------------------------------
# 3. VideoToEBook
# ----------------------------------------------------------------------------

class VideoToEBook:
    """Orquestrador completo de vídeo para eBook."""
    
    def __init__(self):
        self.processor = TranscriptProcessor()
        self.generator = EBookGenerator()
    
    def process(
        self,
        transcription_data: Dict,
        output_dir: str = "ebook_output",
        title: Optional[str] = None,
        author: str = "Transcrição Automática",
        description: str = "",
        pause_threshold: float = 3.0
    ) -> Dict[str, str]:
        """
        Pipeline completo de geração de eBook.
        
        Args:
            transcription_data: Dados do Whisper
            output_dir: Diretório de saída
            title: Título do eBook (auto-detectado se None)
            author: Autor do eBook
            description: Descrição
            pause_threshold: Segundos de pausa para detectar capítulos
        
        Returns:
            Dict com caminhos dos arquivos gerados
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print("GERANDO EBOOK A PARTIR DA TRANSCRIÇÃO")
        print(f"{'='*70}\n")
        
        # 1. Processar transcrição
        print("[1/5] Processando transcrição...")
        self.processor.load_transcription(transcription_data)
        
        # 2. Detectar capítulos
        print(f"[2/5] Detectando capítulos (pausa >= {pause_threshold}s)...")
        chapters = self.processor.detect_chapters(pause_threshold=pause_threshold)
        print(f"      ✓ {len(chapters)} capítulos detectados")
        
        # 3. Gerar títulos
        print("[3/5] Gerando títulos inteligentes...")
        titles = self.processor.generate_chapter_titles(chapters)
        
        # 4. Configurar eBook
        if title is None:
            title = f"Transcrição: {titles[0]}" if titles else "eBook da Transcrição"
        
        self.generator.set_metadata(
            title=title,
            author=author,
            description=description or "eBook gerado automaticamente a partir de transcrição de vídeo."
        )
        
        # 5. Adicionar capítulos
        print("[4/5] Estruturando conteúdo...")
        for i, (chapter, chapter_title) in enumerate(zip(chapters, titles)):
            content = self.processor.clean_text(chapter["text"])
            
            # Timestamp formatado
            start_time = self._format_timestamp(chapter["start"])
            end_time = self._format_timestamp(chapter["end"])
            timestamp = f"{start_time} - {end_time}"
            
            self.generator.add_chapter(
                title=chapter_title,
                content=content,
                timestamp=timestamp
            )
        
        # 6. Gerar arquivos
        print("[5/5] Gerando arquivos...")
        
        files = {}
        
        # Markdown
        md_path = str(output_path / "ebook.md")
        self.generator.generate_markdown(md_path)
        files["markdown"] = md_path
        print(f"      ✓ Markdown: {md_path}")
        
        # HTML
        html_path = str(output_path / "ebook.html")
        self.generator.generate_html(html_path)
        files["html"] = html_path
        print(f"      ✓ HTML: {html_path}")
        
        # PDF
        pdf_path = str(output_path / "ebook.pdf")
        self.generator.generate_pdf(html_path, pdf_path)
        files["pdf"] = pdf_path
        print(f"      ✓ PDF: {pdf_path}")
        
        print(f"\n{'='*70}")
        print("✓ EBOOK GERADO COM SUCESSO!")
        print(f"{'='*70}")
        print(f"Título: {self.generator.metadata['title']}")
        print(f"Capítulos: {len(chapters)}")
        print(f"Formatos: MD, HTML, PDF")
        print(f"\n📁 Arquivos salvos em: {output_dir}/")
        
        return files
    
    def _format_timestamp(self, seconds: float) -> str:
        """Formata segundos em HH:MM:SS."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
