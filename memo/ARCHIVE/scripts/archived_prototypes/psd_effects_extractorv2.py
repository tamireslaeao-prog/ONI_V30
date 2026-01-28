"""
Script COMPLETO para extrair TODOS os efeitos, estilos e conteúdo de arquivos PSD
Versão 2.0 - Extração profunda de Layer Styles e conteúdo
"""

import os
import json
from pathlib import Path
from psd_tools import PSDImage
from psd_tools.constants import BlendMode
from typing import Dict, List, Any
import struct

def extract_color(color_data) -> Dict[str, int]:
    """Extrai dados de cor em formato RGB"""
    try:
        if hasattr(color_data, 'r'):
            return {
                'r': int(getattr(color_data, 'r', 0)),
                'g': int(getattr(color_data, 'g', 0)),
                'b': int(getattr(color_data, 'b', 0)),
                'a': int(getattr(color_data, 'a', 255))
            }
    except:
        pass
    return None

def extract_gradient(gradient_data) -> Dict[str, Any]:
    """Extrai informações de gradiente"""
    try:
        gradient = {
            'type': str(getattr(gradient_data, 'type', 'linear')),
            'angle': getattr(gradient_data, 'angle', 0),
            'scale': getattr(gradient_data, 'scale', 100),
            'reverse': getattr(gradient_data, 'reverse', False),
            'color_stops': []
        }
        
        if hasattr(gradient_data, 'color_stops'):
            for stop in gradient_data.color_stops:
                gradient['color_stops'].append({
                    'location': getattr(stop, 'location', 0),
                    'color': extract_color(getattr(stop, 'color', None))
                })
        
        return gradient
    except:
        return None

