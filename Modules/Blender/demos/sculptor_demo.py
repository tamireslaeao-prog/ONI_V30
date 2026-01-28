"""
ONI SCULPTOR ENGINE DEMO
========================
Demonstrating REAL modeling capabilities vs primitive stacking.
"""
import bpy
import bmesh
import math
import sys
import os

# Add path to import sculptor
sys.path.insert(0, os.path.dirname(__file__))
from oni_sculptor_engine import ONISculptor

def clean_scene():
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

# ============================================================================
# DEMO 1: ORGANIC CREATURE (Not cubes!)
# ============================================================================
def demo_organic_creature():
    """Create an organic creature using advanced techniques."""
    sculptor = ONISculptor("OrganicCreature")
    
    # 1. Start with sphere, not cube
    sculptor.create_base_sphere(1.0, 16)
    
    # 2. Noise displacement for organic feel
    sculptor.apply_noise_displacement(frequency=2.0, amplitude=0.2)
    
    # 3. Taper to create body shape
    sculptor.taper('Z', factor=0.4)
    
    # 4. Twist for dynamic pose
    sculptor.twist('Z', angle=30)
    
    # 5. Subdivide for smoothness
    sculptor.subdivide(2)
    
    # 6. Final smooth pass
    sculptor.smooth_vertices(iterations=2, factor=0.3)
    
    obj = sculptor.finalize(location=(-3, 0, 1))
    sculptor.apply_material((0.8, 0.3, 0.2, 1), roughness=0.7)
    
    return obj

# ============================================================================
# DEMO 2: STYLIZED HEAD (Box Modeling)
# ============================================================================
def demo_stylized_head():
    """Create a head using proper box modeling techniques."""
    sculptor = ONISculptor("StylizedHead")
    
    # 1. Start with subdivided cube
    sculptor.create_base_cube(1.0, subdivisions=2)
    
    # 2. Extrude front for face area
    front_faces = sculptor.select_faces_by_normal((0, -1, 0), threshold=0.6)
    sculptor.extrude_faces(front_faces, distance=0.4, scale=0.85)
    
    # 3. Extrude again for snout/nose
    new_front = sculptor.select_faces_by_normal((0, -1, 0), threshold=0.8)
    sculptor.extrude_faces(new_front[:1] if new_front else [], distance=0.25, scale=0.6)
    
    # 4. Extrude back for head depth
    back_faces = sculptor.select_faces_by_normal((0, 1, 0), threshold=0.6)
    sculptor.extrude_faces(back_faces, distance=0.3, scale=0.9)
    
    # 5. Smooth
    sculptor.smooth_vertices(iterations=3, factor=0.5)
    
    # 6. Subdivide for final smoothness
    sculptor.subdivide(2)
    
    obj = sculptor.finalize(location=(0, 0, 1))
    sculptor.apply_material((0.9, 0.7, 0.5, 1), roughness=0.4)
    
    return obj

# ============================================================================
# DEMO 3: PROCEDURAL TERRAIN
# ============================================================================
def demo_terrain():
    """Generate procedural terrain with Perlin noise."""
    sculptor = ONISculptor("ProceduralTerrain")
    
    sculptor.generate_terrain(
        size=15.0,
        resolution=80,
        height_scale=3.0,
        noise_scale=0.4
    )
    
    obj = sculptor.finalize(location=(0, 0, -2))
    sculptor.apply_material((0.2, 0.5, 0.2, 1), roughness=0.9)
    
    return obj

# ============================================================================
# DEMO 4: VASE (Lofting from profiles)
# ============================================================================
def demo_vase():
    """Create a vase by lofting between circular profiles."""
    sculptor = ONISculptor("LoftedVase")
    
    # Define circular profiles at different heights with different radii
    profiles = []
    heights = [0, 0.3, 0.6, 1.0, 1.5, 2.0, 2.3, 2.5]
    radii = [0.5, 0.6, 0.4, 0.3, 0.35, 0.5, 0.6, 0.55]
    
    segments = 24
    for h, r in zip(heights, radii):
        profile = []
        for i in range(segments):
            angle = (i / segments) * 2 * math.pi
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            z = h
            profile.append((x, y, z))
        profiles.append(profile)
    
    sculptor.loft_profiles(profiles, closed=True)
    sculptor.smooth_vertices(2, 0.3)
    
    obj = sculptor.finalize(location=(3, 0, 0))
    sculptor.apply_material((0.7, 0.5, 0.3, 1), metallic=0.2, roughness=0.3)
    
    return obj

# ============================================================================
# DEMO 5: ROCK (Noise-based sculpting)
# ============================================================================
def demo_rock():
    """Generate organic rock shape."""
    sculptor = ONISculptor("OrganicRock")
    
    sculptor.generate_rock(size=1.0, detail=3, roughness=0.4)
    
    obj = sculptor.finalize(location=(5, 0, 0.5))
    sculptor.apply_material((0.4, 0.4, 0.4, 1), roughness=0.95)
    
    return obj

# ============================================================================
# DEMO 6: TWISTED PILLAR
# ============================================================================
def demo_twisted_pillar():
    """Create a twisted architectural pillar."""
    sculptor = ONISculptor("TwistedPillar")
    
    # Start with cylinder
    sculptor.create_base_cylinder(radius=0.4, depth=4.0, segments=16)
    
    # Add edge loops for twist detail
    sculptor.add_edge_loop(cuts=8)
    
    # Twist it
    sculptor.twist('Z', angle=180)
    
    # Taper slightly
    sculptor.taper('Z', factor=0.7)
    
    # Smooth
    sculptor.smooth_vertices(1, 0.2)
    
    obj = sculptor.finalize(location=(-5, 0, 2))
    sculptor.apply_material((0.9, 0.85, 0.7, 1), metallic=0.1, roughness=0.3)
    
    return obj

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def run_all_demos():
    """Run all demos to showcase capabilities."""
    clean_scene()
    
    print("Creating Organic Creature...")
    demo_organic_creature()
    
    print("Creating Stylized Head...")
    demo_stylized_head()
    
    print("Creating Procedural Terrain...")
    demo_terrain()
    
    print("Creating Lofted Vase...")
    demo_vase()
    
    print("Creating Organic Rock...")
    demo_rock()
    
    print("Creating Twisted Pillar...")
    demo_twisted_pillar()
    
    # Setup camera
    bpy.ops.object.camera_add(location=(10, -10, 8), rotation=(math.radians(60), 0, math.radians(45)))
    bpy.context.scene.camera = bpy.context.active_object
    
    # Add sun light
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    bpy.context.active_object.data.energy = 3
    
    print("=" * 60)
    print("ONI SCULPTOR ENGINE DEMO COMPLETE!")
    print("6 objects created using ADVANCED techniques:")
    print("  1. Organic Creature (noise + taper + twist)")
    print("  2. Stylized Head (box modeling with extrusions)")
    print("  3. Procedural Terrain (fractal noise)")
    print("  4. Lofted Vase (profile curves)")
    print("  5. Organic Rock (noise displacement)")
    print("  6. Twisted Pillar (twist + taper)")
    print("=" * 60)

# RUN
run_all_demos()
