"""
Script V3 - DECODIFICAÇÃO REAL de Layer Styles do PSD
Parseia o binário hexadecimal para extrair valores reais dos efeitos
"""

import os
import json
import struct
from pathlib import Path
from psd_tools import PSDImage
from typing import Dict, List, Any

# Mapeamento de códigos de efeitos conhecidos
EFFECT_KEYS = {
    b'dsdw': 'drop_shadow',
    b'isdw': 'inner_shadow', 
    b'oglw': 'outer_glow',
    b'iglw': 'inner_glow',
    b'bevl': 'bevel_emboss',
    b'sofi': 'satin',
    b'SoCo': 'color_overlay',
    b'GrFl': 'gradient_overlay',
    b'patf': 'pattern_overlay',
    b'FrFX': 'stroke',
}

def parse_fixed_point(data, offset):
    """Converte fixed point (16.16) para float"""
    try:
        value = struct.unpack('>i', data[offset:offset+4])[0]
        return value / 65536.0
    except:
        return 0.0

def parse_double(data, offset):
    """Converte double (8 bytes) para float"""
    try:
        return struct.unpack('>d', data[offset:offset+8])[0]
    except:
        return 0.0

def parse_long(data, offset):
    """Converte long (4 bytes) para int"""
    try:
        return struct.unpack('>i', data[offset:offset+4])[0]
    except:
        return 0

def parse_short(data, offset):
    """Converte short (2 bytes) para int"""
    try:
        return struct.unpack('>h', data[offset:offset+2])[0]
    except:
        return 0

def parse_byte(data, offset):
    """Converte byte para int"""
    try:
        return struct.unpack('>B', data[offset:offset+1])[0]
    except:
        return 0

def parse_color(data, offset):
    """Extrai cor RGB"""
    try:
        # Formato comum: 10 bytes (2 para espaço de cor + 4x2 para RGBA)
        color_space = parse_short(data, offset)
        r = parse_short(data, offset + 2) / 256
        g = parse_short(data, offset + 4) / 256
        b = parse_short(data, offset + 6) / 256
        a = parse_short(data, offset + 8) / 256
        return {'r': int(r), 'g': int(g), 'b': int(b), 'a': int(a * 255)}
    except:
        return None

def decode_drop_shadow(data):
    """Decodifica Drop Shadow do binário"""
    effect = {'enabled': True}
    
    try:
        # Versão (4 bytes)
        version = parse_long(data, 0)
        offset = 4
        
        # Blur (4 bytes - fixed point)
        effect['blur'] = parse_fixed_point(data, offset)
        offset += 4
        
        # Intensidade (4 bytes - fixed point)
        effect['intensity'] = parse_fixed_point(data, offset)
        offset += 4
        
        # Ângulo (4 bytes - fixed point)
        effect['angle'] = parse_fixed_point(data, offset)
        offset += 4
        
        # Distância (4 bytes - fixed point)
        effect['distance'] = parse_fixed_point(data, offset)
        offset += 4
        
        # Cor (10 bytes)
        effect['color'] = parse_color(data, offset)
        offset += 10
        
        # Blend Mode (8 bytes - signature + key)
        offset += 8
        
        # Opacidade (1 byte)
        effect['opacity'] = parse_byte(data, offset)
        offset += 1
        
        # Enabled (1 byte)
        effect['enabled'] = bool(parse_byte(data, offset))
        offset += 1
        
        # Use global light (1 byte)
        effect['use_global_light'] = bool(parse_byte(data, offset))
        
    except Exception as e:
        effect['parse_error'] = str(e)
    
    return effect

def decode_inner_shadow(data):
    """Decodifica Inner Shadow"""
    effect = {'enabled': True}
    
    try:
        offset = 4  # Skip version
        effect['blur'] = parse_fixed_point(data, offset)
        offset += 4
        effect['intensity'] = parse_fixed_point(data, offset)
        offset += 4
        effect['angle'] = parse_fixed_point(data, offset)
        offset += 4
        effect['distance'] = parse_fixed_point(data, offset)
        offset += 4
        effect['color'] = parse_color(data, offset)
        offset += 10 + 8  # Color + blend mode
        effect['opacity'] = parse_byte(data, offset)
        offset += 1
        effect['enabled'] = bool(parse_byte(data, offset))
    except:
        pass
    
    return effect

def decode_outer_glow(data):
    """Decodifica Outer Glow"""
    effect = {'enabled': True}
    
    try:
        offset = 4
        effect['blur'] = parse_fixed_point(data, offset)
        offset += 4
        effect['intensity'] = parse_fixed_point(data, offset)
        offset += 4
        effect['color'] = parse_color(data, offset)
        offset += 10 + 8
        effect['opacity'] = parse_byte(data, offset)
    except:
        pass
    
    return effect

def decode_bevel_emboss(data):
    """Decodifica Bevel and Emboss"""
    effect = {'enabled': True}
    
    try:
        offset = 4
        effect['angle'] = parse_fixed_point(data, offset)
        offset += 4
        effect['strength'] = parse_fixed_point(data, offset)
        offset += 4
        effect['blur'] = parse_fixed_point(data, offset)
        offset += 4
        
        # Highlight
        offset += 8  # Blend mode
        effect['highlight_color'] = parse_color(data, offset)
        offset += 10
        effect['highlight_opacity'] = parse_byte(data, offset)
        offset += 1
        
        # Shadow  
        offset += 8  # Blend mode
        effect['shadow_color'] = parse_color(data, offset)
        offset += 10
        effect['shadow_opacity'] = parse_byte(data, offset)
    except:
        pass
    
    return effect

