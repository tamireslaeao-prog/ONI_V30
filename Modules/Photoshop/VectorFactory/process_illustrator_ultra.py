"""
ONI ILLUSTRATOR PROCESSOR V3 - UNIVERSAL EDITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Advanced Features:
- SVG parsing (native Illustrator export)
- EPS conversion (Illustrator files)
- AI file support (Adobe Illustrator)
- PDF vector extraction
- Multi-format detection
- Automatic format conversion
- Metadata preservation
- Layer structure analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, List
import xml.etree.ElementTree as ET

# ═══════════════════════════════════════════════════════════════════════
# PATH RESOLUTION
# ═══════════════════════════════════════════════════════════════════════

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))

if root_dir not in sys.path:
    sys.path.append(root_dir)

# ═══════════════════════════════════════════════════════════════════════
# DYNAMIC MODULE LOADING
# ═══════════════════════════════════════════════════════════════════════

def load_vector_factory():
    """Dynamically load the UltraVectorCompiler class."""
    import importlib.util
    
    module_path = os.path.join(root_dir, "Modules/Photoshop/VectorFactory/vector_factory_ultra.py")
    
    if not os.path.exists(module_path):
        # Fallback to local directory
        module_path = os.path.join(current_dir, "vector_factory.py")
    
    spec = importlib.util.spec_from_file_location("vector_factory_ultra", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["vector_factory_ultra"] = module
    spec.loader.exec_module(module)
    
    if hasattr(module, 'UltraVectorCompiler'):
        return module.UltraVectorCompiler
    else:
        available = [x for x in dir(module) if isinstance(getattr(module, x), type)]
        raise ImportError(f"UltraVectorCompiler not found. Available: {available}")

# ═══════════════════════════════════════════════════════════════════════
# ANSI COLORS
# ═══════════════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ═══════════════════════════════════════════════════════════════════════
# FORMAT DETECTION
# ═══════════════════════════════════════════════════════════════════════

class FormatDetector:
    """Intelligent file format detection."""
    
    SUPPORTED_FORMATS = {
        '.svg': 'SVG (Scalable Vector Graphics)',
        '.eps': 'EPS (Encapsulated PostScript)',
        '.ai': 'AI (Adobe Illustrator)',
        '.pdf': 'PDF (Portable Document Format)',
        '.svgz': 'SVGZ (Compressed SVG)'
    }
    
    @staticmethod
    def detect_format(file_path: str) -> Dict[str, any]:
        """Detect file format and characteristics."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = path.suffix.lower()
        
        result = {
            'path': str(path),
            'extension': ext,
            'format_name': FormatDetector.SUPPORTED_FORMATS.get(ext, 'Unknown'),
            'is_vector': ext in FormatDetector.SUPPORTED_FORMATS,
            'needs_conversion': ext in ['.eps', '.ai', '.pdf', '.svgz'],
            'file_size': path.stat().st_size,
            'filename': path.name
        }
        
        # Additional analysis
        if ext == '.svg':
            result['is_illustrator_svg'] = FormatDetector._is_illustrator_svg(file_path)
        
        return result
    
    @staticmethod
    def _is_illustrator_svg(svg_path: str) -> bool:
        """Check if SVG was created by Adobe Illustrator."""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Check for Illustrator-specific metadata
            svg_content = ET.tostring(root, encoding='unicode')
            
            illustrator_markers = [
                'Adobe Illustrator',
                'illustrator:',
                'xmlns:illustrator',
                'Creator: Adobe Illustrator'
            ]
            
            return any(marker in svg_content for marker in illustrator_markers)
            
        except:
            return False

# ═══════════════════════════════════════════════════════════════════════
# EPS CONVERTER
# ═══════════════════════════════════════════════════════════════════════

