
import os
import subprocess
import json
import numpy as np
import whisper
import torch
from pathlib import Path
from typing import Dict, List, Optional
from datetime import timedelta
from .config import ONIConfig

class AudioTranscriber:
    """
    Módulo de transcrição de áudio com Whisper.
    Melhorias: melhor gestão de erros, suporte a múltiplos formatos,
    detecção automática de idioma, análise de confiança.
    """
    
    def __init__(self, config: ONIConfig):
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[AudioTranscriber] Inicializando...")
        print(f"  Modelo: {config.whisper_model}")
        print(f"  Device: {self.device}")
        
        try:
            self.model = whisper.load_model(config.whisper_model, device=self.device)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar Whisper: {e}")
            raise
    
    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extrai áudio do vídeo com melhor qualidade.
        Suporta múltiplos formatos de vídeo.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")
        
        if output_path is None:
            output_path = os.path.join(
                self.config.temp_dir, 
                f"{Path(video_path).stem}_audio.wav"
            )
        
        print(f"[AudioTranscriber] Extraindo áudio...")
        print(f"  Input: {video_path}")
        print(f"  Output: {output_path}")
        
        cmd = [
            self.config.ffmpeg_path, '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            '-ar', str(self.config.sample_rate),  # Sample rate
            '-ac', '1',  # Mono
            '-y',  # Overwrite
            output_path
        ]
        
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg falhou: {result.stderr}")
        
        return output_path
    
    def transcribe(
        self, 
        audio_path: str,
        language: Optional[str] = None,
        detect_language: bool = False
    ) -> Dict:
        """
        Transcreve áudio com análise de confiança.
        
        Returns:
            {
                "text": str,
                "language": str,
                "segments": [...],
                "confidence": float,
                "duration": float
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")
        
        print(f"[AudioTranscriber] Transcrevendo {audio_path}...")
        
        # Configurar parâmetros
        params = {
            "word_timestamps": True,
            "verbose": False
        }
        
        if not detect_language:
            params["language"] = language or self.config.language
        
        # Transcrever
        result = self.model.transcribe(audio_path, **params)
        
        # Calcular confiança média
        confidences = []
        for segment in result.get("segments", []):
            if "words" in segment:
                for word in segment["words"]:
                    if "probability" in word:
                        confidences.append(word["probability"])
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Calcular duração
        duration = max(
            (seg["end"] for seg in result.get("segments", [])), 
            default=0.0
        )
        
        # Resultado enriquecido
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": result["segments"],
            "confidence": float(avg_confidence),
            "duration": duration,
            "word_count": len(result["text"].split())
        }
    
    def export_formats(self, transcription: Dict, base_path: str) -> Dict[str, str]:
        """
        Exporta transcrição em múltiplos formatos.
        
        Returns:
            {"srt": path, "vtt": path, "txt": path, "json": path}
        """
        segments = transcription["segments"]
        base = Path(base_path)
        
        files = {}
        
        # SRT
        srt_path = base.with_suffix(".srt")
        self._export_srt(segments, str(srt_path))
        files["srt"] = str(srt_path)
        
        # VTT
        vtt_path = base.with_suffix(".vtt")
        self._export_vtt(segments, str(vtt_path))
        files["vtt"] = str(vtt_path)
        
        # TXT
        txt_path = base.with_suffix(".txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(transcription["text"])
        files["txt"] = str(txt_path)
        
        # JSON (completo com metadados)
        json_path = base.with_suffix(".json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(transcription, f, ensure_ascii=False, indent=2)
        files["json"] = str(json_path)
        
        print(f"[AudioTranscriber] Exportados {len(files)} formatos")
        return files
    
    def _export_srt(self, segments: List[Dict], output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, seg in enumerate(segments, start=1):
                start = self._format_timestamp(seg['start'])
                end = self._format_timestamp(seg['end'])
                text = seg['text'].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    
    def _export_vtt(self, segments: List[Dict], output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for seg in segments:
                start = self._format_timestamp(seg['start'], vtt=True)
                end = self._format_timestamp(seg['end'], vtt=True)
                text = seg['text'].strip()
                f.write(f"{start} --> {end}\n{text}\n\n")
    
    def _format_timestamp(self, seconds: float, vtt: bool = False) -> str:
        td = timedelta(seconds=seconds)
        h = td.seconds // 3600
        m = (td.seconds % 3600) // 60
        s = td.seconds % 60
        ms = td.microseconds // 1000
        sep = "." if vtt else ","
        return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"