def extract_layer_effects_deep(layer) -> Dict[str, Any]:
    """Extração PROFUNDA de todos os Layer Styles e efeitos"""
    effects = {
        'blend_mode': str(layer.blend_mode) if hasattr(layer, 'blend_mode') else 'normal',
        'opacity': layer.opacity if hasattr(layer, 'opacity') else 100,
        'fill_opacity': None,
        'layer_styles': {}
    }
    
    if not hasattr(layer, '_record'):
        return effects
    
    try:
        # Acessar informações de efeitos
        if hasattr(layer._record, 'tagged_blocks'):
            effects_info = None
            
            # Procurar bloco de efeitos
            for block in layer._record.tagged_blocks:
                if block.key == b'lrFX' or block.key == b'lfx2':
                    effects_info = block
                    break
            
            if effects_info and hasattr(effects_info, 'data'):
                data = effects_info.data
                
                # DROP SHADOW
                if hasattr(data, 'drop_shadow') and data.drop_shadow.enabled:
                    ds = data.drop_shadow
                    effects['layer_styles']['drop_shadow'] = {
                        'enabled': True,
                        'blend_mode': str(ds.blend_mode) if hasattr(ds, 'blend_mode') else 'multiply',
                        'color': extract_color(ds.color) if hasattr(ds, 'color') else None,
                        'opacity': getattr(ds, 'opacity', 100),
                        'angle': getattr(ds, 'angle', 120),
                        'distance': getattr(ds, 'distance', 5),
                        'spread': getattr(ds, 'choke', 0),
                        'size': getattr(ds, 'blur', 5),
                        'noise': getattr(ds, 'noise', 0),
                        'use_global_light': getattr(ds, 'use_global_angle', True),
                        'contour': str(getattr(ds, 'contour', 'linear')),
                        'anti_aliased': getattr(ds, 'anti_aliased', False),
                        'layer_knocks_out': getattr(ds, 'layer_knocks_out', True)
                    }
                
                # INNER SHADOW
                if hasattr(data, 'inner_shadow') and data.inner_shadow.enabled:
                    ish = data.inner_shadow
                    effects['layer_styles']['inner_shadow'] = {
                        'enabled': True,
                        'blend_mode': str(ish.blend_mode) if hasattr(ish, 'blend_mode') else 'multiply',
                        'color': extract_color(ish.color) if hasattr(ish, 'color') else None,
                        'opacity': getattr(ish, 'opacity', 75),
                        'angle': getattr(ish, 'angle', 120),
                        'distance': getattr(ish, 'distance', 5),
                        'choke': getattr(ish, 'choke', 0),
                        'size': getattr(ish, 'blur', 5),
                        'noise': getattr(ish, 'noise', 0),
                        'use_global_light': getattr(ish, 'use_global_angle', True)
                    }
                
                # OUTER GLOW
                if hasattr(data, 'outer_glow') and data.outer_glow.enabled:
                    og = data.outer_glow
                    effects['layer_styles']['outer_glow'] = {
                        'enabled': True,
                        'blend_mode': str(og.blend_mode) if hasattr(og, 'blend_mode') else 'screen',
                        'opacity': getattr(og, 'opacity', 75),
                        'noise': getattr(og, 'noise', 0),
                        'color': extract_color(og.color) if hasattr(og, 'color') else None,
                        'technique': str(getattr(og, 'technique', 'softer')),
                        'spread': getattr(og, 'choke', 0),
                        'size': getattr(og, 'blur', 5),
                        'contour': str(getattr(og, 'contour', 'linear')),
                        'range': getattr(og, 'range', 50),
                        'jitter': getattr(og, 'jitter', 0)
                    }
                
                # INNER GLOW
                if hasattr(data, 'inner_glow') and data.inner_glow.enabled:
                    ig = data.inner_glow
                    effects['layer_styles']['inner_glow'] = {
                        'enabled': True,
                        'blend_mode': str(ig.blend_mode) if hasattr(ig, 'blend_mode') else 'screen',
                        'opacity': getattr(ig, 'opacity', 75),
                        'color': extract_color(ig.color) if hasattr(ig, 'color') else None,
                        'technique': str(getattr(ig, 'technique', 'softer')),
                        'source': str(getattr(ig, 'source', 'edge')),
                        'choke': getattr(ig, 'choke', 0),
                        'size': getattr(ig, 'blur', 5)
                    }
                
                # BEVEL AND EMBOSS
                if hasattr(data, 'bevel') and data.bevel.enabled:
                    bv = data.bevel
                    effects['layer_styles']['bevel_emboss'] = {
                        'enabled': True,
                        'style': str(getattr(bv, 'bevel_style', 'inner_bevel')),
                        'technique': str(getattr(bv, 'technique', 'smooth')),
                        'depth': getattr(bv, 'strength', 100),
                        'direction': str(getattr(bv, 'direction', 'up')),
                        'size': getattr(bv, 'blur', 5),
                        'soften': getattr(bv, 'soften', 0),
                        'angle': getattr(bv, 'light_angle', 120),
                        'altitude': getattr(bv, 'light_altitude', 30),
                        'use_global_light': getattr(bv, 'use_global_angle', True),
                        'highlight_mode': str(getattr(bv, 'highlight_blend_mode', 'screen')),
                        'highlight_color': extract_color(getattr(bv, 'highlight_color', None)),
                        'highlight_opacity': getattr(bv, 'highlight_opacity', 75),
                        'shadow_mode': str(getattr(bv, 'shadow_blend_mode', 'multiply')),
                        'shadow_color': extract_color(getattr(bv, 'shadow_color', None)),
                        'shadow_opacity': getattr(bv, 'shadow_opacity', 75)
                    }
                
                # SATIN
                if hasattr(data, 'satin') and data.satin.enabled:
                    st = data.satin
                    effects['layer_styles']['satin'] = {
                        'enabled': True,
                        'blend_mode': str(st.blend_mode) if hasattr(st, 'blend_mode') else 'multiply',
                        'color': extract_color(st.color) if hasattr(st, 'color') else None,
                        'opacity': getattr(st, 'opacity', 50),
                        'angle': getattr(st, 'angle', 19),
                        'distance': getattr(st, 'distance', 11),
                        'size': getattr(st, 'blur', 14),
                        'contour': str(getattr(st, 'contour', 'linear')),
                        'invert': getattr(st, 'invert', False)
                    }
                
                # COLOR OVERLAY
                if hasattr(data, 'solid_fill') and data.solid_fill.enabled:
                    co = data.solid_fill
                    effects['layer_styles']['color_overlay'] = {
                        'enabled': True,
                        'blend_mode': str(co.blend_mode) if hasattr(co, 'blend_mode') else 'normal',
                        'color': extract_color(co.color) if hasattr(co, 'color') else None,
                        'opacity': getattr(co, 'opacity', 100)
                    }
                
                # GRADIENT OVERLAY
                if hasattr(data, 'gradient_fill') and data.gradient_fill.enabled:
                    gf = data.gradient_fill
                    effects['layer_styles']['gradient_overlay'] = {
                        'enabled': True,
                        'blend_mode': str(gf.blend_mode) if hasattr(gf, 'blend_mode') else 'normal',
                        'opacity': getattr(gf, 'opacity', 100),
                        'gradient': extract_gradient(gf.gradient) if hasattr(gf, 'gradient') else None,
                        'style': str(getattr(gf, 'style', 'linear')),
                        'reverse': getattr(gf, 'reverse', False),
                        'align_with_layer': getattr(gf, 'align_with_layer', True),
                        'angle': getattr(gf, 'angle', 90),
                        'scale': getattr(gf, 'scale', 100)
                    }
                
                # PATTERN OVERLAY
                if hasattr(data, 'pattern_fill') and data.pattern_fill.enabled:
                    pf = data.pattern_fill
                    effects['layer_styles']['pattern_overlay'] = {
                        'enabled': True,
                        'blend_mode': str(pf.blend_mode) if hasattr(pf, 'blend_mode') else 'normal',
                        'opacity': getattr(pf, 'opacity', 100),
                        'scale': getattr(pf, 'scale', 100),
                        'pattern_name': str(getattr(pf, 'pattern_name', ''))
                    }
                
                # STROKE
                if hasattr(data, 'stroke') and data.stroke.enabled:
                    sk = data.stroke
                    effects['layer_styles']['stroke'] = {
                        'enabled': True,
                        'size': getattr(sk, 'size', 3),
                        'position': str(getattr(sk, 'position', 'outside')),
                        'blend_mode': str(sk.blend_mode) if hasattr(sk, 'blend_mode') else 'normal',
                        'opacity': getattr(sk, 'opacity', 100),
                        'fill_type': str(getattr(sk, 'fill_type', 'color')),
                        'color': extract_color(sk.color) if hasattr(sk, 'color') else None
                    }
    
    except Exception as e:
        print(f"  ⚠ Aviso ao extrair efeitos: {e}")
    
    return effects

