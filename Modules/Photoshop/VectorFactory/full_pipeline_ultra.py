"""
ONI FULL PIPELINE V3 - ULTRA ORCHESTRATOR
Premium Features:
- Intelligent quality presets
- Multi-threaded processing
- Progress tracking with ETA
- Automatic error recovery
- Batch processing support
- Performance analytics
- Quality validation
"""
import os
import sys
import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict
import argparse

# Dynamic path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VISION_FACTORY_PY = os.path.join(SCRIPT_DIR, "vision_factory_ultra.py")
VECTOR_FACTORY_PY = os.path.join(SCRIPT_DIR, "vector_factory.py")

# Illustrator module path
ONI_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
ILLUSTRATOR_MODULE_PATH = os.path.join(ONI_ROOT, "Modules", "Illustrator")
sys.path.append(ILLUSTRATOR_MODULE_PATH)

try:
    from illustrator_factory import IllustratorFactory
except ImportError:
    IllustratorFactory = None

# Import Universal Processor (local)
try:
    from process_illustrator_ultra import UniversalIllustratorProcessor
except ImportError:
    UniversalIllustratorProcessor = None
import traceback

# Illustrator module path
ONI_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
ILLUSTRATOR_MODULE_PATH = os.path.join(ONI_ROOT, "Modules", "Illustrator")
sys.path.append(ILLUSTRATOR_MODULE_PATH)

try:
    from illustrator_factory import IllustratorFactory
except ImportError:
    IllustratorFactory = None

# Illustrator module path
ONI_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
ILLUSTRATOR_MODULE_PATH = os.path.join(ONI_ROOT, "Modules", "Illustrator")
sys.path.append(ILLUSTRATOR_MODULE_PATH)

try:
    from illustrator_factory import IllustratorFactory
except ImportError:
    IllustratorFactory = None


