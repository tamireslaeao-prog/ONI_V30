"""
Sistema de Controle Total Chaos V-Ray 7.10.01 para Blender
Configurações de qualidade extrema para renders fotorrealistas
RODE ESTE SCRIPT DENTRO DO BLENDER
"""

import bpy
from mathutils import Vector, Color
import os
import math
import json
from typing import Dict, List, Tuple, Any, Optional


class VRayBlenderController:
    """Controlador completo do V-Ray 7.10.01 para Blender"""
    
    def __init__(self):
        self.scene = bpy.context.scene
        self.vray = None
        self.materials = {}
        self.lights = {}
        
    def initialize(self) -> bool:
        """Inicializa V-Ray e configurações"""
        try:
            # Define V-Ray como render engine
            self.scene.render.engine = 'VRAY_RENDER'
            self.vray = self.scene.vray
            
            print("✓ Chaos V-Ray 7.10.01 inicializado")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao inicializar V-Ray: {e}")
            print("NOTA: Certifique-se de que V-Ray 7.10.01 está instalado")
            return False
    
    # ==================== QUALIDADE EXTREMA - PRESETS ====================
    
    def set_ultra_quality(self):
        """Configuração ULTRA - Qualidade máxima fotorrealista"""
        print("\n=== CONFIGURANDO QUALIDADE ULTRA ===\n")
        
        # Image Sampler
        self.vray.SettingsImageSampler.type = 'PROGRESSIVE'
        self.vray.SettingsImageSampler.progressive_minSubdivs = 1
        self.vray.SettingsImageSampler.progressive_maxSubdivs = 100
        self.vray.SettingsImageSampler.progressive_threshold = 0.001
        
        # DMC Sampler
        self.vray.SettingsDMCSampler.adaptive_amount = 0.95
        self.vray.SettingsDMCSampler.adaptive_threshold = 0.001
        self.vray.SettingsDMCSampler.adaptive_min_samples = 16
        self.vray.SettingsDMCSampler.noise_threshold = 0.001
        
        # Global Illumination
        self.vray.SettingsGI.on = True
        self.vray.SettingsGI.primary_engine = 'BRUTE_FORCE'
        self.vray.SettingsGI.primary_multiplier = 1.0
        self.vray.SettingsGI.secondary_engine = 'LIGHT_CACHE'
        self.vray.SettingsGI.secondary_multiplier = 1.0
        
        # Brute Force settings
        self.vray.SettingsGI.BruteForce_subdivs = 1000
        
        # Light Cache settings
        self.vray.SettingsLightCache.subdivs = 3000
        self.vray.SettingsLightCache.sample_size = 0.005
        self.vray.SettingsLightCache.num_passes = 8
        self.vray.SettingsLightCache.filter_type = 'NEAREST'
        self.vray.SettingsLightCache.interp_samples = 50
        
        # Irradiance Map (alternativa)
        self.vray.SettingsIrradianceMap.min_rate = -4
        self.vray.SettingsIrradianceMap.max_rate = 0
        self.vray.SettingsIrradianceMap.subdivs = 200
        self.vray.SettingsIrradianceMap.interp_samples = 100
        
        # Caustics
        self.vray.SettingsCaustics.on = True
        self.vray.SettingsCaustics.multiplier = 1.0
        self.vray.SettingsCaustics.subdivs = 5000
        self.vray.SettingsCaustics.search_distance = 0.1
        self.vray.SettingsCaustics.max_photons = 100
        
        # Ray Tracer
        self.vray.SettingsRaycaster.maxDepth = 20
        self.vray.SettingsRaycaster.cutoff_threshold = 0.001
        
        # Color Mapping
        self.vray.SettingsColorMapping.type = 'REINHARD'
        self.vray.SettingsColorMapping.gamma = 2.2
        self.vray.SettingsColorMapping.dark_mult = 1.0
        self.vray.SettingsColorMapping.bright_mult = 1.0
        
        # Anti-Aliasing Filter
        self.vray.SettingsImageSampler.filter_type = 'CATMULL_ROM'
        self.vray.SettingsImageSampler.filter_size = 3.0
        
        # System
        self.vray.SettingsOptions.light_tree = True
        self.vray.SettingsOptions.probabilistic_lights = True
        
        # Resolution
        self.scene.render.resolution_x = 4096
        self.scene.render.resolution_y = 4096
        self.scene.render.resolution_percentage = 100
        
        print("✓ Qualidade ULTRA configurada")
        print("  • Progressive: 100 subdivisões")
        print("  • GI Primary: Brute Force (1000 subdivisões)")
        print("  • GI Secondary: Light Cache (3000 subdivisões)")
        print("  • Caustics: 5000 subdivisões")
        print("  • Max Depth: 20 bounces")
        print("  • Resolução: 4K")
    
    def set_production_quality(self):
        """Configuração PRODUCTION - Alta qualidade balanceada"""
        print("\n=== CONFIGURANDO QUALIDADE PRODUCTION ===\n")
        
        # Image Sampler
        self.vray.SettingsImageSampler.type = 'PROGRESSIVE'
        self.vray.SettingsImageSampler.progressive_minSubdivs = 1
        self.vray.SettingsImageSampler.progressive_maxSubdivs = 32
        self.vray.SettingsImageSampler.progressive_threshold = 0.005
        
        # DMC
        self.vray.SettingsDMCSampler.adaptive_amount = 0.85
        self.vray.SettingsDMCSampler.adaptive_threshold = 0.01
        self.vray.SettingsDMCSampler.noise_threshold = 0.005
        
        # GI
        self.vray.SettingsGI.on = True
        self.vray.SettingsGI.primary_engine = 'IRRADIANCE_MAP'
        self.vray.SettingsGI.secondary_engine = 'LIGHT_CACHE'
        
        # Irradiance Map
        self.vray.SettingsIrradianceMap.min_rate = -3
        self.vray.SettingsIrradianceMap.max_rate = 0
        self.vray.SettingsIrradianceMap.subdivs = 100
        self.vray.SettingsIrradianceMap.interp_samples = 50
        
        # Light Cache
        self.vray.SettingsLightCache.subdivs = 1500
        self.vray.SettingsLightCache.sample_size = 0.01
        
        # Caustics
        self.vray.SettingsCaustics.on = True
        self.vray.SettingsCaustics.subdivs = 2000
        
        # Ray Tracer
        self.vray.SettingsRaycaster.maxDepth = 12
        
        # Resolution
        self.scene.render.resolution_x = 1920
        self.scene.render.resolution_y = 1080
        
        print("✓ Qualidade PRODUCTION configurada")
    
    def set_preview_quality(self):
        """Configuração PREVIEW - Rápido para testes"""
        print("\n=== CONFIGURANDO QUALIDADE PREVIEW ===\n")
        
        # Image Sampler
        self.vray.SettingsImageSampler.type = 'PROGRESSIVE'
        self.vray.SettingsImageSampler.progressive_minSubdivs = 1
        self.vray.SettingsImageSampler.progressive_maxSubdivs = 4
        self.vray.SettingsImageSampler.progressive_threshold = 0.05
        
        # GI
        self.vray.SettingsGI.on = True
        self.vray.SettingsGI.primary_engine = 'IRRADIANCE_MAP'
        self.vray.SettingsIrradianceMap.min_rate = -5
        self.vray.SettingsIrradianceMap.max_rate = -3
        self.vray.SettingsIrradianceMap.subdivs = 30
        
        self.vray.SettingsGI.secondary_engine = 'LIGHT_CACHE'
        self.vray.SettingsLightCache.subdivs = 500
        
        # Caustics OFF
        self.vray.SettingsCaustics.on = False
        
        # Resolution
        self.scene.render.resolution_x = 960
        self.scene.render.resolution_y = 540
        
        print("✓ Qualidade PREVIEW configurada")
    
    # ==================== CONFIGURAÇÕES AVANÇADAS ====================
    
    def set_render_resolution(self, width: int, height: int):
        """Define resolução de render"""
        self.scene.render.resolution_x = width
        self.scene.render.resolution_y = height
        self.scene.render.resolution_percentage = 100
        print(f"✓ Resolução: {width}x{height}")
    
    def enable_denoiser(self, type: str = "nvidia", strength: float = 1.0):
        """Ativa denoiser"""
        try:
            self.vray.SettingsDenoiser.enabled = True
            
            if type == "nvidia":
                self.vray.SettingsDenoiser.type = 'NVIDIA_AI'
            elif type == "vray":
                self.vray.SettingsDenoiser.type = 'VRAY'
            elif type == "intel":
                self.vray.SettingsDenoiser.type = 'INTEL_OIDN'
            
            self.vray.SettingsDenoiser.strength = strength
            self.vray.SettingsDenoiser.radius = 10
            
            print(f"✓ Denoiser {type.upper()} ativado (strength: {strength})")
            
        except Exception as e:
            print(f"✗ Erro ao ativar denoiser: {e}")
    
    def set_gi_engines(self, primary: str = "brute_force", 
                      secondary: str = "light_cache"):
        """Define engines de GI"""
        engines = {
            'irradiance_map': 'IRRADIANCE_MAP',
            'brute_force': 'BRUTE_FORCE',
            'photon_map': 'PHOTON_MAP',
            'light_cache': 'LIGHT_CACHE',
            'none': 'NONE'
        }
        
        self.vray.SettingsGI.primary_engine = engines.get(primary, 'BRUTE_FORCE')
        self.vray.SettingsGI.secondary_engine = engines.get(secondary, 'LIGHT_CACHE')
        
        print(f"✓ GI Primary: {primary}, Secondary: {secondary}")
    
    def set_dof(self, camera_obj: Any, enabled: bool = True,
               focus_distance: float = 10.0, aperture: float = 5.6,
               blades: int = 6):
        """Configura Depth of Field"""
        if camera_obj and camera_obj.type == 'CAMERA':
            camera_obj.data.dof.use_dof = enabled
            
            if enabled:
                camera_obj.data.dof.focus_distance = focus_distance
                camera_obj.data.dof.aperture_fstop = aperture
                camera_obj.data.dof.aperture_blades = blades
                
                # V-Ray DOF settings
                self.vray.CameraPhysical.use = True
                self.vray.CameraPhysical.f_number = aperture
                self.vray.CameraPhysical.lens_shift = 0.0
                self.vray.CameraPhysical.subdivs = 100
                
                print(f"✓ DOF ativado: f/{aperture}, focus: {focus_distance}m")
        else:
            print("✗ Objeto não é uma câmera")
    
    def set_motion_blur(self, enabled: bool = True, duration: float = 0.5,
                       samples: int = 16):
        """Configura Motion Blur"""
        self.vray.SettingsMotionBlur.on = enabled
        
        if enabled:
            self.vray.SettingsMotionBlur.duration = duration
            self.vray.SettingsMotionBlur.subdivs = samples
            self.vray.SettingsMotionBlur.geom_samples = samples
            
            print(f"✓ Motion Blur: {duration} duration, {samples} samples")
        else:
            print("✓ Motion Blur desativado")
    
    def set_displacement(self, enabled: bool = True, quality: str = "high"):
        """Configura Displacement global"""
        self.vray.SettingsOptions.displacement = enabled
        
        if enabled:
            if quality == "ultra":
                self.vray.SettingsOptions.displacement_amount = 1.0
                self.vray.SettingsOptions.displacement_edge_length = 0.5
            elif quality == "high":
                self.vray.SettingsOptions.displacement_edge_length = 1.0
            else:
                self.vray.SettingsOptions.displacement_edge_length = 2.0
            
            print(f"✓ Displacement: qualidade {quality}")
    
    # ==================== MATERIAIS VRAY ====================
    
    def create_vray_material(self, name: str = "VRayMtl",
                            color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
                            roughness: float = 0.3,
                            metalness: float = 0.0) -> Any:
        """Cria material V-Ray"""
        try:
            # Cria material
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            mat.vray.type = 'BRDFVRayMtl'
            
            # Propriedades
            brdf = mat.vray.BRDFVRayMtl
            brdf.color = color
            brdf.reflect_color = (1.0, 1.0, 1.0)
            brdf.reflect_glossiness = 1.0 - roughness
            brdf.metalness = metalness
            brdf.use_roughness = True
            
            self.materials[name] = mat
            
            print(f"✓ Material V-Ray criado: {name}")
            return mat
            
        except Exception as e:
            print(f"✗ Erro ao criar material: {e}")
            return None
    
    def create_glass_material(self, name: str = "VRayGlass",
                             ior: float = 1.52,
                             color: Tuple[float, float, float] = (1, 1, 1),
                             fog_color: Tuple[float, float, float] = (1, 1, 1)) -> Any:
        """Cria vidro V-Ray"""
        try:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            mat.vray.type = 'BRDFVRayMtl'
            
            brdf = mat.vray.BRDFVRayMtl
            brdf.color = (0, 0, 0)  # Preto = totalmente transparente
            brdf.reflect_color = (1, 1, 1)
            brdf.reflect_glossiness = 1.0
            brdf.refract_color = color
            brdf.refract_glossiness = 1.0
            brdf.refract_ior = ior
            brdf.fog_color = fog_color
            brdf.fog_mult = 1.0
            
            self.materials[name] = mat
            
            print(f"✓ Vidro V-Ray criado: {name} (IOR: {ior})")
            return mat
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return None
    
    def create_metal_material(self, name: str = "VRayMetal",
                             color: Tuple[float, float, float] = (0.95, 0.93, 0.88),
                             roughness: float = 0.1) -> Any:
        """Cria metal V-Ray"""
        try:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            mat.vray.type = 'BRDFVRayMtl'
            
            brdf = mat.vray.BRDFVRayMtl
            brdf.color = color
            brdf.metalness = 1.0
            brdf.reflect_color = (1, 1, 1)
            brdf.reflect_glossiness = 1.0 - roughness
            brdf.use_roughness = True
            brdf.anisotropy = 0.0
            
            self.materials[name] = mat
            
            print(f"✓ Metal V-Ray criado: {name}")
            return mat
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return None
    
    def create_sss_material(self, name: str = "VRaySSS",
                           diffuse_color: Tuple[float, float, float] = (0.9, 0.7, 0.6),
                           scatter_color: Tuple[float, float, float] = (0.9, 0.5, 0.4),
                           scatter_radius: float = 5.0) -> Any:
        """Cria material SSS (pele, cera, etc)"""
        try:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True
            mat.vray.type = 'BRDFSSS2Complex'
            
            sss = mat.vray.BRDFSSS2Complex
            sss.diffuse_color = diffuse_color
            sss.sub_surface_color = scatter_color
            sss.scatter_radius = scatter_radius
            sss.scatter_radius_mult = 1.0
            sss.phase_function = -0.3
            
            self.materials[name] = mat
            
            print(f"✓ SSS V-Ray criado: {name}")
            return mat
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return None
    
    def assign_material(self, obj_name: str, material_name: str) -> bool:
        """Atribui material a objeto"""
        try:
            obj = bpy.data.objects.get(obj_name)
            mat = self.materials.get(material_name)
            
            if obj and mat:
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)
                
                print(f"✓ Material {material_name} atribuído a {obj_name}")
                return True
            return False
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return False
    
    # ==================== LUZES VRAY ====================
    
    def create_vray_light(self, name: str = "VRayLight",
                         light_type: str = "RECT",
                         intensity: float = 30.0,
                         color: Tuple[float, float, float] = (1, 1, 1),
                         size_u: float = 5.0,
                         size_v: float = 5.0,
                         temperature: float = 6500) -> Any:
        """Cria luz V-Ray"""
        try:
            # Cria light object
            light_data = bpy.data.lights.new(name=name, type='AREA')
            light_obj = bpy.data.objects.new(name=name, object_data=light_data)
            bpy.context.collection.objects.link(light_obj)
            
            # Configura como V-Ray light
            light_data.vray.type = 'LIGHT'
            vray_light = light_data.vray.LightRectangle
            
            vray_light.intensity = intensity
            vray_light.color = color
            vray_light.size_u = size_u
            vray_light.size_v = size_v
            vray_light.temperature = temperature
            vray_light.use_temperature = True
            vray_light.subdivs = 32
            vray_light.invisible = False
            
            self.lights[name] = light_obj
            
            print(f"✓ V-Ray Light criada: {name} ({intensity} intensity)")
            return light_obj
            
        except Exception as e:
            print(f"✗ Erro ao criar luz: {e}")
            return None
    
    def create_vray_sun(self, name: str = "VRaySun",
                       intensity: float = 1.0,
                       turbidity: float = 3.0,
                       size_multiplier: float = 1.0) -> Any:
        """Cria V-Ray Sun"""
        try:
            # Cria directional light
            light_data = bpy.data.lights.new(name=name, type='SUN')
            light_obj = bpy.data.objects.new(name=name, object_data=light_data)
            bpy.context.collection.objects.link(light_obj)
            
            # Configura como V-Ray Sun
            light_data.vray.type = 'SUN'
            vray_sun = light_data.vray.LightSun
            
            vray_sun.intensity_multiplier = intensity
            vray_sun.turbidity = turbidity
            vray_sun.size_multiplier = size_multiplier
            vray_sun.sky_model = 'HOSEK'
            
            # Rotação típica de sol
            light_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
            
            self.lights[name] = light_obj
            
            print(f"✓ V-Ray Sun criada: {name}")
            return light_obj
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return None
    
    def create_dome_light(self, name: str = "VRayDome",
                         hdri_path: str = None,
                         intensity: float = 1.0,
                         rotation: float = 0.0) -> Any:
        """Cria Dome Light (HDRI)"""
        try:
            # Usa World para dome
            world = bpy.context.scene.world
            if not world:
                world = bpy.data.worlds.new("VRayWorld")
                bpy.context.scene.world = world
            
            world.use_nodes = True
            world.vray.use = True
            
            # Configura V-Ray Dome
            dome = world.vray.SettingsEnvironment
            dome.bg_tex_mult = intensity
            
            if hdri_path and os.path.exists(hdri_path):
                # Cria texture node
                nodes = world.node_tree.nodes
                nodes.clear()
                
                env_tex = nodes.new('ShaderNodeTexEnvironment')
                env_tex.image = bpy.data.images.load(hdri_path)
                
                mapping = nodes.new('ShaderNodeMapping')
                mapping.inputs['Rotation'].default_value[2] = math.radians(rotation)
                
                tex_coord = nodes.new('ShaderNodeTexCoord')
                
                output = nodes.new('ShaderNodeOutputWorld')
                
                # Conecta
                world.node_tree.links.new(tex_coord.outputs['Generated'], 
                                         mapping.inputs['Vector'])
                world.node_tree.links.new(mapping.outputs['Vector'],
                                         env_tex.inputs['Vector'])
                world.node_tree.links.new(env_tex.outputs['Color'],
                                         output.inputs['Surface'])
                
                print(f"✓ HDRI carregado: {hdri_path}")
            
            print(f"✓ V-Ray Dome criada")
            return world
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return None
    
    # ==================== RENDER ELEMENTS (PASSES) ====================
    
    def add_render_element(self, element_type: str) -> bool:
        """Adiciona render element"""
        try:
            elements = {
                'diffuse': 'DIFFUSE',
                'reflection': 'REFLECT',
                'refraction': 'REFRACT',
                'specular': 'SPECULAR',
                'gi': 'GI',
                'lighting': 'LIGHTING',
                'shadows': 'SHADOW',
                'alpha': 'ALPHA',
                'zdepth': 'ZDEPTH',
                'normals': 'NORMALS',
                'velocity': 'VELOCITY',
                'material_id': 'MATERIALID',
                'object_id': 'OBJECTID'
            }
            
            elem_type = elements.get(element_type.lower())
            if elem_type:
                elem = self.vray.RenderChannels.add()
                elem.type = elem_type
                elem.name = element_type
                
                print(f"✓ Render Element adicionado: {element_type}")
                return True
            
            return False
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return False
    
    def enable_all_render_elements(self):
        """Adiciona todos os render elements principais"""
        elements = [
            'diffuse', 'reflection', 'refraction', 'specular',
            'gi', 'lighting', 'shadows', 'alpha', 'zdepth',
            'normals', 'velocity', 'material_id', 'object_id'
        ]
        
        for elem in elements:
            try:
                self.add_render_element(elem)
            except:
                pass
        
        print(f"✓ {len(elements)} render elements configurados")
    
    # ==================== RENDERIZAÇÃO ====================
    
    def render_current_frame(self, output_path: str = None):
        """Renderiza frame atual"""
        try:
            if output_path:
                self.scene.render.filepath = output_path
            
            bpy.ops.render.render(write_still=True)
            print(f"✓ Render concluído")
            
        except Exception as e:
            print(f"✗ Erro no render: {e}")
    
    def render_animation(self, start_frame: int, end_frame: int,
                        output_path: str = None):
        """Renderiza animação"""
        try:
            self.scene.frame_start = start_frame
            self.scene.frame_end = end_frame
            
            if output_path:
                self.scene.render.filepath = output_path
            
            bpy.ops.render.render(animation=True)
            print(f"✓ Animação renderizada: frames {start_frame}-{end_frame}")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    def start_viewport_render(self):
        """Inicia render no viewport (IPR)"""
        try:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.shading.type = 'RENDERED'
            
            print("✓ Viewport render iniciado")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    # ==================== AMBIENTE E ATMOSFERA ====================
    
    def set_environment_fog(self, enabled: bool = True,
                           color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
                           distance: float = 100.0,
                           height: float = 10.0):
        """Configura fog volumétrico"""
        try:
            if enabled:
                self.vray.SettingsEnvironment.fog_color = color
                self.vray.SettingsEnvironment.fog_distance = distance
                self.vray.SettingsEnvironment.fog_height = height
                self.vray.SettingsEnvironment.use_fog = True
                
                print(f"✓ Fog configurado: distância {distance}")
            else:
                self.vray.SettingsEnvironment.use_fog = False
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    # ==================== CÂMERA ====================
    
    def setup_physical_camera(self, camera_obj: Any):
        """Configura câmera física V-Ray"""
        try:
            if camera_obj and camera_obj.type == 'CAMERA':
                self.vray.CameraPhysical.use = True
                self.vray.CameraPhysical.type = 'STILL'
                self.vray.CameraPhysical.specify_fov = False
                self.vray.CameraPhysical.f_number = 5.6
                self.vray.CameraPhysical.lens_shift = 0.0
                self.vray.CameraPhysical.shutter_speed = 125.0
                self.vray.CameraPhysical.shutter_angle = 180.0
                self.vray.CameraPhysical.shutter_offset = 0.0
                self.vray.CameraPhysical.latency = 0.0
                self.vray.CameraPhysical.ISO = 100.0
                self.vray.CameraPhysical.white_balance = (1.0, 1.0, 1.0)
                self.vray.CameraPhysical.vignetting = 1.0
                self.vray.CameraPhysical.distortion = 0.0
                self.vray.CameraPhysical.distortion_type = 'QUADRATIC'
                
                print(f"✓ Câmera física V-Ray configurada: {camera_obj.name}")
            else:
                print("✗ Objeto não é uma câmera")
                
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    # ==================== OTIMIZAÇÃO E PERFORMANCE ====================
    
    def optimize_for_gpu(self):
        """Otimiza configurações para GPU rendering"""
        try:
            self.vray.SettingsOptions.use_gpu = True
            self.vray.SettingsRTEngine.trace_depth = 5
            self.vray.SettingsRTEngine.gi_depth = 3
            self.vray.SettingsOptions.override_max_size = True
            self.vray.SettingsOptions.max_render_time = 0
            
            print("✓ Otimização GPU ativada")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    def set_bucket_rendering(self, size: int = 64, order: str = "SPIRAL"):
        """Configura bucket rendering"""
        try:
            orders = {
                'spiral': 'SPIRAL',
                'hilbert': 'HILBERT',
                'horizontal': 'HORIZONTAL',
                'vertical': 'VERTICAL',
                'triangulation': 'TRIANGULATION'
            }
            
            self.vray.SettingsImageSampler.bucket_width = size
            self.vray.SettingsImageSampler.bucket_height = size
            self.vray.SettingsImageSampler.render_order = orders.get(order.lower(), 'SPIRAL')
            
            print(f"✓ Bucket rendering: {size}x{size}, ordem {order}")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    def enable_distributed_rendering(self, server_list: List[str] = None):
        """Ativa render distribuído"""
        try:
            self.vray.SettingsDR.on = True
            
            if server_list:
                self.vray.SettingsDR.network_type = 'NORMAL'
                # Adicionar servidores aqui
                for server in server_list:
                    # self.vray.SettingsDR.nodes.add(server)
                    print(f"  • Servidor: {server}")
            
            print("✓ Distributed Rendering ativado")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    # ==================== EXPORT & BATCH ====================
    
    def export_vrscene(self, filepath: str):
        """Exporta cena para .vrscene"""
        try:
            self.vray.Exporter.output = filepath
            self.vray.Exporter.auto_save_vrscene = True
            
            bpy.ops.vray.export_vrscene()
            
            print(f"✓ Cena exportada: {filepath}")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    def save_render_preset(self, name: str, filepath: str):
        """Salva preset de render"""
        try:
            preset_data = {
                'name': name,
                'image_sampler': {
                    'type': self.vray.SettingsImageSampler.type,
                    'max_subdivs': self.vray.SettingsImageSampler.progressive_maxSubdivs,
                    'threshold': self.vray.SettingsImageSampler.progressive_threshold
                },
                'gi': {
                    'enabled': self.vray.SettingsGI.on,
                    'primary': self.vray.SettingsGI.primary_engine,
                    'secondary': self.vray.SettingsGI.secondary_engine
                },
                'resolution': {
                    'x': self.scene.render.resolution_x,
                    'y': self.scene.render.resolution_y
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(preset_data, f, indent=4)
            
            print(f"✓ Preset salvo: {filepath}")
            
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    # ==================== UTILITIES ====================
    
    def print_current_settings(self):
        """Exibe configurações atuais"""
        print("\n" + "="*60)
        print("CONFIGURAÇÕES ATUAIS V-RAY 7.10.01")
        print("="*60)
        
        try:
            print(f"\n📊 IMAGE SAMPLER")
            print(f"  • Tipo: {self.vray.SettingsImageSampler.type}")
            print(f"  • Max Subdivs: {self.vray.SettingsImageSampler.progressive_maxSubdivs}")
            print(f"  • Threshold: {self.vray.SettingsImageSampler.progressive_threshold}")
            
            print(f"\n🌍 GLOBAL ILLUMINATION")
            print(f"  • Enabled: {self.vray.SettingsGI.on}")
            print(f"  • Primary: {self.vray.SettingsGI.primary_engine}")
            print(f"  • Secondary: {self.vray.SettingsGI.secondary_engine}")
            
            print(f"\n🎨 RENDER")
            print(f"  • Resolução: {self.scene.render.resolution_x}x{self.scene.render.resolution_y}")
            print(f"  • Engine: {self.scene.render.engine}")
            
            print(f"\n💡 LIGHTS: {len(self.lights)} criadas")
            print(f"🎭 MATERIALS: {len(self.materials)} criados")
            
            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"✗ Erro ao exibir configurações: {e}")
    
    def get_estimated_render_time(self) -> str:
        """Estima tempo de render (aproximado)"""
        try:
            resolution = self.scene.render.resolution_x * self.scene.render.resolution_y
            subdivs = self.vray.SettingsImageSampler.progressive_maxSubdivs
            
            # Fórmula simplificada
            pixels_per_second = 10000  # Estimativa base
            total_samples = resolution * subdivs
            estimated_seconds = total_samples / pixels_per_second
            
            minutes = int(estimated_seconds / 60)
            seconds = int(estimated_seconds % 60)
            
            return f"~{minutes}min {seconds}s (estimativa aproximada)"
            
        except:
            return "Não disponível"
    
    # ==================== QUICK SETUP METHODS ====================
    
    def quick_setup_photorealistic(self):
        """Setup completo para render fotorrealista"""
        print("\n" + "="*60)
        print("🎬 QUICK SETUP: FOTORREALISTA")
        print("="*60 + "\n")
        
        self.set_ultra_quality()
        self.enable_denoiser("nvidia", 0.8)
        self.enable_all_render_elements()
        self.set_bucket_rendering(64, "spiral")
        
        print("\n✓ Setup fotorrealista completo!")
        print(f"⏱  Tempo estimado: {self.get_estimated_render_time()}")
    
    def quick_setup_animation(self):
        """Setup otimizado para animação"""
        print("\n" + "="*60)
        print("🎬 QUICK SETUP: ANIMAÇÃO")
        print("="*60 + "\n")
        
        self.set_production_quality()
        self.enable_denoiser("nvidia", 1.0)
        self.set_motion_blur(True, 0.5, 16)
        
        print("\n✓ Setup animação completo!")
    
    def quick_setup_architectural(self):
        """Setup para renderização arquitetônica"""
        print("\n" + "="*60)
        print("🎬 QUICK SETUP: ARQUITETÔNICO")
        print("="*60 + "\n")
        
        self.set_ultra_quality()
        self.set_gi_engines("brute_force", "light_cache")
        self.enable_denoiser("nvidia", 0.7)
        self.set_render_resolution(3840, 2160)  # 4K
        
        # Adiciona elementos úteis
        self.add_render_element('diffuse')
        self.add_render_element('reflection')
        self.add_render_element('gi')
        self.add_render_element('lighting')
        self.add_render_element('alpha')
        
        print("\n✓ Setup arquitetônico completo!")


# ==================== EXEMPLO DE USO ====================

def example_usage():
    """Exemplo de como usar o controlador"""
    
    # Inicializa
    vray = VRayBlenderController()
    
    if not vray.initialize():
        print("ERRO: V-Ray não está instalado ou não foi inicializado")
        return
    
    # ===== OPÇÃO 1: Setup Rápido =====
    # vray.quick_setup_photorealistic()
    # vray.quick_setup_animation()
    # vray.quick_setup_architectural()
    
    # ===== OPÇÃO 2: Configuração Manual =====
    
    # Define qualidade
    vray.set_ultra_quality()
    # vray.set_production_quality()
    # vray.set_preview_quality()
    
    # Ativa denoiser
    vray.enable_denoiser("nvidia", strength=0.8)
    
    # Cria materiais
    chrome = vray.create_metal_material("Chrome", (0.95, 0.95, 0.95), roughness=0.05)
    glass = vray.create_glass_material("Glass", ior=1.52)
    plastic = vray.create_vray_material("Plastic", (0.8, 0.2, 0.2), roughness=0.3)
    skin = vray.create_sss_material("Skin")
    
    # Cria luzes
    key_light = vray.create_vray_light("KeyLight", intensity=50, size_u=10, size_v=10)
    sun = vray.create_vray_sun("Sun", intensity=1.5, turbidity=2.5)
    dome = vray.create_dome_light("Dome", intensity=1.0)
    
    # Configura câmera (se existir)
    camera = bpy.data.objects.get("Camera")
    if camera:
        vray.setup_physical_camera(camera)
        vray.set_dof(camera, True, focus_distance=10.0, aperture=2.8)
    
    # Adiciona render elements
    vray.enable_all_render_elements()
    
    # Mostra configurações
    vray.print_current_settings()
    
    # Renderiza
    # vray.render_current_frame("/tmp/render.exr")
    # vray.render_animation(1, 100, "/tmp/animation_")
    
    print("\n✓ Configuração concluída!")
    print("🎬 Pronto para renderizar!")


# ==================== EXECUTAR ====================

if __name__ == "__main__":
    # Descomenta para executar o exemplo
    example_usage()
    
    # Ou use manualmente:
    # vray = VRayBlenderController()
    # vray.initialize()
    # vray.quick_setup_photorealistic()
    # vray.render_current_frame()