def extract_text_data(layer) -> Dict[str, Any]:
    """Extrai TODOS os dados de camadas de texto"""
    if not hasattr(layer, 'text') or layer.kind != 'type':
        return None
    
    text_data = {
        'content': str(layer.text) if hasattr(layer, 'text') else '',
        'font': None,
        'size': None,
        'color': None,
        'alignment': None,
        'styles': []
    }
    
    try:
        # Acessar engine_dict para dados de texto
        if hasattr(layer, 'engine_dict'):
            engine = layer.engine_dict
            
            # Extrair dados de estilo
            if 'StyleRun' in engine and 'RunArray' in engine['StyleRun']:
                for run in engine['StyleRun']['RunArray']:
                    style_sheet = run.get('StyleSheet', {}).get('StyleSheetData', {})
                    
                    style_info = {
                        'font_name': style_sheet.get('Font', ''),
                        'font_size': style_sheet.get('FontSize', 0),
                        'font_color': None,
                        'bold': style_sheet.get('FauxBold', False),
                        'italic': style_sheet.get('FauxItalic', False),
                        'underline': style_sheet.get('Underline', False),
                        'strikethrough': style_sheet.get('Strikethrough', False)
                    }
                    
                    # Extrair cor do texto
                    if 'FillColor' in style_sheet:
                        fc = style_sheet['FillColor']
                        if 'Values' in fc:
                            vals = fc['Values']
                            if len(vals) >= 3:
                                style_info['font_color'] = {
                                    'r': int(vals[0] * 255),
                                    'g': int(vals[1] * 255),
                                    'b': int(vals[2] * 255),
                                    'a': int(vals[3] * 255) if len(vals) > 3 else 255
                                }
                    
                    text_data['styles'].append(style_info)
            
            # Pegar primeiro estilo como padrão
            if text_data['styles']:
                first_style = text_data['styles'][0]
                text_data['font'] = first_style['font_name']
                text_data['size'] = first_style['font_size']
                text_data['color'] = first_style['font_color']
            
            # Alinhamento
            if 'ParagraphRun' in engine and 'RunArray' in engine['ParagraphRun']:
                para = engine['ParagraphRun']['RunArray'][0].get('ParagraphSheet', {}).get('Properties', {})
                text_data['alignment'] = para.get('Justification', 'left')
    
    except Exception as e:
        print(f"  ⚠ Aviso ao extrair texto: {e}")
    
    return text_data