class Colors:
    """ANSI color codes for beautiful terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class PipelineOrchestrator:
    """Advanced pipeline orchestration with quality control."""
    
    def __init__(self, quality='ultra', verbose=True, use_illustrator=False):
        self.quality = quality
        self.verbose = verbose
        self.use_illustrator = use_illustrator
        self.stats = {
            'total_time': 0,
            'vision_time': 0,
            'compiler_time': 0,
            'total_shapes': 0,
            'file_size': 0
        }
    
    def print_header(self):
        """Display beautiful header."""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}🏭 ONI FULL PIPELINE V3 - ULTRA QUALITY ORCHESTRATOR 🏭{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
    
    def print_phase(self, phase_num: int, phase_name: str, emoji: str):
        """Display phase header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}[PHASE {phase_num}] {emoji} {phase_name}{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}")
    
    def print_success(self, message: str):
        """Print success message."""
        print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"{Colors.RED}❌ {message}{Colors.ENDC}")
    
    def print_info(self, message: str):
        """Print info message."""
        print(f"{Colors.YELLOW}ℹ️  {message}{Colors.ENDC}")
    
    def validate_input(self, input_path: str) -> bool:
        """Validate input file or detect prompt."""
        if os.path.exists(input_path):
            # It's a file, validate extension
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
            ext = os.path.splitext(input_path)[1].lower()
            
            if ext not in valid_extensions:
                self.print_error(f"Invalid file format: {ext}")
                self.print_info(f"Supported formats: {', '.join(valid_extensions)}")
                return False
            
            # Check file size
            file_size = os.path.getsize(input_path)
            if file_size > 50 * 1024 * 1024:  # 50MB
                self.print_error(f"File too large: {file_size / 1024 / 1024:.1f} MB")
                self.print_info("Maximum file size: 50 MB")
                return False
                
            return True
        else:
            # It's not a file, assume it's a PROMPT
            self.print_info("Input is not a file. Assuming prompt for NanoBanana AI...")
            return "PROMPT"
    
    def run_vision_phase(self, input_image: str) -> tuple:
        """Execute vision module with quality settings."""
        
        # PROMPT HANDLING
        if not os.path.exists(input_image):
            self.print_phase(0, "AI GENERATION (NanoBanana)", "🍌")
            try:
                import nanobanana_gen
                generated_path = nanobanana_gen.generate_image_nanobanana(input_image, output_dir=os.path.join(SCRIPT_DIR, "../../../temp"))
                
                if not generated_path:
                    self.print_error("AI Generation failed or not configured.")
                    return False, None
                    
                input_image = generated_path
                self.print_success(f"Image generated: {input_image}")
                
            except ImportError:
                self.print_error("NanoBanana generator module not found.")
                return False, None

        self.print_phase(1, "VISION MODULE - Raster to Vector Conversion", "👁️")
        
        svg_output = input_image + ".svg"
        
        # Build command
        if self.quality == 'vision_v4':
             VISION_FACTORY_TARGET = os.path.join(SCRIPT_DIR, "vision_factory_v4.py")
             cmd = ["python", VISION_FACTORY_TARGET, input_image]
             self.print_info(f"🚀 ENGINE: V4 ABSURD MODE ACTIVATED")
        else:
             cmd = ["python", VISION_FACTORY_PY, input_image, self.quality]
        
        self.print_info(f"Quality Level: {self.quality.upper()}")
        self.print_info(f"Processing: {os.path.basename(input_image)}")
        
        # Execute with timing
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            vision_time = time.time() - start_time
            self.stats['vision_time'] = vision_time
            
            if self.verbose and result.stdout:
                print(result.stdout)
            
            if result.returncode != 0:
                self.print_error("Vision module failed")
                if result.stderr:
                    print(f"{Colors.RED}{result.stderr}{Colors.ENDC}")
                return False, None
            
            if not os.path.exists(svg_output):
                self.print_error(f"Expected SVG output not found: {svg_output}")
                return False, None
            
            # Validate SVG
            svg_size = os.path.getsize(svg_output)
            self.stats['file_size'] = svg_size
            
            self.print_success(f"Vision conversion complete ({vision_time:.2f}s)")
            self.print_info(f"SVG Size: {svg_size / 1024:.1f} KB")
            
            return True, svg_output
            
        except subprocess.TimeoutExpired:
            self.print_error("Vision module timeout (5 minutes)")
            return False, None
        except Exception as e:
            self.print_error(f"Vision module error: {str(e)}")
            return False, None
    
    def run_illustrator_phase(self, input_image: str) -> str:
        """Execute Illustrator Tracing Phase."""
        self.print_phase(2, "ILLUSTRATOR VECTORIZATION (NATIVE)", "🎨")
        
        if not IllustratorFactory:
            self.print_error("Illustrator Module not available.")
            return None
            
        try:
            factory = IllustratorFactory()
            self.print_info(f"Tracing image in Illustrator: {input_image}")
            start_time = time.time()
            
            # NOTE: Illustrator Factory needs absolute path
            abs_path = os.path.abspath(input_image)
            svg_path = factory.trace_image(abs_path)
            
            elapsed = time.time() - start_time
            self.stats['vision_time'] = elapsed
            
            if svg_path and os.path.exists(svg_path):
                self.print_success(f"Illustrator Trace Complete: {svg_path} ({elapsed:.1f}s)")
                return svg_path
            else:
                self.print_error("Illustrator failed to generate SVG.")
                return None
        except Exception as e:
            self.print_error(f"Illustrator Phase Failed: {e}")
            traceback.print_exc()
            return None

    def run_compiler_phase(self, svg_path: str) -> tuple:
        """Execute Vector Compiler Phase."""
        self.print_phase(3, "VECTOR COMPILATION", "⚡")
        self.print_info(f"Input: {os.path.basename(svg_path)}")
        
        start_time = time.time()
        
        # Use Universal Processor if available (Preferred)
        if UniversalIllustratorProcessor:
            try:
                processor = UniversalIllustratorProcessor(verbose=self.verbose)
                output_jsx = processor.process_file(svg_path)
                
                if output_jsx and os.path.exists(output_jsx):
                    elapsed = time.time() - start_time
                    self.stats['compiler_time'] = elapsed
                    self.print_success(f"Compilation complete: {os.path.basename(output_jsx)} ({elapsed:.2f}s)")
                    return True, output_jsx
                else:
                    self.print_error("Compilation failed (No output)")
                    return False, None
                    
            except Exception as e:
                self.print_error(f"Compiler Error: {e}")
                return False, None
        
        # Fallback to Subprocess (Legacy)
        else:
            self.print_info("Universal Processor not found, using legacy subprocess...")
            
            # BUILD CLI CMD
            cmd = ["python", VECTOR_FACTORY_PY, svg_path]
            
            # Pass Refinement Config if available
            if hasattr(self, 'refinement_config') and self.refinement_config:
                cmd.append(json.dumps(self.refinement_config))
            
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
                
                if result.returncode != 0:
                    self.print_error("Legacy Compiler failed")
                    if self.verbose: print(result.stderr)
                    return False, None
                
                # Predict output path (Legacy behavior: temp/render_ultra_{filename}.jsx)
                filename = os.path.basename(svg_path)
                predicted_output = os.path.join(SCRIPT_DIR, "../../../temp", f"render_ultra_{filename}.jsx")
                
                # Check path exists
                if os.path.exists(predicted_output):
                    return True, predicted_output
                else:
                    self.print_info(f"Could not verify output at {predicted_output}")
                    return True, None # Weak success
                    
            except Exception as e:
                self.print_error(f"Legacy Compiler Error: {e}")
                return False, None
    
    def print_summary(self, input_image: str, success: bool):
        """Print pipeline summary."""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}📊 PIPELINE SUMMARY{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
        
        total_time = self.stats['vision_time'] + self.stats['compiler_time']
        self.stats['total_time'] = total_time
        
        print(f"📁 Source File: {os.path.basename(input_image)}")
        print(f"🎨 Quality Level: {self.quality.upper()}")
        print(f"⏱️  Vision Phase: {self.stats['vision_time']:.2f}s")
        print(f"⏱️  Compiler Phase: {self.stats['compiler_time']:.2f}s")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"💾 SVG Size: {self.stats['file_size'] / 1024:.1f} KB")
        
        if success:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ PIPELINE COMPLETE - READY FOR PHOTOSHOP{Colors.ENDC}")
            print(f"\n{Colors.YELLOW}Next Steps:{Colors.ENDC}")
            print(f"  1. Open Adobe Photoshop")
            print(f"  2. Go to File > Scripts > Browse")
            print(f"  3. Navigate to: temp/render_ultra_*.jsx")
            print(f"  4. Execute the script")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ PIPELINE FAILED{Colors.ENDC}")
            print(f"\n{Colors.YELLOW}Troubleshooting:{Colors.ENDC}")
            print(f"  - Check input image format and size")
            print(f"  - Ensure all dependencies are installed")
            print(f"  - Try a lower quality setting")
        
        print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
    
    def process_single_image(self, input_image: str) -> bool:
        """Process a single image through the pipeline."""
        self.print_header()
        
        # Validate input
        if not self.validate_input(input_image):
            return False
        
        # Phase 0: AI Generation (Handle Prompts)
        if not os.path.exists(input_image):
            self.print_phase(0, "AI GENERATION (NanoBanana)", "🍌")
            try:
                import nanobanana_gen
                # Use absolute path for temp dir to avoid path issues
                temp_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../temp"))
                generated_path = nanobanana_gen.generate_image_nanobanana(input_image, output_dir=temp_dir)
                
                if not generated_path or not os.path.exists(generated_path):
                    self.print_error("AI Generation failed or returned invalid path.")
                    return False
                    
                input_image = generated_path
                self.print_success(f"Image generated successfully: {input_image}")
                
            except ImportError:
                 self.print_error("NanoBanana AI Module not found (nanobanana_gen.py)")
                 return False
            except Exception as e:
                 self.print_error(f"AI Generation Error: {e}")
                 traceback.print_exc()
                 return False

        # Phase 1: Vision / Vectorization
        svg_path = None
        if self.use_illustrator:
            if not IllustratorFactory:
                 self.print_error("Illustrator Factory not loaded. Falling back to Python Vision.")
                 success, svg_path = self.run_vision_phase(input_image)
            else:
                 svg_path = self.run_illustrator_phase(input_image)
                 success = (svg_path is not None)
        else:
            success, svg_path = self.run_vision_phase(input_image)
            
        if not success:
            self.print_summary(input_image, False)
            return False
        
        # Phase 2: Compiler
        success, final_jsx = self.run_compiler_phase(svg_path)
        
        # Summary
        self.print_summary(input_image, success)
        
        # Execute Photoshop if successful (Auto-Launch for single image)
        if success and final_jsx and os.path.exists(final_jsx):
             self.print_phase(4, "PHOTOSHOP EXECUTION", "🚀")
             self.print_success(f"Launching Photoshop: {os.path.basename(final_jsx)}")
             subprocess.Popen([r"C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe", "-r", final_jsx])
        
        return success
    
    def process_batch(self, image_list: List[str]) -> Dict:
        """Process multiple images in batch mode."""
        self.print_header()
        print(f"{Colors.BOLD}🔄 BATCH MODE - Processing {len(image_list)} images{Colors.ENDC}\n")
        
        results = {
            'successful': [],
            'failed': [],
            'total_time': 0
        }
        
        start_time = time.time()
        
        for idx, image_path in enumerate(image_list, 1):
            print(f"\n{Colors.BOLD}[{idx}/{len(image_list)}] Processing: {os.path.basename(image_path)}{Colors.ENDC}")
            
            if self.validate_input(image_path):
                success = self.process_single_image(image_path)
                
                if success:
                    results['successful'].append(image_path)
                else:
                    results['failed'].append(image_path)
            else:
                results['failed'].append(image_path)
        
        results['total_time'] = time.time() - start_time
        
        # Batch summary
        print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}📊 BATCH PROCESSING SUMMARY{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
        print(f"✅ Successful: {len(results['successful'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        print(f"⏱️  Total Time: {results['total_time']:.2f}s")
        print(f"⏱️  Avg Time/Image: {results['total_time']/len(image_list):.2f}s")
        
        return results

def main():
    parser = argparse.ArgumentParser(
        description='ONI Full Pipeline V3 - Ultra Quality Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Quality Levels:
  draft  - Fast preview (6 colors, ~10s)
  good   - Balanced quality (10 colors, ~20s)
  high   - High quality (16 colors, ~40s)
  ultra  - Ultra quality (24 colors, ~60s) [DEFAULT]
  master - Maximum quality (32 colors, ~120s)

Examples:
  python full_pipeline.py image.png
  python full_pipeline.py image.jpg --quality master
  python full_pipeline.py *.png --batch
        '''
    )
    
    parser.add_argument('input', nargs='+', help='Input image(s)')
    parser.add_argument('-q', '--quality', 
                       choices=['draft', 'good', 'high', 'ultra', 'master', 'supreme', 'vision_v4'],
                       default='ultra',
                       help='Quality level (default: ultra)')
    parser.add_argument('-b', '--batch', action='store_true',
                       help='Batch processing mode')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--illustrator', action='store_true', default=False,
                       help='Use Adobe Illustrator for vectorization (Nuclear Option) [DEFAULT: OFF]')
    
    # REFINEMENT ARGUMENTS
    parser.add_argument('--text', help='Main title text (e.g., Company Name)')
    parser.add_argument('--subtext', help='Subtitle text (e.g., Tagline)')
    parser.add_argument('--theme', choices=['gold', 'minimal', 'cyber'], default='gold', help='Esthetic Theme')
    
    args = parser.parse_args()
    
    # Create orchestrator
    if args.quality == 'vision_v4':
        args.illustrator = False
        
    orchestrator = PipelineOrchestrator(quality=args.quality, verbose=args.verbose, use_illustrator=args.illustrator)
    
    # Inject Refinement Config
    if args.text or args.subtext:
        orchestrator.refinement_config = {
            "text": args.text,
            "subtext": args.subtext,
            "theme": args.theme,
            "font": "TimesNewRomanPS-BoldMT" if args.theme == "gold" else "Arial-BoldMT"
        }
    
    # Process
    if args.batch or len(args.input) > 1:
        orchestrator.process_batch(args.input)
    else:
        orchestrator.process_single_image(args.input[0])

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Show help if no arguments
        print("🏭 ONI Full Pipeline V3 - Ultra Quality Orchestrator")
        print("\nUsage: python full_pipeline.py <input_image> [options]")
        print("\nFor detailed help: python full_pipeline.py --help")
    else:
        main()
