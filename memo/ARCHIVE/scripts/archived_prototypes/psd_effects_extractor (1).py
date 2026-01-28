"""
Script COMPLETO para extrair TODOS os efeitos de PSD
Usando acesso direto às estruturas internas do arquivo
"""

import os
import json
from pathlib import Path
from psd_tools import PSDImage
from psd_tools.psd.tagged_blocks import TaggedBlocks
from typing import Dict, List, Any

def parse_descriptor(desc) -> Dict[str, Any]:
    """Converte um Descriptor do PSD em dicionário Python"""
    if desc is None:
        return {}
    
    result = {}
    try:
        if hasattr(desc, 'items'):
            for key, value in desc.items():
                # Processar diferentes tipos de valores
                if hasattr(value, 'items'):  # Outro descriptor
                    result[key] = parse_descriptor(value)
                elif isinstance(value, (list, tuple)):
                    result[key] = [parse_descriptor(v) if hasattr(v, 'items') else v for v in value]
                elif hasattr(value, 'value'):  # Objeto com propriedade value
                    result[key] = value.value
                elif hasattr(value, '__dict__'):  # Objeto complexo
                    result[key] = {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
                else:
                    result[key] = value
    except Exception as e:
        print(f"    ⚠ Erro ao parsear descriptor: {e}")
    
    return result

def extract_all_effects(layer) -> Dict[str, Any]:
    """Extrai TODOS os efeitos usando acesso direto aos tagged blocks"""
    all_effects = {
        'blend_mode': str(layer.blend_mode) if hasattr(layer, 'blend_mode') else 'normal',
        'opacity': layer.opacity if hasattr(layer, 'opacity') else 255,
        'fill_opacity': None,
        'layer_effects': {}
    }
    
    if not hasattr(layer, '_record') or not layer._record:
        return all_effects
    
    try:
        # Percorrer TODOS os tagged blocks
        if hasattr(layer._record, 'tagged_blocks'):
            for block in layer._record.tagged_blocks:
                block_key = block.key.decode('latin-1') if isinstance(block.key, bytes) else str(block.key)
                
                # Capturar dados brutos do bloco
                block_data = {}
                
                # Tentar extrair todos os atributos do bloco
                for attr in dir(block):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(block, attr)
                            if not callable(value):
                                # Converter objetos complexos
                                if hasattr(value, '__dict__'):
                                    block_data[attr] = {k: v for k, v in value.__dict__.items() 
                                                       if not k.startswith('_')}
                                elif hasattr(value, 'items'):
                                    block_data[attr] = parse_descriptor(value)
                                elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                                    block_data[attr] = value
                        except:
                            pass
                
                # Armazenar informações do bloco
                if block_data:
                    all_effects['layer_effects'][block_key] = block_data
                
                # Tentar acessar data específica de efeitos
                if hasattr(block, 'data'):
                    try:
                        data = block.data
                        effects_data = parse_descriptor(data) if hasattr(data, 'items') else {}
                        
                        if effects_data:
                            all_effects['layer_effects'][f'{block_key}_data'] = effects_data
                    except:
                        pass
    
    except Exception as e:
        print(f"    ⚠ Erro ao extrair efeitos: {e}")
    
    return all_effects

def extract_text_complete(layer) -> Dict[str, Any]:
    """Extrai TODOS os dados de texto"""
    if not hasattr(layer, 'text'):
        return None
    
    text_info = {
        'content': str(layer.text) if layer.text else '',
        'raw_data': {}
    }
    
    try:
        # Extrair engine_dict completo
        if hasattr(layer, 'engine_dict'):
            text_info['engine_dict'] = parse_descriptor(layer.engine_dict)
        
        # Extrair resource_dict completo
        if hasattr(layer, 'resource_dict'):
            text_info['resource_dict'] = parse_descriptor(layer.resource_dict)
        
        # Extrair warp
        if hasattr(layer, 'warp'):
            text_info['warp'] = parse_descriptor(layer.warp)
        
        # Extrair transform
        if hasattr(layer, 'transform'):
            text_info['transform'] = list(layer.transform) if layer.transform else None
            
    except Exception as e:
        print(f"    ⚠ Erro ao extrair texto: {e}")
    
    return text_info

def extract_vector_data(layer) -> Dict[str, Any]:
    """Extrai dados de vetores e shapes"""
    vector_info = {}
    
    try:
        if hasattr(layer, 'vector_mask'):
            vector_info['vector_mask'] = parse_descriptor(layer.vector_mask)
        
        if hasattr(layer, 'origination'):
            vector_info['origination'] = parse_descriptor(layer.origination)
            
        # Extrair todos os tagged blocks relacionados a vetores
        if hasattr(layer, '_record') and hasattr(layer._record, 'tagged_blocks'):
            for block in layer._record.tagged_blocks:
                if block.key in [b'vstk', b'vscg', b'SoCo', b'GdFl', b'PtFl', b'vmsk', b'vsms']:
                    block_key = block.key.decode('latin-1')
                    block_data = {}
                    
                    for attr in dir(block):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(block, attr)
                                if not callable(value):
                                    if hasattr(value, '__dict__'):
                                        block_data[attr] = {k: v for k, v in value.__dict__.items() 
                                                           if not k.startswith('_')}
                                    elif isinstance(value, (str, int, float, bool, list, dict, type(None))):
                                        block_data[attr] = value
                            except:
                                pass
                    
                    if block_data:
                        vector_info[block_key] = block_data
    
    except Exception as e:
        print(f"    ⚠ Erro ao extrair vetores: {e}")
    
    return vector_info if vector_info else None

def extract_all_tagged_blocks(layer) -> Dict[str, Any]:
    """Extrai TODOS os tagged blocks sem filtro"""
    all_blocks = {}
    
    if not hasattr(layer, '_record') or not hasattr(layer._record, 'tagged_blocks'):
        return all_blocks
    
    for block in layer._record.tagged_blocks:
        try:
            block_key = block.key.decode('latin-1') if isinstance(block.key, bytes) else str(block.key)
            
            block_info = {
                'key_hex': block.key.hex() if isinstance(block.key, bytes) else block_key,
                'attributes': {}
            }
            
            # Extrair TODOS os atributos
            for attr in dir(block):
                if not attr.startswith('_') and attr not in ['read', 'write', 'key']:
                    try:
                        value = getattr(block, attr)
                        if not callable(value):
                            if hasattr(value, 'items'):
                                block_info['attributes'][attr] = parse_descriptor(value)
                            elif hasattr(value, '__dict__'):
                                block_info['attributes'][attr] = str(value.__dict__)[:500]  # Limitar tamanho
                            elif isinstance(value, (str, int, float, bool, type(None))):
                                block_info['attributes'][attr] = value
                            elif isinstance(value, bytes):
                                block_info['attributes'][attr] = value.hex()[:100]
                            else:
                                block_info['attributes'][attr] = str(type(value))
                    except Exception as e:
                        block_info['attributes'][attr] = f"Error: {str(e)}"
            
            all_blocks[block_key] = block_info
            
        except Exception as e:
            print(f"    ⚠ Erro ao processar bloco: {e}")
    
    return all_blocks

def process_layer_complete(layer, layer_path: str = "", depth: int = 0) -> Dict[str, Any]:
    """Processa layer com MÁXIMA extração de dados"""
    current_path = f"{layer_path}/{layer.name}" if layer_path else layer.name
    
    print("  " * depth + f"📄 {layer.name} ({layer.kind if hasattr(layer, 'kind') else 'unknown'})")
    
    layer_data = {
        'name': layer.name,
        'path': current_path,
        'type': str(layer.kind) if hasattr(layer, 'kind') else 'unknown',
        'visible': layer.visible if hasattr(layer, 'visible') else True,
        'bounds': {
            'left': layer.left if hasattr(layer, 'left') else 0,
            'top': layer.top if hasattr(layer, 'top') else 0,
            'right': layer.right if hasattr(layer, 'right') else 0,
            'bottom': layer.bottom if hasattr(layer, 'bottom') else 0,
            'width': layer.width if hasattr(layer, 'width') else 0,
            'height': layer.height if hasattr(layer, 'height') else 0
        },
        'effects': extract_all_effects(layer),
        'all_tagged_blocks': extract_all_tagged_blocks(layer),
        'text_data': extract_text_complete(layer) if hasattr(layer, 'text') else None,
        'vector_data': extract_vector_data(layer),
        'children': []
    }
    
    # Processar filhos recursivamente
    if hasattr(layer, '__iter__'):
        try:
            for sublayer in layer:
                child_data = process_layer_complete(sublayer, current_path, depth + 1)
                layer_data['children'].append(child_data)
        except:
            pass
    
    return layer_data

def extract_psd_maximum(psd_path: str) -> Dict[str, Any]:
    """Extração MÁXIMA de dados do PSD"""
    print(f"\n{'='*70}")
    print(f"📂 PROCESSANDO: {psd_path}")
    print(f"{'='*70}\n")
    
    psd = PSDImage.open(psd_path)
    
    output_data = {
        'filename': os.path.basename(psd_path),
        'metadata': {
            'width': psd.width,
            'height': psd.height,
            'channels': psd.channels if hasattr(psd, 'channels') else 0,
            'depth': psd.depth if hasattr(psd, 'depth') else 8,
            'color_mode': str(psd.color_mode) if hasattr(psd, 'color_mode') else 'RGB',
        },
        'layers': []
    }
    
    # Processar layers
    layer_count = 0
    for layer in psd:
        layer_data = process_layer_complete(layer)
        output_data['layers'].append(layer_data)
        layer_count += 1
    
    print(f"\n✅ Total de layers processados: {layer_count}")
    
    return output_data

def main():
    """Função principal"""
    current_dir = Path('.')
    psd_files = list(current_dir.glob('*.psd'))
    
    if not psd_files:
        print("❌ Nenhum arquivo PSD encontrado!")
        return
    
    print(f"\n🔍 Encontrados {len(psd_files)} arquivo(s) PSD")
    
    all_data = []
    
    for psd_file in psd_files:
        try:
            psd_data = extract_psd_maximum(str(psd_file))
            all_data.append(psd_data)
        except Exception as e:
            print(f"\n❌ ERRO ao processar {psd_file}:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Salvar JSON
    output_file = 'psd_maximum_extraction.json'
    
    print(f"\n{'='*70}")
    print(f"💾 Salvando dados...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    
    print(f"{'='*70}")
    print(f"✅ EXTRAÇÃO COMPLETA!")
    print(f"{'='*70}")
    print(f"📊 Arquivos processados: {len(all_data)}")
    print(f"💾 Arquivo gerado: {output_file}")
    print(f"📦 Tamanho: {file_size:.2f} MB")
    print(f"\n🎯 Dados extraídos:")
    print(f"   ✓ TODOS os tagged blocks (sem filtro)")
    print(f"   ✓ Todos os layer effects com metadados completos")
    print(f"   ✓ Engine dict e resource dict de textos")
    print(f"   ✓ Dados de vetores e shapes")
    print(f"   ✓ Hierarquia completa de layers")
    print(f"   ✓ Geometria e bounds")

if __name__ == '__main__':
    # pip install psd-tools
    main()
