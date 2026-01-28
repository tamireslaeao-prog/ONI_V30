"""
Sistema de Controle Total do Foxit PDF Editor Pro para IA
Permite controle completo de PDFs sem bloqueios
Suporta edição, criação, conversão, OCR, formulários, assinaturas e mais
"""

import win32com.client
import pythoncom
import os
import time
import threading
import queue
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import comtypes.client
import subprocess


class FoxitPDFController:
    """Controlador completo do Foxit PDF Editor Pro"""
    
    def __init__(self):
        self.foxit = None
        self.app = None
        self.current_doc = None
        self.command_queue = queue.Queue()
        self.running = False
        self.documents = {}
        
    def connect(self, foxit_path: str = None) -> bool:
        """Conecta ao Foxit PDF Editor Pro"""
        try:
            pythoncom.CoInitialize()
            
            # Tenta conectar via COM
            try:
                self.app = win32com.client.Dispatch("FoxitReader.Application")
                print("✓ Conectado ao Foxit via COM")
            except:
                # Se falhar, tenta iniciar o processo
                if foxit_path:
                    subprocess.Popen([foxit_path])
                    time.sleep(3)
                    self.app = win32com.client.Dispatch("FoxitReader.Application")
                else:
                    print("✗ Forneça o caminho do Foxit")
                    return False
            
            # Torna visível
            try:
                self.app.Visible = True
            except:
                pass
            
            print("✓ Foxit PDF sob controle total")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            print("NOTA: Instale Foxit PDF Editor Pro (não Reader)")
            return False
    
    # ==================== ABERTURA E CRIAÇÃO DE DOCUMENTOS ====================
    
    def open_pdf(self, filepath: str, name: str = None) -> Any:
        """Abre PDF existente"""
        try:
            if not os.path.exists(filepath):
                print(f"✗ Arquivo não encontrado: {filepath}")
                return None
            
            doc = self.app.OpenDoc(filepath, "")
            
            if name is None:
                name = os.path.basename(filepath)
            
            self.documents[name] = doc
            self.current_doc = doc
            
            print(f"✓ PDF aberto: {filepath}")
            return doc
            
        except Exception as e:
            print(f"✗ Erro ao abrir PDF: {e}")
            return None
    
    def create_pdf(self, name: str = "NewDocument.pdf") -> Any:
        """Cria novo PDF"""
        try:
            doc = self.app.NewDoc()
            self.documents[name] = doc
            self.current_doc = doc
            
            print(f"✓ Novo PDF criado: {name}")
            return doc
            
        except Exception as e:
            print(f"✗ Erro ao criar PDF: {e}")
            return None
    
    def close_pdf(self, name: str = None, save: bool = True) -> bool:
        """Fecha PDF"""
        try:
            if name and name in self.documents:
                doc = self.documents[name]
            else:
                doc = self.current_doc
            
            if doc:
                if save:
                    doc.Save(1)
                doc.Close()
                
                if name and name in self.documents:
                    del self.documents[name]
                
                print(f"✓ PDF fechado")
                return True
            return False
            
        except Exception as e:
            print(f"✗ Erro ao fechar: {e}")
            return False
    
    def save_pdf(self, filepath: str = None, doc_name: str = None) -> bool:
        """Salva PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            
            if not doc:
                return False
            
            if filepath:
                doc.SaveAs(filepath)
                print(f"✓ PDF salvo como: {filepath}")
            else:
                doc.Save(1)
                print(f"✓ PDF salvo")
            
            return True
            
        except Exception as e:
            print(f"✗ Erro ao salvar: {e}")
            return False
    
    # ==================== MANIPULAÇÃO DE PÁGINAS ====================
    
    def get_page_count(self, doc_name: str = None) -> int:
        """Obtém número de páginas"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if doc:
                return doc.NumPages
            return 0
        except Exception as e:
            print(f"✗ Erro: {e}")
            return 0
    
    def add_page(self, page_index: int = -1, width: float = 612, 
                 height: float = 792, doc_name: str = None) -> bool:
        """Adiciona nova página (tamanho padrão: Letter)"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            if page_index == -1:
                page_index = doc.NumPages
            
            doc.InsertPages(page_index, page_index, width, height)
            print(f"✓ Página adicionada no índice {page_index}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar página: {e}")
            return False
    
    def delete_page(self, page_index: int, doc_name: str = None) -> bool:
        """Deleta página"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            doc.DeletePages(page_index, page_index)
            print(f"✓ Página {page_index} deletada")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao deletar página: {e}")
            return False
    
    def rotate_page(self, page_index: int, rotation: int = 90,
                    doc_name: str = None) -> bool:
        """Rotaciona página (0, 90, 180, 270)"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            page.Rotation = rotation
            
            print(f"✓ Página {page_index} rotacionada {rotation}°")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao rotacionar: {e}")
            return False
    
    def extract_pages(self, start_page: int, end_page: int,
                     output_path: str, doc_name: str = None) -> bool:
        """Extrai páginas para novo PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            doc.ExtractPages(start_page, end_page, output_path)
            print(f"✓ Páginas {start_page}-{end_page} extraídas: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao extrair: {e}")
            return False
    
    # ==================== EDIÇÃO DE TEXTO ====================
    
    def add_text(self, page_index: int, x: float, y: float, text: str,
                font_size: int = 12, font_name: str = "Arial",
                color: Tuple[int, int, int] = (0, 0, 0),
                doc_name: str = None) -> bool:
        """Adiciona texto ao PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            # Cria anotação de texto
            annot = page.AddAnnot("FreeText")
            annot.SetContents(text)
            
            # Posição e tamanho
            rect = annot.GetRect()
            rect.left = x
            rect.bottom = y
            rect.right = x + len(text) * font_size * 0.6
            rect.top = y + font_size * 1.5
            annot.SetRect(rect)
            
            # Formatação
            annot.SetFontSize(font_size)
            annot.SetFontName(font_name)
            annot.SetColor(color[0], color[1], color[2])
            
            print(f"✓ Texto adicionado na página {page_index}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar texto: {e}")
            return False
    
    def edit_text(self, page_index: int, old_text: str, new_text: str,
                  doc_name: str = None) -> bool:
        """Substitui texto no PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            # Busca e substitui texto
            page.ReplaceText(old_text, new_text)
            
            print(f"✓ Texto substituído na página {page_index}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao editar texto: {e}")
            return False
    
    def search_text(self, search_term: str, doc_name: str = None) -> List[Dict]:
        """Busca texto no PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return []
            
            results = []
            
            for page_num in range(doc.NumPages):
                page = doc.GetPage(page_num)
                text_content = page.GetText()
                
                if search_term.lower() in text_content.lower():
                    results.append({
                        'page': page_num,
                        'text': text_content
                    })
            
            print(f"✓ Encontrado em {len(results)} páginas")
            return results
            
        except Exception as e:
            print(f"✗ Erro na busca: {e}")
            return []
    
    # ==================== IMAGENS ====================
    
    def add_image(self, page_index: int, image_path: str,
                 x: float, y: float, width: float = None, height: float = None,
                 doc_name: str = None) -> bool:
        """Adiciona imagem ao PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            if not os.path.exists(image_path):
                print(f"✗ Imagem não encontrada: {image_path}")
                return False
            
            page = doc.GetPage(page_index)
            
            # Adiciona imagem
            page.AddImage(image_path, x, y, width or 100, height or 100)
            
            print(f"✓ Imagem adicionada na página {page_index}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar imagem: {e}")
            return False
    
    def extract_images(self, page_index: int, output_dir: str,
                      doc_name: str = None) -> List[str]:
        """Extrai imagens de uma página"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return []
            
            os.makedirs(output_dir, exist_ok=True)
            
            page = doc.GetPage(page_index)
            images = page.ExtractImages(output_dir)
            
            print(f"✓ {len(images)} imagens extraídas")
            return images
            
        except Exception as e:
            print(f"✗ Erro ao extrair imagens: {e}")
            return []
    
    # ==================== ANOTAÇÕES ====================
    
    def add_highlight(self, page_index: int, x1: float, y1: float,
                     x2: float, y2: float,
                     color: Tuple[int, int, int] = (255, 255, 0),
                     doc_name: str = None) -> bool:
        """Adiciona highlight (marca texto)"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            annot = page.AddAnnot("Highlight")
            rect = annot.GetRect()
            rect.left = x1
            rect.bottom = y1
            rect.right = x2
            rect.top = y2
            annot.SetRect(rect)
            annot.SetColor(color[0], color[1], color[2])
            
            print(f"✓ Highlight adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar highlight: {e}")
            return False
    
    def add_comment(self, page_index: int, x: float, y: float,
                   comment: str, doc_name: str = None) -> bool:
        """Adiciona comentário"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            annot = page.AddAnnot("Note")
            annot.SetContents(comment)
            
            rect = annot.GetRect()
            rect.left = x
            rect.bottom = y
            rect.right = x + 20
            rect.top = y + 20
            annot.SetRect(rect)
            
            print(f"✓ Comentário adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar comentário: {e}")
            return False
    
    def add_stamp(self, page_index: int, x: float, y: float,
                 stamp_type: str = "Approved", doc_name: str = None) -> bool:
        """Adiciona carimbo (stamp)"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            annot = page.AddAnnot("Stamp")
            annot.SetStampType(stamp_type)
            
            rect = annot.GetRect()
            rect.left = x
            rect.bottom = y
            rect.right = x + 100
            rect.top = y + 50
            annot.SetRect(rect)
            
            print(f"✓ Carimbo '{stamp_type}' adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar carimbo: {e}")
            return False
    
    # ==================== FORMULÁRIOS ====================
    
    def add_text_field(self, page_index: int, x: float, y: float,
                      width: float, height: float, field_name: str,
                      default_value: str = "", doc_name: str = None) -> bool:
        """Adiciona campo de texto ao formulário"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            field = page.AddFormField("Text", field_name)
            field.SetDefaultValue(default_value)
            
            rect = field.GetRect()
            rect.left = x
            rect.bottom = y
            rect.right = x + width
            rect.top = y + height
            field.SetRect(rect)
            
            print(f"✓ Campo de texto '{field_name}' adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar campo: {e}")
            return False
    
    def add_checkbox(self, page_index: int, x: float, y: float,
                    field_name: str, checked: bool = False,
                    doc_name: str = None) -> bool:
        """Adiciona checkbox"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            field = page.AddFormField("CheckBox", field_name)
            field.SetChecked(checked)
            
            rect = field.GetRect()
            rect.left = x
            rect.bottom = y
            rect.right = x + 15
            rect.top = y + 15
            field.SetRect(rect)
            
            print(f"✓ Checkbox '{field_name}' adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar checkbox: {e}")
            return False
    
    def add_button(self, page_index: int, x: float, y: float,
                  width: float, height: float, label: str,
                  action: str = None, doc_name: str = None) -> bool:
        """Adiciona botão"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            field = page.AddFormField("Button", label)
            field.SetCaption(label)
            
            if action:
                field.SetAction(action)
            
            rect = field.GetRect()
            rect.left = x
            rect.bottom = y
            rect.right = x + width
            rect.top = y + height
            field.SetRect(rect)
            
            print(f"✓ Botão '{label}' adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar botão: {e}")
            return False
    
    def fill_form_field(self, field_name: str, value: Any,
                       doc_name: str = None) -> bool:
        """Preenche campo de formulário"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            field = doc.GetField(field_name)
            if field:
                field.SetValue(value)
                print(f"✓ Campo '{field_name}' preenchido")
                return True
            
            return False
            
        except Exception as e:
            print(f"✗ Erro ao preencher campo: {e}")
            return False
    
    # ==================== SEGURANÇA ====================
    
    def add_password(self, user_password: str, owner_password: str = None,
                    doc_name: str = None) -> bool:
        """Adiciona senha ao PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            security = doc.GetSecurity()
            security.SetUserPassword(user_password)
            
            if owner_password:
                security.SetOwnerPassword(owner_password)
            
            print(f"✓ Senha adicionada ao PDF")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar senha: {e}")
            return False
    
    def set_permissions(self, allow_print: bool = True,
                       allow_copy: bool = True,
                       allow_edit: bool = True,
                       doc_name: str = None) -> bool:
        """Define permissões do PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            security = doc.GetSecurity()
            security.SetPermissions({
                'print': allow_print,
                'copy': allow_copy,
                'edit': allow_edit
            })
            
            print(f"✓ Permissões configuradas")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao configurar permissões: {e}")
            return False
    
    def add_watermark(self, text: str, page_index: int = -1,
                     opacity: float = 0.5, rotation: int = 45,
                     doc_name: str = None) -> bool:
        """Adiciona marca d'água"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            if page_index == -1:
                # Aplica a todas as páginas
                for i in range(doc.NumPages):
                    page = doc.GetPage(i)
                    page.AddWatermark(text, opacity, rotation)
            else:
                page = doc.GetPage(page_index)
                page.AddWatermark(text, opacity, rotation)
            
            print(f"✓ Marca d'água adicionada")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar marca d'água: {e}")
            return False
    
    # ==================== CONVERSÃO ====================
    
    def convert_to_word(self, output_path: str, doc_name: str = None) -> bool:
        """Converte PDF para Word"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            doc.SaveAs(output_path, "Word")
            print(f"✓ Convertido para Word: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erro na conversão: {e}")
            return False
    
    def convert_to_excel(self, output_path: str, doc_name: str = None) -> bool:
        """Converte PDF para Excel"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            doc.SaveAs(output_path, "Excel")
            print(f"✓ Convertido para Excel: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erro na conversão: {e}")
            return False
    
    def convert_to_image(self, output_dir: str, format: str = "PNG",
                        dpi: int = 300, doc_name: str = None) -> List[str]:
        """Converte PDF para imagens"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return []
            
            os.makedirs(output_dir, exist_ok=True)
            
            images = []
            for i in range(doc.NumPages):
                output_file = os.path.join(output_dir, f"page_{i+1}.{format.lower()}")
                page = doc.GetPage(i)
                page.SaveAsImage(output_file, format, dpi)
                images.append(output_file)
            
            print(f"✓ {len(images)} páginas convertidas para {format}")
            return images
            
        except Exception as e:
            print(f"✗ Erro na conversão: {e}")
            return []
    
    # ==================== OCR ====================
    
    def perform_ocr(self, language: str = "English", doc_name: str = None) -> bool:
        """Executa OCR no PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            doc.PerformOCR(language)
            print(f"✓ OCR executado ({language})")
            return True
            
        except Exception as e:
            print(f"✗ Erro no OCR: {e}")
            return False
    
    def extract_text(self, page_index: int = None, doc_name: str = None) -> str:
        """Extrai texto do PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return ""
            
            if page_index is not None:
                page = doc.GetPage(page_index)
                text = page.GetText()
            else:
                # Extrai de todas as páginas
                text = ""
                for i in range(doc.NumPages):
                    page = doc.GetPage(i)
                    text += page.GetText() + "\n\n"
            
            print(f"✓ Texto extraído ({len(text)} caracteres)")
            return text
            
        except Exception as e:
            print(f"✗ Erro ao extrair texto: {e}")
            return ""
    
    # ==================== MERGE E SPLIT ====================
    
    def merge_pdfs(self, pdf_paths: List[str], output_path: str) -> bool:
        """Mescla múltiplos PDFs"""
        try:
            # Cria novo documento
            merged_doc = self.app.NewDoc()
            
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    temp_doc = self.app.OpenDoc(pdf_path, "")
                    
                    # Copia todas as páginas
                    for i in range(temp_doc.NumPages):
                        merged_doc.InsertPages(
                            merged_doc.NumPages,
                            merged_doc.NumPages,
                            temp_doc.GetPage(i)
                        )
                    
                    temp_doc.Close()
            
            merged_doc.SaveAs(output_path)
            merged_doc.Close()
            
            print(f"✓ {len(pdf_paths)} PDFs mesclados: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao mesclar: {e}")
            return False
    
    def split_pdf(self, output_dir: str, pages_per_file: int = 1,
                 doc_name: str = None) -> List[str]:
        """Divide PDF em múltiplos arquivos"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return []
            
            os.makedirs(output_dir, exist_ok=True)
            
            files = []
            total_pages = doc.NumPages
            file_count = 0
            
            for i in range(0, total_pages, pages_per_file):
                end_page = min(i + pages_per_file - 1, total_pages - 1)
                output_file = os.path.join(output_dir, f"split_{file_count+1}.pdf")
                
                doc.ExtractPages(i, end_page, output_file)
                files.append(output_file)
                file_count += 1
            
            print(f"✓ PDF dividido em {len(files)} arquivos")
            return files
            
        except Exception as e:
            print(f"✗ Erro ao dividir: {e}")
            return []
    
    # ==================== ASSINATURA DIGITAL ====================
    
    def add_signature_field(self, page_index: int, x: float, y: float,
                           width: float, height: float, field_name: str,
                           doc_name: str = None) -> bool:
        """Adiciona campo de assinatura"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            field = page.AddFormField("Signature", field_name)
            
            rect = field.GetRect()
            rect.left = x
            rect.bottom = y
            rect.right = x + width
            rect.top = y + height
            field.SetRect(rect)
            
            print(f"✓ Campo de assinatura '{field_name}' adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar campo de assinatura: {e}")
            return False
    
    def sign_pdf(self, certificate_path: str, password: str,
                field_name: str, doc_name: str = None) -> bool:
        """Assina PDF digitalmente"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            if not os.path.exists(certificate_path):
                print(f"✗ Certificado não encontrado: {certificate_path}")
                return False
            
            doc.SignDocument(field_name, certificate_path, password)
            print(f"✓ PDF assinado digitalmente")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao assinar: {e}")
            return False
    
    # ==================== MARCADORES (BOOKMARKS) ====================
    
    def add_bookmark(self, title: str, page_index: int,
                    parent_bookmark: str = None, doc_name: str = None) -> bool:
        """Adiciona marcador"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            bookmarks = doc.GetBookmarks()
            
            if parent_bookmark:
                parent = bookmarks.GetBookmark(parent_bookmark)
                bookmark = parent.AddChild(title)
            else:
                bookmark = bookmarks.AddRoot(title)
            
            bookmark.SetDestination(page_index)
            
            print(f"✓ Marcador '{title}' adicionado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar marcador: {e}")
            return False
    
    # ==================== LINKS ====================
    
    def add_link(self, page_index: int, x1: float, y1: float,
                x2: float, y2: float, url: str, doc_name: str = None) -> bool:
        """Adiciona hyperlink"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            annot = page.AddAnnot("Link")
            annot.SetURL(url)
            
            rect = annot.GetRect()
            rect.left = x1
            rect.bottom = y1
            rect.right = x2
            rect.top = y2
            annot.SetRect(rect)
            
            print(f"✓ Link adicionado: {url}")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar link: {e}")
            return False
    
    # ==================== OTIMIZAÇÃO ====================
    
    def optimize_pdf(self, output_path: str = None, 
                    compress_images: bool = True,
                    remove_duplicates: bool = True,
                    doc_name: str = None) -> bool:
        """Otimiza PDF (reduz tamanho)"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            options = {
                'CompressImages': compress_images,
                'RemoveDuplicates': remove_duplicates,
                'OptimizeForWeb': True
            }
            
            if output_path:
                doc.Optimize(options, output_path)
            else:
                doc.Optimize(options)
            
            print(f"✓ PDF otimizado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao otimizar: {e}")
            return False
    
    def linearize_pdf(self, output_path: str = None, doc_name: str = None) -> bool:
        """Lineariza PDF (Fast Web View)"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            if output_path:
                doc.SaveAs(output_path, options={'Linearize': True})
            else:
                doc.Save(1, options={'Linearize': True})
            
            print(f"✓ PDF linearizado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao linearizar: {e}")
            return False
    
    # ==================== COMPARAÇÃO ====================
    
    def compare_pdfs(self, pdf1_path: str, pdf2_path: str,
                    output_path: str) -> bool:
        """Compara dois PDFs"""
        try:
            doc1 = self.app.OpenDoc(pdf1_path, "")
            doc2 = self.app.OpenDoc(pdf2_path, "")
            
            comparison = self.app.CompareDocs(doc1, doc2)
            comparison.SaveAs(output_path)
            
            doc1.Close()
            doc2.Close()
            
            print(f"✓ PDFs comparados: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erro na comparação: {e}")
            return False
    
    # ==================== REDAÇÃO (REDACT) ====================
    
    def add_redaction(self, page_index: int, x1: float, y1: float,
                     x2: float, y2: float, doc_name: str = None) -> bool:
        """Adiciona área de redação"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            page = doc.GetPage(page_index)
            
            annot = page.AddAnnot("Redact")
            rect = annot.GetRect()
            rect.left = x1
            rect.bottom = y1
            rect.right = x2
            rect.top = y2
            annot.SetRect(rect)
            
            print(f"✓ Redação adicionada")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao adicionar redação: {e}")
            return False
    
    def apply_redactions(self, doc_name: str = None) -> bool:
        """Aplica todas as redações permanentemente"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            doc.ApplyRedactions()
            print(f"✓ Redações aplicadas permanentemente")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao aplicar redações: {e}")
            return False
    
    # ==================== BATCH PROCESSING ====================
    
    def batch_process(self, pdf_files: List[str], operation: str,
                     output_dir: str, **kwargs) -> List[str]:
        """Processa múltiplos PDFs em lote"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            results = []
            
            operations = {
                'ocr': lambda doc: doc.PerformOCR(kwargs.get('language', 'English')),
                'optimize': lambda doc: doc.Optimize({}),
                'watermark': lambda doc: self.add_watermark(
                    kwargs.get('text', 'CONFIDENTIAL'),
                    doc_name=doc
                ),
                'convert_to_word': lambda doc: self.convert_to_word(
                    os.path.join(output_dir, f"{os.path.basename(doc)}.docx"),
                    doc
                )
            }
            
            op_func = operations.get(operation)
            if not op_func:
                print(f"✗ Operação desconhecida: {operation}")
                return []
            
            for pdf_file in pdf_files:
                try:
                    doc_name = os.path.basename(pdf_file)
                    self.open_pdf(pdf_file, doc_name)
                    op_func(doc_name)
                    
                    output_file = os.path.join(output_dir, doc_name)
                    self.save_pdf(output_file, doc_name)
                    self.close_pdf(doc_name)
                    
                    results.append(output_file)
                except Exception as e:
                    print(f"✗ Erro processando {pdf_file}: {e}")
            
            print(f"✓ Batch: {len(results)}/{len(pdf_files)} processados")
            return results
            
        except Exception as e:
            print(f"✗ Erro no batch: {e}")
            return []
    
    # ==================== SISTEMA DE FILA ====================
    
    def start_command_processor(self):
        """Inicia processador de comandos"""
        self.running = True
        thread = threading.Thread(target=self._process_commands, daemon=True)
        thread.start()
        print("✓ Processador Foxit iniciado")
    
    def _process_commands(self):
        """Processa comandos da fila"""
        while self.running:
            try:
                if not self.command_queue.empty():
                    cmd_data = self.command_queue.get(timeout=0.1)
                    func = cmd_data['function']
                    args = cmd_data.get('args', ())
                    kwargs = cmd_data.get('kwargs', {})
                    func(*args, **kwargs)
                else:
                    time.sleep(0.01)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"✗ Erro no processador: {e}")
    
    def queue_action(self, func, *args, **kwargs):
        """Adiciona ação à fila"""
        self.command_queue.put({
            'function': func,
            'args': args,
            'kwargs': kwargs
        })
    
    def stop_command_processor(self):
        """Para processador"""
        self.running = False
        print("✓ Processador Foxit parado")
    
    # ==================== UTILIDADES ====================
    
    def get_pdf_info(self, doc_name: str = None) -> Dict:
        """Obtém informações do PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return {}
            
            info = {
                'pages': doc.NumPages,
                'title': doc.GetTitle(),
                'author': doc.GetAuthor(),
                'subject': doc.GetSubject(),
                'keywords': doc.GetKeywords(),
                'creator': doc.GetCreator(),
                'producer': doc.GetProducer(),
                'creation_date': doc.GetCreationDate(),
                'modification_date': doc.GetModificationDate(),
                'file_size': doc.GetFileSize()
            }
            
            return info
            
        except Exception as e:
            print(f"✗ Erro ao obter info: {e}")
            return {}
    
    def set_pdf_info(self, title: str = None, author: str = None,
                    subject: str = None, keywords: str = None,
                    doc_name: str = None) -> bool:
        """Define metadados do PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            if title:
                doc.SetTitle(title)
            if author:
                doc.SetAuthor(author)
            if subject:
                doc.SetSubject(subject)
            if keywords:
                doc.SetKeywords(keywords)
            
            print(f"✓ Metadados atualizados")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao definir metadados: {e}")
            return False
    
    def print_pdf(self, printer_name: str = None, doc_name: str = None) -> bool:
        """Imprime PDF"""
        try:
            doc = self.documents.get(doc_name, self.current_doc)
            if not doc:
                return False
            
            if printer_name:
                doc.Print(printer_name)
            else:
                doc.Print()
            
            print(f"✓ PDF enviado para impressão")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao imprimir: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do Foxit"""
        try:
            self.stop_command_processor()
            
            # Fecha todos os documentos
            for doc_name in list(self.documents.keys()):
                self.close_pdf(doc_name, save=True)
            
            if self.app:
                try:
                    self.app.Quit()
                except:
                    pass
            
            pythoncom.CoUninitialize()
            print("✓ Foxit desconectado")
            
        except Exception as e:
            print(f"✗ Erro ao desconectar: {e}")


# ==================== EXEMPLO DE USO ====================

if __name__ == "__main__":
    # Inicializa controlador
    foxit = FoxitPDFController()
    
    # Conecta (forneça o caminho se necessário)
    if foxit.connect():
        print("\n=== FOXIT PDF SOB CONTROLE TOTAL DA IA ===\n")
        
        # Exemplo 1: Criar novo PDF
        print("1. Criando novo PDF...")
        foxit.create_pdf("MeuDocumento.pdf")
        foxit.add_page(0, 612, 792)  # Letter size
        
        # Exemplo 2: Adicionar texto
        print("\n2. Adicionando texto...")
        foxit.add_text(0, 100, 700, "Documento Criado por IA", 
                      font_size=24, color=(0, 0, 255))
        foxit.add_text(0, 100, 650, "Sistema de Controle Total do Foxit PDF",
                      font_size=14)
        
        # Exemplo 3: Adicionar imagem
        # foxit.add_image(0, "logo.png", 100, 500, 200, 100)
        
        # Exemplo 4: Adicionar formulário
        print("\n3. Criando formulário...")
        foxit.add_text_field(0, 100, 400, 200, 30, "nome", "Digite seu nome")
        foxit.add_checkbox(0, 100, 350, "concordo", False)
        foxit.add_button(0, 100, 300, 100, 40, "Enviar")
        
        # Exemplo 5: Adicionar anotações
        print("\n4. Adicionando anotações...")
        foxit.add_highlight(0, 100, 200, 300, 220, color=(255, 255, 0))
        foxit.add_comment(0, 350, 200, "Revisar este texto")
        foxit.add_stamp(0, 400, 100, "Approved")
        
        # Exemplo 6: Salvar
        print("\n5. Salvando PDF...")
        foxit.save_pdf("output_ia.pdf")
        
        # Exemplo 7: Abrir PDF existente
        # foxit.open_pdf("documento.pdf")
        
        # Exemplo 8: Operações avançadas
        # foxit.perform_ocr()
        # foxit.add_watermark("CONFIDENCIAL", opacity=0.3)
        # foxit.add_password("senha123")
        # foxit.optimize_pdf("documento_otimizado.pdf")
        
        # Exemplo 9: Conversão
        # foxit.convert_to_word("documento.docx")
        # foxit.convert_to_image("./images", format="PNG", dpi=300)
        
        # Exemplo 10: Batch processing
        # pdf_list = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        # foxit.batch_process(pdf_list, 'ocr', './output', language='Portuguese')
        
        # Sistema de fila
        foxit.start_command_processor()
        foxit.queue_action(foxit.add_text, 0, 100, 100, "Texto na fila", 12)
        
        time.sleep(2)
        
        print("\n✓ Sistema pronto! Foxit sob controle total da IA")
        
        # Desconectar
        # foxit.disconnect()
