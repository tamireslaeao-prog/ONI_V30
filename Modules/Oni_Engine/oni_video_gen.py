import subprocess
import os

class OniVideoGen:
    """
    ONI Video Generation Engine (Level 2).
    Wraps FFmpeg complexity into a clean Python API.
    """
    
    def __init__(self, width=1280, height=720, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.ffmpeg_path = r"c:\Users\user\Desktop\ONI V22\data\bin\ffmpeg\bin\ffmpeg.exe"
        self.inputs = []
        self.filter_chain = []
        
    def add_input(self, file_path):
        """Adds an asset (image/video/audio) to the pipeline."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Asset not found: {file_path}")
        self.inputs.append(file_path)
        return len(self.inputs) - 1 # Return index
        
    def add_solid_color(self, color="black", duration=5, alias="bg"):
        """Generates a solid color background."""
        # This is a virtual input, treated as a filter source
        f = f"color=c={color}:s={self.width}x{self.height}:d={duration}[{alias}]"
        self.filter_chain.append(f)
        return alias

    def draw_box(self, input_alias, x, y, w, h, color, output_alias):
        """Draws a rectangle."""
        f = f"[{input_alias}]drawbox=x={x}:y={y}:w={w}:h={h}:color={color}:t=fill[{output_alias}]"
        self.filter_chain.append(f)
        
    def draw_text(self, input_alias, text, x, y, font_size=24, color="white", output_alias="out_txt"):
        """Draws text (using internal font)."""
        # Local Font Strategy: Copy to temp to avoid Path Escaping Hell
        temp_dir = os.path.dirname(self.ffmpeg_path) # or just use ./temp relative if CWD is correct
        # Better: Use CWD since we run scripts from root
        font_source = r"C:\Windows\Fonts\consola.ttf"
        font_dest = "consola.ttf" # Relative path
        
        if not os.path.exists(font_dest):
            import shutil
            try:
                shutil.copy(font_source, font_dest)
            except:
                pass # Already there or perm error
        
        # Use single quotes for text to allow spaces
        f = f"[{input_alias}]drawtext=fontfile='{font_dest}':text='{text}':fontsize={font_size}:fontcolor={color}:x={x}:y={y}[{output_alias}]"
        self.filter_chain.append(f)

    def render(self, output_path, map_video_alias, audio_input_index=None):
        """Compiles the filter graph and renders the video."""
        cmd = [self.ffmpeg_path, "-y"]
        
        # Add real file inputs
        for inp in self.inputs:
            cmd.extend(["-i", inp])
            
        # Build Filter Complex
        full_graph = ";".join(self.filter_chain)
        cmd.extend(["-filter_complex", full_graph])
        
        # Map Video Output
        cmd.extend(["-map", f"[{map_video_alias}]"])
        
        # Map Audio if present
        if audio_input_index is not None:
            cmd.extend(["-map", f"{audio_input_index}:a"])
            # Ensure audio codec is good
            cmd.extend(["-c:a", "libmp3lame" if output_path.endswith(".mp3") else "aac"])
        
        # Video settings
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p"])
        
        # Shortest to cut to audio length usually
        cmd.extend(["-shortest", output_path])
        
        print(f"ONI VIDEO: Rendering to {output_path}...")
        # print("DEBUG CMD:", " ".join(cmd))
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("ERROR IN RENDER:")
            print(result.stderr.decode("utf-8"))
            raise RuntimeError("FFmpeg Render Failed")
            
        print("Render Complete.")

# Self Test
if __name__ == "__main__":
    vg = OniVideoGen()
    print("ONI Video Engine Initialized.")
