
# -------------------------------------------------------------------------
# ONI V24 - UNIFIED ARCHITECTURE
# Module: Video Brain (Orchestrator)
# Version: 23.0
# Description: Central intelligence for Video/Audio/Ebook processing.
# -------------------------------------------------------------------------

import os
import json
import argparse
from pathlib import Path
from typing import Optional, Dict

from .config import ONIConfig
from .audio_transcriber import AudioTranscriber
from .video_vision import VideoVision
from .oni_dsp import OniDSP
from .ebook_generator import VideoToEBook

class VideoBrain:
    """
    Orquestrador principal do sistema ONI.
    Coordena todos os módulos de forma inteligente.
    """
    
    def __init__(self, config: Optional[ONIConfig] = None):
        self.config = config or ONIConfig()
        
        print("="*70)
        print("ONI V24 - UNIFIED VIDEO BRAIN")
        print("="*70)
        
        self.audio = AudioTranscriber(self.config)
        self.vision = VideoVision(self.config)
        self.dsp = OniDSP(self.config.sample_rate)
        self.ebook_converter = VideoToEBook()
    
    def process_video(
        self, 
        video_path: str,
        output_dir: Optional[str] = None,
        extract_audio: bool = True,
        extract_frames: bool = True,
        analyze_scenes: bool = True,
        generate_ebook: bool = True,
        ebook_title: Optional[str] = None
    ) -> Dict:
        """
        Pipeline completo de processamento de vídeo.
        
        Returns:
            {
                "video_info": {...},
                "transcription": {...},
                "visual_analysis": [...],
                "scenes": [...],
                "ebook_files": {...},
                "files": {...}
            }
        """
        if output_dir is None:
            video_name = Path(video_path).stem
            output_dir = os.path.join(self.config.output_dir, video_name)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"PROCESSANDO: {video_path}")
        print(f"OUTPUT: {output_dir}")
        print(f"{'='*70}\n")
        
        results = {
            "video_path": video_path,
            "output_dir": output_dir,
            "files": {}
        }
        
        # 1. INFO DO VÍDEO
        print(">>> [1/5] Obtendo informações do vídeo...")
        video_info = self.vision.get_info(video_path)
        results["video_info"] = video_info
        print(f"    Duração: {video_info['duration']:.2f}s")
        print(f"    Resolução: {video_info['width']}x{video_info['height']}")
        print(f"    FPS: {video_info['fps']:.2f}")
        
        # 2. ANÁLISE VISUAL
        if extract_frames:
            print("\n>>> [2/5] Extraindo e analisando frames...")
            frames_dir = output_path / "frames"
            frames = self.vision.extract_frames(
                video_path,
                save_dir=str(frames_dir)
            )
            
            if analyze_scenes:
                visual_analysis = self.vision.analyze_scenes(frames)
                
                # Salvar análise
                analysis_path = output_path / "visual_analysis.json"
                with open(analysis_path, 'w') as f:
                    json.dump(visual_analysis, f, indent=2)
                
                results["visual_analysis"] = visual_analysis
                results["files"]["visual_analysis"] = str(analysis_path)
                
                print(f"    {len(frames)} frames analisados")
                print(f"    Análise salva em: {analysis_path}")
        
        # 3. TRANSCRIÇÃO DE ÁUDIO
        transcription = None
        if extract_audio:
            print("\n>>> [3/5] Processando áudio...")
            
            # Extrair WAV
            audio_path = output_path / "audio.wav"
            self.audio.extract_audio(video_path, str(audio_path))
            results["files"]["audio"] = str(audio_path)
            
            # Transcrever
            transcription = self.audio.transcribe(
                str(audio_path), 
                detect_language=True
            )
            results["transcription"] = transcription
            
            # Exportar formatos
            config_files = self.audio.export_formats(transcription, str(output_path / "transcription"))
            results["files"].update(config_files)
            
            print(f"    Idioma: {transcription['language'].upper()}")
            print(f"    Confiança: {transcription['confidence']:.2%}")
            
        # 4. GERAÇÃO DE EBOOK
        if generate_ebook and transcription:
            print("\n>>> [4/5] Gerando eBook...")
            ebook_dir = output_path / "ebook"
            ebook_files = self.ebook_converter.process(
                transcription_data=transcription,
                output_dir=str(ebook_dir),
                title=ebook_title or Path(video_path).stem.replace("_", " ").title(),
                description=f"Gerado automaticamente a partir de {Path(video_path).name}"
            )
            results["ebook_files"] = ebook_files
            results["files"]["ebook"] = ebook_files

        # 5. GERAR RELATÓRIO FINAL
        print("\n>>> [5/5] Finalizando...")
        report_path = output_path / "report.json"
        
        # Limpar dados pesados antes de salvar
        clean_results = results.copy()
        if "visual_analysis" in clean_results:
            # Remover frames raw se existirem na estrutura (embora não devam estar aqui)
            pass 
            
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        results["files"]["report"] = str(report_path)
        print(f"    Relatório salvo: {report_path}")
        
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ONI Video Processor V23")
    parser.add_argument("video", help="Caminho do vídeo")
    parser.add_argument("--output", help="Diretório de saída")
    parser.add_argument("--ebook", action="store_true", help="Gerar eBook")
    parser.add_argument("--title", help="Título do eBook")
    
    args = parser.parse_args()
    
    brain = VideoBrain()
    brain.process_video(
        args.video,
        output_dir=args.output,
        generate_ebook=args.ebook,
        ebook_title=args.title
    )
