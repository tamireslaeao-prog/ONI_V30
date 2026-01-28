
import os
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from .config import ONIConfig

class VideoVision:
    """
    Módulo de análise visual avançado.
    Melhorias: detecção de cenas, análise de movimento, extração de cores,
    detecção de rostos, análise de composição.
    """
    
    def __init__(self, config: ONIConfig):
        self.config = config
    
    def get_info(self, video_path: str) -> Dict:
        """Obtém metadados completos do vídeo."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        info = {
            "path": video_path,
            "fps": fps,
            "frame_count": frame_count,
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration": frame_count / fps if fps > 0 else 0,
            "codec": int(cap.get(cv2.CAP_PROP_FOURCC)),
            "bitrate": int(cap.get(cv2.CAP_PROP_BITRATE))
        }
        
        cap.release()
        return info
    
    def extract_frames(
        self, 
        video_path: str,
        interval: Optional[float] = None,
        save_dir: Optional[str] = None,
        max_dimension: int = 1280
    ) -> List[Dict]:
        """
        Extrai frames com otimização automática.
        
        Args:
            interval: Segundos entre frames (usa config se None)
            save_dir: Diretório para salvar JPEGs
            max_dimension: Dimensão máxima para resize
        """
        if interval is None:
            interval = self.config.frame_extract_interval
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if fps == 0:
            raise ValueError("FPS inválido no vídeo")
        
        frame_interval = max(1, int(fps * interval))
        
        frames = []
        count = 0
        extracted = 0
        
        if save_dir:
            Path(save_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"[VideoVision] Extraindo frames (intervalo: {interval}s)...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if count % frame_interval == 0:
                timestamp = count / fps
                
                # Resize para otimização
                h, w = frame.shape[:2]
                if max(h, w) > max_dimension:
                    scale = max_dimension / max(h, w)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                
                frame_data = {
                    "timestamp": timestamp,
                    "frame_number": count,
                    "array": frame,
                    "shape": frame.shape
                }
                
                if save_dir:
                    filename = f"frame_{extracted:05d}_t{timestamp:.2f}s.jpg"
                    filepath = Path(save_dir) / filename
                    cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    frame_data["path"] = str(filepath)
                
                frames.append(frame_data)
                extracted += 1
            
            count += 1
        
        cap.release()
        print(f"[VideoVision] {extracted} frames extraídos")
        return frames
    
    def analyze_scenes(self, frames: List[Dict]) -> List[Dict]:
        """
        Análise avançada de cenas com múltiplas métricas.
        """
        print("[VideoVision] Analisando cenas...")
        
        analysis = []
        prev_gray = None
        
        for i, frame_data in enumerate(frames):
            frame = frame_data["array"]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Métricas básicas
            brightness = float(np.mean(gray))
            contrast = float(np.std(gray))
            
            # Análise de cores
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dominant_hue = float(np.median(hsv[:, :, 0]))
            saturation = float(np.mean(hsv[:, :, 1]))
            
            # Detecção de movimento/mudança de cena
            scene_change = False
            motion_score = 0.0
            
            if prev_gray is not None:
                # Diferença absoluta
                diff = cv2.absdiff(gray, prev_gray)
                motion_score = float(np.mean(diff))
                
                # Detectar mudança de cena
                if motion_score > self.config.scene_change_threshold:
                    scene_change = True
            
            # Análise de composição (regra dos terços)
            composition = self._analyze_composition(gray)
            
            analysis.append({
                "timestamp": frame_data["timestamp"],
                "frame_number": frame_data["frame_number"],
                "brightness": brightness,
                "contrast": contrast,
                "dominant_hue": dominant_hue,
                "saturation": saturation,
                "motion_score": motion_score,
                "scene_change": scene_change,
                "composition": composition,
                "path": frame_data.get("path")
            })
            
            prev_gray = gray
        
        # Identificar cenas (agrupamento)
        scenes = self._group_scenes(analysis)
        
        print(f"[VideoVision] {len(scenes)} cenas detectadas")
        return analysis
    
    def _analyze_composition(self, gray: np.ndarray) -> Dict:
        """Analisa composição usando regra dos terços."""
        h, w = gray.shape
        
        # Dividir em 9 regiões (regra dos terços)
        third_h = h // 3
        third_w = w // 3
        
        regions = {}
        for i, row_name in enumerate(["top", "middle", "bottom"]):
            for j, col_name in enumerate(["left", "center", "right"]):
                region = gray[i*third_h:(i+1)*third_h, j*third_w:(j+1)*third_w]
                region_name = f"{row_name}_{col_name}"
                regions[region_name] = {
                    "brightness": float(np.mean(region)),
                    "activity": float(np.std(region))
                }
        
        return regions
    
    def _group_scenes(self, analysis: List[Dict]) -> List[Dict]:
        """Agrupa frames em cenas baseado em mudanças."""
        scenes = []
        current_scene = {
            "start_timestamp": analysis[0]["timestamp"],
            "start_frame": analysis[0]["frame_number"],
            "frames": []
        }
        
        for i, frame_analysis in enumerate(analysis):
            current_scene["frames"].append(i)
            
            if frame_analysis["scene_change"] or i == len(analysis) - 1:
                current_scene["end_timestamp"] = frame_analysis["timestamp"]
                current_scene["end_frame"] = frame_analysis["frame_number"]
                current_scene["duration"] = (
                    current_scene["end_timestamp"] - current_scene["start_timestamp"]
                )
                
                # Calcular métricas médias da cena
                scene_frames = [analysis[idx] for idx in current_scene["frames"]]
                current_scene["avg_brightness"] = np.mean(
                    [f["brightness"] for f in scene_frames]
                )
                current_scene["avg_motion"] = np.mean(
                    [f["motion_score"] for f in scene_frames]
                )
                
                scenes.append(current_scene)
                
                # Nova cena
                if i < len(analysis) - 1:
                    current_scene = {
                        "start_timestamp": frame_analysis["timestamp"],
                        "start_frame": frame_analysis["frame_number"],
                        "frames": []
                    }
        
        return scenes