def decode_stroke(data):
    """Decodifica Stroke"""
    effect = {'enabled': True}
    
    try:
        offset = 4
        effect['size'] = parse_fixed_point(data, offset)
        offset += 4
        effect['position'] = parse_long(data, offset)  # 0=outside, 1=inside, 2=center
        offset += 4 + 8  # Skip blend mode
        effect['opacity'] = parse_byte(data, offset)
        offset += 1
        effect['enabled'] = bool(parse_byte(data, offset))
        offset += 1
        effect['fill_type'] = parse_long(data, offset)  # 0=color, 1=gradient, 2=pattern
        offset += 4
        effect['color'] = parse_color(data, offset)
    except:
        pass
    
    return effect

def extract_layer_styles(layer) -> Dict[str, Any]:
    """Extrai e DECODIFICA Layer Styles"""
    styles = {
        'blend_mode': str(getattr(layer, 'blend_mode', 'normal')),
        'opacity': getattr(layer, 'opacity', 255),
        'effects': {}
    }
    
    try:
        if not hasattr(layer, '_record') or not layer._record:
            return styles
        
        record = layer._record
        
        if hasattr(record, 'tagged_blocks'):
            for block in record.tagged_blocks:
                try:
                    # Identificar tipo de efeito
                    effect_key = None
                    raw_data = None
                    
                    # Tentar extrair key
                    if hasattr(block, 'key'):
                        effect_key = block.key
                    elif hasattr(block, 'tag'):
                        effect_key = block.tag
                    
                    # Tentar extrair dados brutos
                    if hasattr(block, 'data'):
                        raw_data = block.data
                    elif hasattr(block, 'value'):
                        if isinstance(block.value, bytes):
                            raw_data = block.value
                        elif isinstance(block.value, str):
                            raw_data = bytes.fromhex(block.value)
                    
                    # Decodificar se temos key e data
                    if effect_key and raw_data and isinstance(raw_data, bytes):
                        effect_name = EFFECT_KEYS.get(effect_key, effect_key.decode('latin-1') if isinstance(effect_key, bytes) else str(effect_key))
                        
                        # Aplicar decoder específico
                        if effect_key == b'dsdw':
                            styles['effects']['drop_shadow'] = decode_drop_shadow(raw_data)
                        elif effect_key == b'isdw':
                            styles['effects']['inner_shadow'] = decode_inner_shadow(raw_data)
                        elif effect_key == b'oglw':
                            styles['effects']['outer_glow'] = decode_outer_glow(raw_data)
                        elif effect_key == b'bevl':
                            styles['effects']['bevel_emboss'] = decode_bevel_emboss(raw_data)
                        elif effect_key == b'FrFX':
                            styles['effects']['stroke'] = decode_stroke(raw_data)
                        else:
                            # Efeito desconhecido - salvar hex
                            styles['effects'][effect_name] = {
                                'raw_hex': raw_data.hex()[:200],
                                'decoded': False
                            }
                
                except Exception as e:
                    pass
    
    except Exception as e:
        styles['parse_error'] = str(e)
    
    return styles

def extract_text_data(layer):
    """Extrai dados de texto"""
    if not hasattr(layer, 'text'):
        return None
    
    return {
        'content': str(getattr(layer, 'text', '')),
        'has_engine_dict': hasattr(layer, 'engine_dict')
    }

def process_layer(layer, path="", depth=0):
    """Processa layer"""
    current_path = f"{path}/{layer.name}" if path else layer.name
    print("  " * depth + f"📄 {layer.name}")
    
    data = {
        'name': layer.name,
        'path': current_path,
        'type': str(getattr(layer, 'kind', 'unknown')),
        'visible': getattr(layer, 'visible', True),
        'bounds': {
            'left': getattr(layer, 'left', 0),
            'top': getattr(layer, 'top', 0),
            'width': getattr(layer, 'width', 0),
            'height': getattr(layer, 'height', 0)
        },
        'styles': extract_layer_styles(layer),
        'text': extract_text_data(layer),
        'children': []
    }
    
    if hasattr(layer, '__iter__'):
        try:
            for sublayer in layer:
                data['children'].append(process_layer(sublayer, current_path, depth + 1))
        except:
            pass
    
    return data

def main():
    """Função principal"""
    psd_files = list(Path('.').glob('*.psd'))
    
    if not psd_files:
        print("❌ Nenhum PSD encontrado!")
        return
    
    output_dir = Path('psd_decoded_output')
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n🔍 Encontrados {len(psd_files)} arquivo(s) PSD\n")
    
    for psd_file in psd_files:
        try:
            print(f"{'='*70}")
            print(f"📂 {psd_file.name}")
            print(f"{'='*70}\n")
            
            psd = PSDImage.open(str(psd_file))
            
            data = {
                'filename': psd_file.name,
                'width': psd.width,
                'height': psd.height,
                'layers': [process_layer(layer) for layer in psd]
            }
            
            json_path = output_dir / f"{psd_file.stem}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            size_kb = os.path.getsize(json_path) / 1024
            print(f"\n✅ Salvo: {json_path.name} ({size_kb:.1f} KB)\n")
            
        except Exception as e:
            print(f"❌ Erro: {e}\n")
    
    print(f"{'='*70}")
    print(f"✅ Concluído! JSONs em: {output_dir}/")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
