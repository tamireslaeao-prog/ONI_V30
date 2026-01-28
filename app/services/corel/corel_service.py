"""
CorelDRAW Service - Production Integration
Controle total com vetorização Bezier por IA
Versão 2.2 - Merged: Correção de Coordenadas e Viewport Capture
"""

import win32com.client
import pythoncom
import numpy as np
import cv2
from PIL import Image
from typing import List, Tuple, Optional, Dict, Any
import os
import tempfile
import logging
from pathlib import Path
import time
import io
import win32clipboard

from app.infrastructure.monitoring.logger import get_logger

logger = get_logger(__name__)


class CorelService:
    """Controlador principal do CorelDRAW com suporte completo à ferramenta Bezier"""
    
    def __init__(self):
        self.app = None
        self.doc = None
        self.page = None
        self.layer = None
        self.version = None
        self._connected = False
        self.temp_dir = Path(tempfile.gettempdir()) / "corel_ai_vectorizer"
        self.temp_dir.mkdir(exist_ok=True)
        
        # ONI V25 - Persistent Hardcoded Path (Validated for this machine)
        self.validated_path = r"c:\Program Files\Corel\CorelDRAW Graphics Suite\26\Programs64\CorelDRW.exe"
        self.requires_elevation = True
    
    def _ensure_connection(self):
        """Garante conexão antes de operações (Lazy Loading)"""
        if self._connected and self.app:
            try:
                # Verifica se ainda está vivo
                _ = self.app.Version
                return True
            except:
                self._connected = False
                self.app = None
        
        return self.connect()
    
    def connect(self) -> bool:
        """Conecta ao CorelDRAW independente da versão instalada"""
        try:
            pythoncom.CoInitialize()
            
            # Tenta conectar a uma instância em execução
            try:
                self.app = win32com.client.GetActiveObject("CorelDRAW.Application")
                logger.info("corel_connected_existing")
            except:
                # Tenta conexão via Dispatch
                versions = [
                    "CorelDRAW.Application.26",  # 2024
                    "CorelDRAW.Application.25",
                    "CorelDRAW.Application"
                ]
                
                for ver in versions:
                    try:
                        self.app = win32com.client.Dispatch(ver)
                        logger.info("corel_started_via_dispatch", version=ver)
                        break
                    except Exception as e:
                        if "0x800702e4" in str(e) or "elevation" in str(e).lower():
                            logger.warning("corel_requires_elevation", version=ver)
                            # Se falhou por elevação e temos o path validado, tenta o Sovereign Restart
                            if self.validated_path:
                                return self.sovereign_restart()
                        continue
            
            if not self.app:
                # Fallback final: Tenta o Sovereign Restart se nada funcionou
                if self.validated_path:
                    return self.sovereign_restart()
                return False
            
            self.app.Visible = True
            self.version = self._get_version()
            self._init_document()
            self._connected = True
            return True
            
        except Exception as e:
            logger.error("corel_connection_error", error=str(e))
            return False

    def sovereign_restart(self) -> bool:
        """ONI Sovereign Protocol: Força o reinício elevado do Corel se necessário"""
        logger.info("triggering_sovereign_restart", path=self.validated_path)
        try:
            import subprocess
            # Usa o script já validado para forçar admin
            restart_script = Path("Modules/Corel/Scripts/start_corel_admin.ps1")
            if restart_script.exists():
                subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(restart_script)], 
                             capture_output=True, check=True)
                # Dá tempo para o processo subir
                time.sleep(5)
                # Tenta reconectar ao objeto que agora deve estar disponível via GetActiveObject
                # ou via nova tentativa de Dispatch que agora deve ser permitida se o servidor estiver elevado.
                return self.connect()
            return False
        except Exception as e:
            logger.error("sovereign_restart_failed", error=str(e))
            return False
    
    def _get_version(self) -> str:
        """Detecta a versão do CorelDRAW"""
        try:
            version = self.app.Version
            logger.info("corel_version", version=version)
            return version
        except:
            return "Unknown"
    
    def _init_document(self):
        """Inicializa ou obtém o documento ativo"""
        try:
            if self.app.ActiveDocument:
                self.doc = self.app.ActiveDocument
                logger.info("corel_using_existing_doc", name=self.doc.Name)
            else:
                self.doc = self.app.CreateDocument()
                logger.info("corel_new_doc_created")
        except:
            self.doc = self.app.CreateDocument()
            logger.info("corel_new_doc_created_fallback")
        
        self.page = self.doc.ActivePage
        self.layer = self.page.ActiveLayer
    
    def get_page_image(self, dpi: int = 150) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Captura APENAS a área da página usando exportação nativa do CorelDRAW
        CORRIGE o bug de coordenadas - agora 1:1 com a página real
        """
        self._ensure_connection()
        
        temp_file = self.temp_dir / f"page_capture_{os.getpid()}.png"
        
        try:
            # Exporta apenas a página atual como bitmap (PNG)
            # Args: FileName, Filter(770=PNG), Mode(1=Page), Width(0), Height(0), DPIX, DPIY
            self.doc.ExportBitmap(
                str(temp_file),
                770,  # cdrPNG (Filter)
                1,    # cdrExportPage (Mode)
                0,    # Width (0=Calc)
                0,    # Height (0=Calc)
                dpi,
                dpi
            )
            
            # Aguarda conclusão da exportação
            timeout = 5
            start = time.time()
            while not temp_file.exists() and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            if not temp_file.exists():
                raise FileNotFoundError("Export failed or timed out")
            
            # Carrega a imagem
            img = cv2.imread(str(temp_file))
            if img is None:
                raise ValueError("Failed to load exported image")
                
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Calcula metadados para mapeamento correto
            img_height, img_width = img_rgb.shape[:2]
            page_width = self.page.SizeWidth  # unidades do Corel (geralmente mm)
            page_height = self.page.SizeHeight
            
            metadata = {
                "image_size": (img_width, img_height),
                "page_size": (page_width, page_height),
                "dpi": dpi,
                "scale_x": page_width / img_width,  # unidades_corel por pixel
                "scale_y": page_height / img_height,
                "temp_file": str(temp_file)
            }
            
            logger.info("corel_page_captured", size=f"{img_width}x{img_height}")
            return img_rgb, metadata
            
        except Exception as e:
            logger.error("corel_capture_error", error=str(e))
            raise
    
    def pixel_to_page_coords(self, px: int, py: int, metadata: Dict) -> Tuple[float, float]:
        """
        Converte coordenadas de pixel para coordenadas da página do CorelDRAW
        CORRIGIDO: Inverte eixo Y corretamente
        CorelDRAW: Origem Bottom-Left, Y cresce para cima
        Imagem: Origem Top-Left, Y cresce para baixo
        """
        x = px * metadata['scale_x']
        y = metadata['page_size'][1] - (py * metadata['scale_y'])
        return x, y
    
    def create_bezier_curve(self, points: List[Tuple[float, float]], 
                           closed: bool = False) -> object:
        """Cria uma curva Bezier com pontos específicos"""
        self._ensure_connection()
        
        if len(points) < 2:
            raise ValueError("Need at least 2 points")
        
        try:
            curve = self.layer.CreateCurve()
            
            for i, (x, y) in enumerate(points):
                if i == 0:
                    curve.CreateSubPath(x, y)
                else:
                    curve.AppendLineSegment(x, y)
            
            if closed:
                curve.SubPaths[0].Closed = True
            
            return curve
        except Exception as e:
            logger.error("corel_create_bezier_error", error=str(e))
            raise
    
    def create_smooth_bezier(self, points: List[Tuple[float, float]], 
                            smoothness: float = 0.3,
                            closed: bool = False) -> object:
        """Cria uma curva Bezier suave"""
        self._ensure_connection()
        
        if len(points) < 2:
            raise ValueError("Need at least 2 points")
        
        try:
            curve = self.layer.CreateCurve()
            
            for i, (x, y) in enumerate(points):
                if i == 0:
                    curve.CreateSubPath(x, y)
                else:
                    prev_x, prev_y = points[i-1]
                    
                    if i < len(points) - 1:
                        next_x, next_y = points[i+1]
                        ctrl_x = x - (next_x - prev_x) * smoothness
                        ctrl_y = y - (next_y - prev_y) * smoothness
                    else:
                        ctrl_x = x
                        ctrl_y = y
                    
                    curve.AppendCurveSegment(
                        prev_x + (x - prev_x) * smoothness,
                        prev_y + (y - prev_y) * smoothness,
                        ctrl_x, ctrl_y,
                        x, y
                    )
            
            if closed:
                curve.SubPaths[0].Closed = True
            
            return curve
        except Exception as e:
            logger.error("corel_smooth_bezier_error", error=str(e))
            raise
    
    def set_curve_properties(self, curve: object, 
                           outline_width: float = 0.5,
                           outline_color: Tuple[int, int, int] = (0, 0, 0),
                           fill_color: Optional[Tuple[int, int, int]] = None):
        """Define propriedades visuais da curva"""
        try:
            curve.Outline.Width = outline_width
            curve.Outline.Color.RGBAssign(*outline_color)
            
            if fill_color:
                curve.Fill.UniformColor.RGBAssign(*fill_color)
            else:
                curve.Fill.ApplyNoFill()
        except Exception as e:
            logger.error("corel_properties_error", error=str(e))
            raise
    
    def vectorize_image_trace(self, image: np.ndarray, 
                             metadata: Dict,
                             threshold: int = 127,
                             min_area: int = 100,
                             epsilon_factor: float = 0.005) -> List[object]:
        """Vetoriza uma imagem detectando contornos"""
        self._ensure_connection()
        
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            logger.info("corel_contours_detected", count=len(contours))
            
            curves = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if area < min_area:
                    continue
                
                epsilon = epsilon_factor * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Conversão correta usando metadados
                points = []
                for point in approx:
                    px, py = point[0][0], point[0][1]
                    x, y = self.pixel_to_page_coords(px, py, metadata)
                    points.append((x, y))
                
                if len(points) >= 3:
                    try:
                        curve = self.create_smooth_bezier(points, closed=True, smoothness=0.2)
                        self.set_curve_properties(curve, outline_width=0.3)
                        curves.append(curve)
                    except Exception as e:
                        logger.warning("corel_curve_creation_failed", error=str(e))
            
            logger.info("corel_curves_created", count=len(curves))
            return curves
            
        except Exception as e:
            logger.error("corel_vectorize_error", error=str(e))
            raise
    
    def clear_page(self):
        """Limpa todos os objetos da página atual"""
        self._ensure_connection()
        try:
            shapes = self.page.Shapes
            if shapes.Count > 0:
                shapes.All().Delete()
                logger.info("corel_page_cleared")
        except Exception as e:
            logger.error("corel_clear_error", error=str(e))
            raise
    
    def _copy_image_to_clipboard(self, image_path: str):
        """Copia imagem para o clipboard para colar no Corel"""
        try:
            image = Image.open(image_path)
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            logger.error("clipboard_copy_error", error=str(e))
            return False

    def import_image(self, image_path: str, x: float = 0, y: float = 0) -> object:
        """Importa uma imagem para o canvas (usando Paste se Import falhar)"""
        self._ensure_connection()
        try:
            # Refresh context
            if self.doc is None:
                self._init_document()
            self.page = self.doc.ActivePage
            self.layer = self.page.ActiveLayer
            
            # Tentar método Paste (mais robusto que Import via COM)
            if self._copy_image_to_clipboard(image_path):
                try:
                    self.layer.Paste()
                    # O objeto colado é selecionado automaticamente
                    # Selection is a method in COM
                    sel = self.doc.Selection()
                    if sel.Shapes.Count > 0:
                        img = sel.Shapes.Item(1)
                        img.SetPosition(x, y)
                        return img
                except Exception as e_paste:
                    logger.warning("corel_paste_failed", error=str(e_paste))
            
            # Fallback para método Import original
            logger.info("fallback_to_import_method")
            imp_filter = self.layer.Import(image_path)
            imp_filter.Finish()
            
            # Check selection
            sel = self.doc.Selection()
            if sel.Shapes.Count > 0:
                img = sel.Shapes.Item(1)
                img.SetPosition(x, y)
                return img
                
            return None
        except Exception as e:
            logger.error("corel_import_error", error=str(e))
            return None
    
    def save_document(self, file_path: str):
        """Salva o documento"""
        self._ensure_connection()
        self.doc.SaveAs(file_path)
        logger.info("corel_document_saved", path=file_path)
    
    def cleanup_temp_files(self):
        """Remove arquivos temporários"""
        try:
            for file in self.temp_dir.glob("page_capture_*.png"):
                file.unlink()
            logger.info("corel_temp_cleaned")
        except Exception as e:
            logger.warning("corel_cleanup_warning", error=str(e))


class AIVectorizerInterface:
    """Interface para controle por IA do processo de vetorização"""
    
    def __init__(self, service: CorelService = None):
        self.controller = service or CorelService()
        self.current_image = None
        self.current_metadata = None
        self.vectorization_history = []
    
    def load_page_image(self, dpi: int = 150) -> Dict:
        """Carrega imagem da PÁGINA para análise pela IA"""
        try:
            self.current_image, self.current_metadata = self.controller.get_page_image(dpi)
            
            return {
                "status": "success",
                "shape": self.current_image.shape,
                "page_size": self.current_metadata["page_size"],
                "dpi": dpi,
                "metadata": self.current_metadata
            }
        except Exception as e:
            logger.error("corel_load_page_error", error=str(e))
            return {"status": "error", "message": str(e)}
    
    def create_bezier_from_pixels(self, pixel_points: List[List[int]], 
                                  smooth: bool = True,
                                  closed: bool = False,
                                  outline_color: Optional[List[int]] = None,
                                  fill_color: Optional[List[int]] = None) -> Dict:
        """Cria Bezier a partir de coordenadas de pixel"""
        try:
            if self.current_metadata is None:
                return {"status": "error", "message": "Load page image first"}
            
            page_points = []
            for px, py in pixel_points:
                x, y = self.controller.pixel_to_page_coords(px, py, self.current_metadata)
                page_points.append((x, y))
            
            if smooth:
                curve = self.controller.create_smooth_bezier(page_points, closed=closed)
            else:
                curve = self.controller.create_bezier_curve(page_points, closed=closed)
            
            self.controller.set_curve_properties(
                curve,
                outline_color=tuple(outline_color) if outline_color else (0, 0, 0),
                fill_color=tuple(fill_color) if fill_color else None
            )
            
            self.vectorization_history.append({
                "type": "bezier",
                "pixel_points": pixel_points,
                "page_points": page_points
            })
            
            return {
                "status": "success",
                "points_count": len(pixel_points),
                "page_coords": page_points
            }
        except Exception as e:
            logger.error("corel_bezier_error", error=str(e))
            return {"status": "error", "message": str(e)}
    
    def auto_vectorize(self, threshold: int = 127, 
                      min_area: int = 100,
                      epsilon_factor: float = 0.005) -> Dict:
        """Vetorização automática da imagem atual"""
        try:
            if self.current_image is None or self.current_metadata is None:
                result = self.load_page_image()
                if result["status"] == "error":
                    return result
            
            curves = self.controller.vectorize_image_trace(
                self.current_image,
                self.current_metadata,
                threshold=threshold,
                min_area=min_area,
                epsilon_factor=epsilon_factor
            )
            
            return {
                "status": "success",
                "curves_created": len(curves)
            }
        except Exception as e:
            logger.error("corel_auto_vectorize_error", error=str(e))
            return {"status": "error", "message": str(e)}
    
    def get_image_analysis(self) -> Dict:
        """Retorna análise da imagem para a IA decidir estratégia"""
        try:
            if self.current_image is None:
                result = self.load_page_image()
                if result["status"] == "error":
                    return result
            
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            return {
                "status": "success",
                "image_size": self.current_image.shape,
                "page_size": self.current_metadata["page_size"],
                "contours_detected": len(contours),
                "edge_density": float(np.sum(edges > 0) / edges.size),
                "brightness": float(np.mean(gray)),
                "contrast": float(np.std(gray))
            }
        except Exception as e:
            logger.error("corel_analysis_error", error=str(e))
            return {"status": "error", "message": str(e)}
    
    def clear_and_reset(self) -> Dict:
        """Limpa página e reseta histórico"""
        try:
            self.controller.clear_page()
            self.vectorization_history = []
            self.current_image = None
            self.current_metadata = None
            return {"status": "cleared"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def cleanup(self):
        """Limpeza final"""
        self.controller.cleanup_temp_files()
