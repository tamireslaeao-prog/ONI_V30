"""
ONI V24 Module Component
Part of the ONI Automation Framework.
Managed by The Jewel Polishing Protocol.
"""

"""
============================================================================
ONI.Gen.py - Procedural Generation Core for Blender
Version: 1.0
Description: Random generation system with reproducible seeds
============================================================================
"""

import random
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
import colorsys

# ============================================================================
# SEED MANAGEMENT
# ============================================================================

class ONISeedManager:
    """Manages random seeds for reproducible generation"""
    
    _current_seed: Optional[str] = None
    _seed_history: List[str] = []
    
    @classmethod
    def generate_seed(cls, style_prefix: str = "BLD") -> str:
        """
        Generate new ONI seed with format: ONI-{PREFIX}-{DATE}-{HASH}
        
        Args:
            style_prefix: 3-letter style identifier (e.g., CYB, BRT, MIN)
            
        Returns:
            Seed string like "ONI-BLD-20260104-A7F3"
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        random_data = f"{datetime.now().isoformat()}{random.random()}"
        hash_obj = hashlib.sha256(random_data.encode())
        hash_hex = hash_obj.hexdigest()[:4].upper()
        
        seed = f"ONI-{style_prefix}-{timestamp}-{hash_hex}"
        cls._current_seed = seed
        cls._seed_history.append(seed)
        
        return seed
    
    @classmethod
    def set_seed(cls, seed: str) -> None:
        """Set current seed and initialize random state"""
        cls._current_seed = seed
        
        # Extract hash from seed for random initialization
        parts = seed.split("-")
        if len(parts) >= 4:
            hash_part = parts[3]
            seed_int = int(hash_part, 16)
            random.seed(seed_int)
    
    @classmethod
    def get_current_seed(cls) -> Optional[str]:
        """Get current active seed"""
        return cls._current_seed
    
    @classmethod
    def get_seed_history(cls) -> List[str]:
        """Get all generated seeds in session"""
        return cls._seed_history.copy()


# ============================================================================
# COLOR GENERATION
# ============================================================================

class ONIColorGenerator:
    """Generate colors from style palettes"""
    
    def __init__(self, styles_db_path: str = "data/styles_db.json"):
        self.styles_db_path = styles_db_path
        self.styles_db = None
        self._load_styles_db()
    
    def _load_styles_db(self) -> None:
        """Load styles database from JSON"""
        try:
            with open(self.styles_db_path, 'r', encoding='utf-8') as f:
                self.styles_db = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Styles DB not found at {self.styles_db_path}")
            self.styles_db = {"styles": []}
    
    def get_random_color(self, 
                        palette: str = "cyberpunk_v1", 
                        category: str = "primary") -> str:
        """
        Get random hex color from style palette
        
        Args:
            palette: Style ID (e.g., "cyberpunk_v1")
            category: Color category ("primary", "accent", "background")
            
        Returns:
            Hex color string like "#00F0FF"
        """
        if not self.styles_db:
            return "#FFFFFF"
        
        # Find style
        style = next((s for s in self.styles_db["styles"] 
                     if s["style_id"] == palette), None)
        
        if not style:
            return "#FFFFFF"
        
        # Get colors from category
        try:
            colors = style["visual_dna"]["palette"][category]
            return random.choice(colors)
        except (KeyError, IndexError):
            return "#FFFFFF"
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[float, float, float]:
        """
        Convert hex to RGB float values (0-1) for Blender
        
        Args:
            hex_color: Hex string like "#00F0FF"
            
        Returns:
            RGB tuple (0.0-1.0, 0.0-1.0, 0.0-1.0)
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    
    def hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """Convert hex to RGBA for Blender materials"""
        r, g, b = self.hex_to_rgb(hex_color)
        return (r, g, b, alpha)
    
    def generate_gradient(self, 
                         color1: str, 
                         color2: str, 
                         steps: int = 10) -> List[Tuple[float, float, float]]:
        """Generate color gradient between two colors"""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)
        
        gradient = []
        for i in range(steps):
            t = i / (steps - 1)
            r = rgb1[0] + (rgb2[0] - rgb1[0]) * t
            g = rgb1[1] + (rgb2[1] - rgb1[1]) * t
            b = rgb1[2] + (rgb2[2] - rgb1[2]) * t
            gradient.append((r, g, b))
        
        return gradient
    
    def adjust_brightness(self, hex_color: str, factor: float) -> Tuple[float, float, float]:
        """Adjust color brightness (factor: 0.0-2.0, 1.0 = no change)"""
        r, g, b = self.hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        v = max(0.0, min(1.0, v * factor))
        return colorsys.hsv_to_rgb(h, s, v)