class EPSConverter:
    """Convert EPS/AI/PDF to SVG using multiple fallback methods."""
    
    @staticmethod
    def convert_to_svg(input_path: str, output_path: Optional[str] = None) -> str:
        """Convert EPS/AI/PDF to SVG using best available method."""
        
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.svg'))
        
        print(f"{Colors.YELLOW}🔄 Converting to SVG format...{Colors.ENDC}")
        
        # Try methods in order of preference
        methods = [
            EPSConverter._convert_with_inkscape,
            EPSConverter._convert_with_imagemagick,
            EPSConverter._convert_with_ghostscript,
            EPSConverter._convert_with_cairosvg
        ]
        
        for method in methods:
            try:
                if method(input_path, output_path):
                    print(f"{Colors.GREEN}✅ Conversion successful!{Colors.ENDC}")
                    return output_path
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Method failed: {e}{Colors.ENDC}")
                continue
        
        raise RuntimeError("All conversion methods failed. Please install: inkscape, imagemagick, ghostscript, or cairosvg")
    
    @staticmethod
    def _convert_with_inkscape(input_path: str, output_path: str) -> bool:
        """Convert using Inkscape (best quality)."""
        print(f"{Colors.CYAN}  Trying: Inkscape...{Colors.ENDC}")
        
        # Try different Inkscape command variants
        commands = [
            ['inkscape', input_path, '--export-plain-svg', output_path],
            ['inkscape', '--export-filename=' + output_path, '--export-type=svg', input_path],
            ['inkscape', '-o', output_path, input_path]
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60
                )
                if result.returncode == 0 and os.path.exists(output_path):
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return False
    
    @staticmethod
    def _convert_with_imagemagick(input_path: str, output_path: str) -> bool:
        """Convert using ImageMagick."""
        print(f"{Colors.CYAN}  Trying: ImageMagick...{Colors.ENDC}")
        
        try:
            result = subprocess.run(
                ['convert', input_path, output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )
            return result.returncode == 0 and os.path.exists(output_path)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def _convert_with_ghostscript(input_path: str, output_path: str) -> bool:
        """Convert using Ghostscript (for EPS/PDF)."""
        print(f"{Colors.CYAN}  Trying: Ghostscript...{Colors.ENDC}")
        
        # First convert to high-res PNG, then to SVG
        temp_png = tempfile.mktemp(suffix='.png')
        
        try:
            # EPS/PDF → PNG
            result = subprocess.run(
                [
                    'gs',
                    '-dNOPAUSE',
                    '-dBATCH',
                    '-sDEVICE=png16m',
                    '-r300',
                    f'-sOutputFile={temp_png}',
                    input_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(temp_png):
                # PNG → SVG using potrace
                result2 = subprocess.run(
                    ['potrace', '-s', '-o', output_path, temp_png],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30
                )
                
                return result2.returncode == 0 and os.path.exists(output_path)
            
            return False
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
        finally:
            if os.path.exists(temp_png):
                os.remove(temp_png)
    
    @staticmethod
    def _convert_with_cairosvg(input_path: str, output_path: str) -> bool:
        """Convert using CairoSVG (Python library)."""
        print(f"{Colors.CYAN}  Trying: CairoSVG...{Colors.ENDC}")
        
        try:
            import cairosvg
            
            # Read input
            with open(input_path, 'rb') as f:
                content = f.read()
            
            # Convert
            svg_content = cairosvg.svg2svg(bytestring=content)
            
            # Write output
            with open(output_path, 'wb') as f:
                f.write(svg_content)
            
            return os.path.exists(output_path)
            
        except ImportError:
            return False
        except Exception:
            return False

# ═══════════════════════════════════════════════════════════════════════
# ILLUSTRATOR METADATA EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════

class IllustratorAnalyzer:
    """Extract metadata from Illustrator files."""
    
    @staticmethod
    def analyze_svg(svg_path: str) -> Dict[str, any]:
        """Analyze Illustrator SVG structure."""
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            
            # Count elements
            paths = len(list(root.iter('{http://www.w3.org/2000/svg}path')))
            groups = len(list(root.iter('{http://www.w3.org/2000/svg}g')))
            
            # Get dimensions
            width = root.get('width', 'unknown')
            height = root.get('height', 'unknown')
            
            # Check for layers
            layers = []
            for g in root.iter('{http://www.w3.org/2000/svg}g'):
                layer_name = g.get('{http://www.w3.org/2000/svg}id') or g.get('id')
                if layer_name:
                    layers.append(layer_name)
            
            return {
                'paths': paths,
                'groups': groups,
                'layers': layers[:10],  # First 10 layers
                'dimensions': f"{width}x{height}",
                'total_layers': len(layers)
            }
            
        except Exception as e:
            return {'error': str(e)}

# ═══════════════════════════════════════════════════════════════════════
# MAIN PROCESSOR
# ═══════════════════════════════════════════════════════════════════════

class UniversalIllustratorProcessor:
    """Universal processor for Illustrator files."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.vector_factory = None
    
    def print_header(self):
        """Print beautiful header."""
        print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}🎨 ONI ILLUSTRATOR PROCESSOR V3 - UNIVERSAL EDITION 🎨{Colors.ENDC}")
        print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
    
    def print_info(self, message: str):
        """Print info message."""
        if self.verbose:
            print(f"{Colors.YELLOW}ℹ️  {message}{Colors.ENDC}")
    
    def print_success(self, message: str):
        """Print success message."""
        print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"{Colors.RED}❌ {message}{Colors.ENDC}")
    
    def process_file(self, input_path: str, output_jsx: Optional[str] = None) -> str:
        """Process any supported vector format."""
        
        self.print_header()
        
        # 1. DETECT FORMAT
        print(f"{Colors.BOLD}[STEP 1] FORMAT DETECTION{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}")
        
        format_info = FormatDetector.detect_format(input_path)
        
        print(f"📁 File: {format_info['filename']}")
        print(f"📐 Format: {format_info['format_name']}")
        print(f"💾 Size: {format_info['file_size'] / 1024:.1f} KB")
        
        if not format_info['is_vector']:
            self.print_error(f"Unsupported format: {format_info['extension']}")
            self.print_info(f"Supported: {', '.join(FormatDetector.SUPPORTED_FORMATS.keys())}")
            return None
        
        # 2. CONVERT IF NEEDED
        svg_path = input_path
        
        if format_info['needs_conversion']:
            print(f"\n{Colors.BOLD}[STEP 2] FORMAT CONVERSION{Colors.ENDC}")
            print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}")
            
            try:
                svg_path = EPSConverter.convert_to_svg(input_path)
                self.print_success(f"Converted to SVG: {svg_path}")
            except Exception as e:
                self.print_error(f"Conversion failed: {e}")
                return None
        else:
            print(f"\n{Colors.BOLD}[STEP 2] FORMAT CONVERSION{Colors.ENDC}")
            print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}")
            self.print_info("File is already SVG, skipping conversion")
        
        # 3. ANALYZE STRUCTURE
        print(f"\n{Colors.BOLD}[STEP 3] STRUCTURE ANALYSIS{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}")
        
        analysis = IllustratorAnalyzer.analyze_svg(svg_path)
        
        if 'error' not in analysis:
            print(f"📊 Vector Paths: {analysis['paths']}")
            print(f"📦 Groups: {analysis['groups']}")
            print(f"🎨 Total Layers: {analysis['total_layers']}")
            print(f"📐 Canvas: {analysis['dimensions']}")
            
            if analysis['layers']:
                print(f"🏷️  Sample Layers: {', '.join(analysis['layers'][:5])}")
        
        # 4. COMPILE TO JSX
        print(f"\n{Colors.BOLD}[STEP 4] JSX COMPILATION{Colors.ENDC}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}")
        
        try:
            # Load vector factory
            if self.vector_factory is None:
                VectorFactoryClass = load_vector_factory()
                self.vector_factory = VectorFactoryClass()
            
            # Compile
            output_path = self.vector_factory.compile_to_jsx(svg_path)
            
            self.print_success(f"JSX Generated: {output_path}")
            
            # 5. SUMMARY
            print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
            print(f"{Colors.BOLD}📊 PROCESSING SUMMARY{Colors.ENDC}")
            print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
            
            print(f"📁 Source: {format_info['filename']}")
            print(f"📐 Format: {format_info['format_name']}")
            print(f"🎨 Paths: {analysis.get('paths', 'N/A')}")
            print(f"💾 Output: {os.path.basename(output_path)}")
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ PROCESSING COMPLETE{Colors.ENDC}")
            print(f"\n{Colors.YELLOW}Next Steps:{Colors.ENDC}")
            print(f"  1. Open Adobe Photoshop")
            print(f"  2. File → Scripts → Browse")
            print(f"  3. Select: {output_path}")
            print(f"  4. Run the script")
            
            print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
            
            return output_path
            
        except Exception as e:
            self.print_error(f"Compilation failed: {e}")
            import traceback
            if self.verbose:
                traceback.print_exc()
            return None

# ═══════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='ONI Illustrator Processor V3 - Universal Vector Converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Supported Formats:
  .svg   - Scalable Vector Graphics (native)
  .eps   - Encapsulated PostScript (requires conversion)
  .ai    - Adobe Illustrator (requires conversion)
  .pdf   - PDF with vectors (requires conversion)
  .svgz  - Compressed SVG (requires conversion)

Conversion Tools (install at least one):
  - Inkscape (recommended): https://inkscape.org
  - ImageMagick: https://imagemagick.org
  - Ghostscript: https://www.ghostscript.com
  - CairoSVG: pip install cairosvg

Examples:
  python process_illustrator_svg.py logo.svg
  python process_illustrator_svg.py design.eps
  python process_illustrator_svg.py artwork.ai --verbose
  python process_illustrator_svg.py file.pdf -o custom_output.jsx
        '''
    )
    
    parser.add_argument('input', help='Input vector file (SVG, EPS, AI, PDF)')
    parser.add_argument('-o', '--output', help='Output JSX file path (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (minimal output)')
    
    args = parser.parse_args()
    
    # Create processor
    processor = UniversalIllustratorProcessor(verbose=not args.quiet)
    
    # Process file
    result = processor.process_file(args.input, args.output)
    
    # Exit code
    sys.exit(0 if result else 1)

# ═══════════════════════════════════════════════════════════════════════
# LEGACY SUPPORT
# ═══════════════════════════════════════════════════════════════════════

def run_svg_to_jsx(svg_path):
    """Legacy function for backward compatibility."""
    processor = UniversalIllustratorProcessor(verbose=True)
    return processor.process_file(svg_path)

# ═══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"{Colors.CYAN}🎨 ONI Illustrator Processor V3 - Universal Edition{Colors.ENDC}")
        print("\nUsage: python process_illustrator_svg.py <input_file> [options]")
        print("\nSupported formats: SVG, EPS, AI, PDF, SVGZ")
        print("For detailed help: python process_illustrator_svg.py --help")
        sys.exit(0)
    
    main()
