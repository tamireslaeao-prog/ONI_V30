"""
Script para extrair efeitos de layers de arquivos PSD
Gera um JSON estruturado para treinamento de IA
"""

import os
import json
from pathlib import Path
from psd_tools import PSDImage
from typing import Dict, List, Any

def extract_layer_effects(layer) -> Dict[str, Any]:
    """Extrai todos os efeitos de um layer"""
    effects = {}
    
    # Verificar se o layer tem efeitos
    if not hasattr(layer, '_record') or not layer._record:
        return effects
    
    # Extrair informações de efeitos da estrutura do layer
    try:
        # Blend mode
        if hasattr(layer, 'blend_mode'):
            effects['blend_mode'] = str(layer.blend_mode)
        
        # Opacidade
        if hasattr(layer, 'opacity'):
            effects['opacity'] = layer.opacity
        
        # Efeitos de layer (layer effects/styles)
        if hasattr(layer._record, 'tagged_blocks'):
            for block in layer._record.tagged_blocks:
                # Drop Shadow
                if block.key == b'dsdw':
                    effects['drop_shadow'] = {
                        'enabled': True,
                        'angle': getattr(block, 'angle', None),
                        'distance': getattr(block, 'distance', None),
                        'size': getattr(block, 'size', None),
                        'opacity': getattr(block, 'opacity', None)
                    }
                
                # Inner Shadow
                elif block.key == b'isdw':
                    effects['inner_shadow'] = {
                        'enabled': True,
                        'angle': getattr(block, 'angle', None),
                        'distance': getattr(block, 'distance', None),
                        'size': getattr(block, 'size', None)
                    }
                
                # Outer Glow
                elif block.key == b'oglw':
                    effects['outer_glow'] = {
                        'enabled': True,
                        'size': getattr(block, 'size', None),
                        'opacity': getattr(block, 'opacity', None)
                    }
                
                # Inner Glow
                elif block.key == b'iglw':
                    effects['inner_glow'] = {
                        'enabled': True,
                        'size': getattr(block, 'size', None)
                    }
                
                # Bevel and Emboss
                elif block.key == b'bevl':
                    effects['bevel_emboss'] = {
                        'enabled': True,
                        'depth': getattr(block, 'depth', None),
                        'size': getattr(block, 'size', None),
                        'angle': getattr(block, 'angle', None)
                    }
                
                # Satin
                elif block.key == b'sofi':
                    effects['satin'] = {'enabled': True}
                
                # Color Overlay
                elif block.key == b'SoCo':
                    effects['color_overlay'] = {
                        'enabled': True,
                        'opacity': getattr(block, 'opacity', None)
                    }
                
                # Gradient Overlay
                elif block.key == b'GrFl':
                    effects['gradient_overlay'] = {
                        'enabled': True,
                        'angle': getattr(block, 'angle', None),
                        'opacity': getattr(block, 'opacity', None)
                    }
                
                # Pattern Overlay
                elif block.key == b'patf':
                    effects['pattern_overlay'] = {'enabled': True}
                
                # Stroke
                elif block.key == b'FrFX':
                    effects['stroke'] = {
                        'enabled': True,
                        'size': getattr(block, 'size', None),
                        'opacity': getattr(block, 'opacity', None)
                    }
    
    except Exception as e:
        print(f"Aviso ao extrair efeitos: {e}")
    
    return effects

def process_layer(layer, layer_path: str = "") -> Dict[str, Any]:
    """Processa um layer e seus sub-layers recursivamente"""
    current_path = f"{layer_path}/{layer.name}" if layer_path else layer.name
    
    layer_data = {
        'name': layer.name,
        'path': current_path,
        'type': str(layer.kind) if hasattr(layer, 'kind') else 'unknown',
        'visible': layer.visible if hasattr(layer, 'visible') else True,
        'effects': extract_layer_effects(layer),
        'bounds': {
            'left': layer.left,
            'top': layer.top,
            'right': layer.right,
            'bottom': layer.bottom
        } if hasattr(layer, 'left') else None,
        'children': []
    }
    
    # Processar sub-layers se existirem
    if hasattr(layer, '__iter__'):
        for sublayer in layer:
            child_data = process_layer(sublayer, current_path)
            layer_data['children'].append(child_data)
    
    return layer_data

def extract_psd_effects(psd_path: str) -> Dict[str, Any]:
    """Extrai todos os efeitos de um arquivo PSD"""
    print(f"Processando: {psd_path}")
    
    psd = PSDImage.open(psd_path)
    
    output_data = {
        'filename': os.path.basename(psd_path),
        'width': psd.width,
        'height': psd.height,
        'color_mode': str(psd.color_mode) if hasattr(psd, 'color_mode') else 'unknown',
        'layers': []
    }
    
    # Processar todos os layers
    for layer in psd:
        layer_data = process_layer(layer)
        output_data['layers'].append(layer_data)
    
    return output_data

def main():
    """Função principal"""
    # Encontrar todos os arquivos PSD na pasta atual
    current_dir = Path('.')
    psd_files = list(current_dir.glob('*.psd'))
    
    if not psd_files:
        print("Nenhum arquivo PSD encontrado na pasta atual.")
        return
    
    print(f"Encontrados {len(psd_files)} arquivo(s) PSD")
    
    all_data = []
    
    for psd_file in psd_files:
        try:
            psd_data = extract_psd_effects(str(psd_file))
            all_data.append(psd_data)
        except Exception as e:
            print(f"Erro ao processar {psd_file}: {e}")
    
    # Salvar JSON
    output_file = 'psd_effects_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Dados extraídos com sucesso!")
    print(f"✓ JSON salvo em: {output_file}")
    print(f"✓ Total de arquivos processados: {len(all_data)}")

if __name__ == '__main__':
    # Instalar dependências necessárias:
    # pip install psd-tools
    
    main()
