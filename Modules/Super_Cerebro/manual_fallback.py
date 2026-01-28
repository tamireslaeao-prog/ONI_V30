
import os
import sys
from pytubefix import YouTube as PyTubeFix
import brain_core

def force_learn(url):
    print(f"🚀 MANUAL FALLBACK LEARN: {url}")
    
    # 1. Download Video using PyTubeFix directly
    try:
        print("   📦 Tentando pytubefix directly...")
        yt = PyTubeFix(url)
        titulo = yt.title
        print(f"   Vide Title: {titulo}")
        
        info = {
            'id': url.split("v=")[-1].split("&")[0],
            'original_url': url
        }
        
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'estudos_temporario', 'temp_video.mp4')
        
        # Download stream
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first()
        if not stream:
            stream = yt.streams.filter(file_extension='mp4').first()
            
        if stream:
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            stream.download(output_path=output_dir, filename='temp_video.mp4')
            print("   ✅ pytubefix: Download Sucesso!")
            
            # Setup metadata
            desc = yt.description or ''
            canal = yt.author or 'Desconhecido'
            dur = yt.length
            views = yt.views or 0
            
            # 2. Setup Directory
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estudos_temporario")
            pasta = os.path.join(base_dir, brain_core.sanitizar_nome(titulo))
            os.makedirs(pasta, exist_ok=True)
            
            # 3. Subtitles & Frames (using brain_core)
            brain_core.baixar_legendas(url, pasta, titulo, desc, canal, dur, views)
            brain_core.extrair_frames(output_path, pasta)
            
            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)
                
            print(f"\n✅ SUCESSO! Conteúdo em: {pasta}")
            
        else:
            print("❌ Falha: Nenhum stream encontrado.")

    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    force_learn("https://www.youtube.com/watch?v=4haAdmHqGOw")