# ============================================================================
# GEOMETRY GENERATION
# ============================================================================

class ONIGeometryGenerator:
    """Generate random geometric values and coordinates"""
    
    @staticmethod
    def random_point_2d(x_min: float = 0, x_max: float = 10,
                       y_min: float = 0, y_max: float = 10) -> Tuple[float, float]:
        """Generate random 2D point"""
        return (random.uniform(x_min, x_max), random.uniform(y_min, y_max))
    
    @staticmethod
    def random_point_3d(x_min: float = -5, x_max: float = 5,
                       y_min: float = -5, y_max: float = 5,
                       z_min: float = 0, z_max: float = 10) -> Tuple[float, float, float]:
        """Generate random 3D point"""
        return (random.uniform(x_min, x_max), 
                random.uniform(y_min, y_max), 
                random.uniform(z_min, z_max))
    
    @staticmethod
    def random_rotation() -> Tuple[float, float, float]:
        """Generate random rotation (Euler angles in radians)"""
        import math
        return (random.uniform(0, 2 * math.pi),
                random.uniform(0, 2 * math.pi),
                random.uniform(0, 2 * math.pi))
    
    @staticmethod
    def random_scale(min_scale: float = 0.5, 
                    max_scale: float = 2.0,
                    uniform: bool = True) -> Tuple[float, float, float]:
        """Generate random scale values"""
        if uniform:
            s = random.uniform(min_scale, max_scale)
            return (s, s, s)
        else:
            return (random.uniform(min_scale, max_scale),
                   random.uniform(min_scale, max_scale),
                   random.uniform(min_scale, max_scale))
    
    @staticmethod
    def random_in_circle(radius: float = 1.0) -> Tuple[float, float]:
        """Generate random point inside circle"""
        import math
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, radius)
        return (r * math.cos(angle), r * math.sin(angle))
    
    @staticmethod
    def random_on_sphere(radius: float = 1.0) -> Tuple[float, float, float]:
        """Generate random point on sphere surface"""
        import math
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        
        x = radius * math.sin(phi) * math.cos(theta)
        y = radius * math.sin(phi) * math.sin(theta)
        z = radius * math.cos(phi)
        
        return (x, y, z)


# ============================================================================
# VARIATION GENERATION
# ============================================================================

class ONIVariationGenerator:
    """Generate variations of parameters"""
    
    @staticmethod
    def create_variations(base_params: Dict[str, Any],
                         vary_params: List[str],
                         count: int = 5,
                         variation_amount: float = 0.2) -> List[Dict[str, Any]]:
        """
        Create multiple variations of base parameters
        
        Args:
            base_params: Base parameter dictionary
            vary_params: List of parameter names to vary
            count: Number of variations to generate
            variation_amount: Amount of variation (0.0-1.0)
            
        Returns:
            List of parameter dictionaries
        """
        variations = []
        
        for i in range(count):
            var = base_params.copy()
            
            for param in vary_params:
                if param not in base_params:
                    continue
                
                value = base_params[param]
                
                if isinstance(value, (int, float)):
                    # Numeric variation
                    variation = value * variation_amount * random.uniform(-1, 1)
                    var[param] = value + variation
                
                elif isinstance(value, tuple) and len(value) == 3:
                    # 3D vector variation
                    var[param] = tuple(
                        v + v * variation_amount * random.uniform(-1, 1)
                        for v in value
                    )
            
            variations.append(var)
        
        return variations
    
    @staticmethod
    def mutate_value(value: Any, mutation_rate: float = 0.1) -> Any:
        """Mutate a single value"""
        if isinstance(value, (int, float)):
            return value * (1 + random.uniform(-mutation_rate, mutation_rate))
        elif isinstance(value, str) and value.startswith('#'):
            # Color mutation
            color_gen = ONIColorGenerator()
            rgb = color_gen.hex_to_rgb(value)
            mutated = tuple(max(0, min(1, c + random.uniform(-0.1, 0.1))) for c in rgb)
            return "#{:02x}{:02x}{:02x}".format(
                int(mutated[0] * 255),
                int(mutated[1] * 255),
                int(mutated[2] * 255)
            )
        return value


# ============================================================================
# GREEBLES GENERATION
# ============================================================================