def extract_shape_data(layer) -> Dict[str, Any]:
    """Extrai dados de camadas de forma (shape)"""
    if layer.kind != 'shape':
        return None
    
    shape_data = {
        'type': 'shape',
        'fill_color': None,
        'stroke_color': None,
        'stroke_width': None
    }
    
    try:
        if hasattr(layer, '_record') and hasattr(layer._record, 'tagged_blocks'):
            for block in layer._record.tagged_blocks:
                # Procurar informações de preenchimento
                if block.key == b'SoCo':  # Solid Color
                    shape_data['fill_color'] = extract_color(block.color) if hasattr(block, 'color') else None
                elif block.key == b'vstk':  # Vector Stroke
                    if hasattr(block, 'stroke_style'):
                        shape_data['stroke_width'] = getattr(block.stroke_style, 'line_width', None)
    except Exception as e:
        print(f"  ⚠ Aviso ao extrair shape: {e}")
    
    return shape_data

def process_layer(layer, layer_path: str = "") -> Dict[str, Any]:
    """Processa um layer com TODOS os dados possíveis"""
    current_path = f"{layer_path}/{layer.name}" if layer_path else layer.name
    
    layer_data = {
        'name': layer.name,
        'path': current_path,
        'type': str(layer.kind) if hasattr(layer, 'kind') else 'unknown',
        'visible': layer.visible if hasattr(layer, 'visible') else True,
        'locked': getattr(layer, 'protected', {}).get('transparency', False) if hasattr(layer, 'protected') else False,
        'effects': extract_layer_effects_deep(layer),
        'bounds': {
            'left': layer.left,
            'top': layer.top,
            'right': layer.right,
            'bottom': layer.bottom,
            'width': layer.width,
            'height': layer.height
        } if hasattr(layer, 'left') else None,
        'text_data': extract_text_data(layer),
        'shape_data': extract_shape_data(layer),
        'children': []
    }
    
    # Processar sub-layers
    if hasattr(layer, '__iter__'):
        for sublayer in layer:
            child_data = process_layer(sublayer, current_path)
            layer_data['children'].append(child_data)
    
    return layer_data

def extract_psd_complete(psd_path: str) -> Dict[str, Any]:
    """Extração COMPLETA de um arquivo PSD"""
    print(f"📄 Processando: {psd_path}")
    
    psd = PSDImage.open(psd_path)
    
    output_data = {
        'filename': os.path.basename(psd_path),
        'width': psd.width,
        'height': psd.height,
        'channels': psd.channels if hasattr(psd, 'channels') else 0,
        'depth': psd.depth if hasattr(psd, 'depth') else 8,
        'color_mode': str(psd.color_mode) if hasattr(psd, 'color_mode') else 'RGB',
        'layers': []
    }
    
    # Processar todos os layers
    total_layers = 0
    for layer in psd:
        layer_data = process_layer(layer)
        output_data['layers'].append(layer_data)
        total_layers += 1
    
    print(f"  ✓ {total_layers} layers processados")
    
    return output_data

def main():
    """Função principal"""
    current_dir = Path('.')
    psd_files = list(current_dir.glob('*.psd'))
    
    if not psd_files:
        print("❌ Nenhum arquivo PSD encontrado na pasta atual.")
        return
    
    print(f"🔍 Encontrados {len(psd_files)} arquivo(s) PSD\n")
    
    all_data = []
    
    for psd_file in psd_files:
        try:
            psd_data = extract_psd_complete(str(psd_file))
            all_data.append(psd_data)
        except Exception as e:
            print(f"❌ Erro ao processar {psd_file}: {e}")
    
    # Salvar JSON
    output_file = 'psd_complete_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ EXTRAÇÃO COMPLETA FINALIZADA!")
    print(f"{'='*60}")
    print(f"📊 Arquivos processados: {len(all_data)}")
    print(f"💾 JSON salvo em: {output_file}")
    print(f"\n📋 Dados extraídos:")
    print(f"   ✓ Layer Styles completos (Drop Shadow, Bevel, Glow, etc.)")
    print(f"   ✓ Conteúdo de texto + fontes + cores")
    print(f"   ✓ Dados de shapes + fills")
    print(f"   ✓ Blend modes + opacidades")
    print(f"   ✓ Hierarquia completa")
    print(f"   ✓ Geometria (bounds)")

if __name__ == '__main__':
    # Instalar: pip install psd-tools
    main()