class ONIGreeblesGenerator:
    """Generate technical details and greebles"""
    
    @staticmethod
    def generate_greebles(count: int = 20,
                         area_bounds: Tuple[float, float, float, float] = (-5, 5, -5, 5),
                         size_range: Tuple[float, float] = (0.1, 0.5)) -> List[Dict[str, Any]]:
        """
        Generate random greeble data
        
        Args:
            count: Number of greebles
            area_bounds: (x_min, x_max, y_min, y_max)
            size_range: (min_size, max_size)
            
        Returns:
            List of greeble dictionaries with position, size, type
        """
        greebles = []
        greeble_types = ["cube", "cylinder", "sphere", "cone", "torus"]
        
        for i in range(count):
            x_min, x_max, y_min, y_max = area_bounds
            
            greeble = {
                "type": random.choice(greeble_types),
                "position": (
                    random.uniform(x_min, x_max),
                    random.uniform(y_min, y_max),
                    random.uniform(0, 1)
                ),
                "size": random.uniform(*size_range),
                "rotation": ONIGeometryGenerator.random_rotation(),
                "color_variant": random.random()
            }
            
            greebles.append(greeble)
        
        return greebles


# ============================================================================
# GLITCH EFFECTS
# ============================================================================

class ONIGlitchGenerator:
    """Generate glitch effect parameters"""
    
    @staticmethod
    def chromatic_aberration(intensity: float = 0.5) -> Dict[str, float]:
        """Generate chromatic aberration parameters"""
        return {
            "red_offset": random.uniform(-intensity, intensity),
            "green_offset": random.uniform(-intensity, intensity),
            "blue_offset": random.uniform(-intensity, intensity),
            "intensity": intensity
        }
    
    @staticmethod
    def displacement(intensity: float = 0.5) -> Dict[str, Any]:
        """Generate displacement parameters"""
        return {
            "strength": random.uniform(0, intensity),
            "scale": random.uniform(1, 10),
            "direction": random.choice(["horizontal", "vertical", "diagonal"])
        }
    
    @staticmethod
    def noise_overlay(intensity: float = 0.3) -> Dict[str, float]:
        """Generate noise overlay parameters"""
        return {
            "intensity": intensity,
            "scale": random.uniform(10, 100),
            "seed": random.randint(0, 9999)
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def test_randomness(iterations: int = 10000) -> Dict[str, Any]:
    """Test random distribution quality"""
    values = [random.random() for _ in range(iterations)]
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    
    # Test uniform distribution (should be close to 0.5)
    quartiles = [sum(1 for v in values if i * 0.25 <= v < (i + 1) * 0.25) 
                 for i in range(4)]
    
    return {
        "mean": mean,
        "variance": variance,
        "std_dev": variance ** 0.5,
        "quartiles": quartiles,
        "expected_per_quartile": iterations // 4
    }


def get_random_choice(items: List[Any]) -> Any:
    """Get random item from list"""
    return random.choice(items) if items else None


def get_random_weighted(items: List[Any], weights: List[float]) -> Any:
    """Get random item with weighted probability"""
    return random.choices(items, weights=weights, k=1)[0]


# ============================================================================
# MAIN API EXPORTS
# ============================================================================

# Global instances
seed_manager = ONISeedManager()
color_gen = ONIColorGenerator()
geometry_gen = ONIGeometryGenerator()
variation_gen = ONIVariationGenerator()
greebles_gen = ONIGreeblesGenerator()
glitch_gen = ONIGlitchGenerator()

# Convenience functions
def new_seed(prefix: str = "BLD") -> str:
    """Generate new seed"""
    return seed_manager.generate_seed(prefix)

def set_seed(seed: str) -> None:
    """Set current seed"""
    seed_manager.set_seed(seed)

def random_color(palette: str = "cyberpunk_v1", category: str = "primary") -> str:
    """Get random color"""
    return color_gen.get_random_color(palette, category)

def random_point_3d(**kwargs) -> Tuple[float, float, float]:
    """Get random 3D point"""
    return geometry_gen.random_point_3d(**kwargs)

def create_variations(base: Dict, vary: List[str], count: int = 5) -> List[Dict]:
    """Create parameter variations"""
    return variation_gen.create_variations(base, vary, count)


if __name__ == "__main__":
    # Test the system
    print("=== ONI.Gen.py Test ===")
    
    # Test seed generation
    seed = new_seed("TEST")
    print(f"Generated seed: {seed}")
    
    # Test color generation
    color = random_color("cyberpunk_v1", "primary")
    print(f"Random color: {color}")
    
    # Test 3D point
    point = random_point_3d()
    print(f"Random 3D point: {point}")
    
    # Test randomness
    stats = test_randomness(1000)
    print(f"Randomness test - Mean: {stats['mean']:.3f}, Std Dev: {stats['std_dev']:.3f}")
    
    print("\n✓ ONI.Gen.py loaded successfully!")

