"""
Script CORRIGIDO para extrair efeitos de PSD
Compatível com a estrutura real de psd-tools
"""

import os
import json
from pathlib import Path
from psd_tools import PSDImage
from typing import Dict, List, Any

def safe_get_attr(obj, attr, default=None):
    """Obtém atributo de forma segura"""
    try:
        return getattr(obj, attr, default)
    except:
        return default

def extract_layer_effects(layer) -> Dict[str, Any]:
    """Extrai efeitos básicos do layer"""
    effects = {
        'blend_mode': str(safe_get_attr(layer, 'blend_mode', 'normal')),
        'opacity': safe_get_attr(layer, 'opacity', 255),
        'visible': safe_get_attr(layer, 'visible', True),
        'effects_raw': {}
    }
    
    # Tentar extrair tagged_blocks de forma segura
    try:
        if hasattr(layer, '_record') and layer._record:
            record = layer._record
            
            # Tentar diferentes formas de acessar os blocos
            blocks = None
            if hasattr(record, 'tagged_blocks'):
                blocks = record.tagged_blocks
            elif hasattr(record, '_tagged_blocks'):
                blocks = record._tagged_blocks
            
            if blocks:
                for i, block in enumerate(blocks):
                    try:
                        # Extrair informações do bloco
                        block_info = {
                            'index': i,
                            'type': str(type(block).__name__),
                            'attributes': {}
                        }
                        
                        # Tentar pegar a chave do bloco
                        block_key = None
                        if hasattr(block, 'key'):
                            block_key = block.key
                        elif hasattr(block, 'tag'):
                            block_key = block.tag
                        elif hasattr(block, 'code'):
                            block_key = block.code
                        
                        if block_key:
                            if isinstance(block_key, bytes):
                                key_str = block_key.decode('latin-1', errors='ignore')
                            else:
                                key_str = str(block_key)
                            block_info['key'] = key_str
                        
                        # Extrair todos os atributos do bloco
                        for attr_name in dir(block):
                            if not attr_name.startswith('_') and attr_name not in ['read', 'write']:
                                try:
                                    attr_value = getattr(block, attr_name)
                                    if not callable(attr_value):
                                        # Serializar valor
                                        if isinstance(attr_value, (str, int, float, bool, type(None))):
                                            block_info['attributes'][attr_name] = attr_value
                                        elif isinstance(attr_value, bytes):
                                            block_info['attributes'][attr_name] = attr_value.hex()[:200]
                                        elif hasattr(attr_value, '__dict__'):
                                            block_info['attributes'][attr_name] = str(type(attr_value))
                                        else:
                                            block_info['attributes'][attr_name] = str(attr_value)[:200]
                                except:
                                    pass
                        
                        # Armazenar bloco
                        effects['effects_raw'][f'block_{i}'] = block_info
                        
                    except Exception as e:
                        effects['effects_raw'][f'block_{i}_error'] = str(e)
    
    except Exception as e:
        effects['extraction_error'] = str(e)
    
    return effects

def extract_text_data(layer) -> Dict[str, Any]:
    """Extrai dados de texto"""
    if not hasattr(layer, 'text'):
        return None
    
    text_data = {
        'content': str(safe_get_attr(layer, 'text', '')),
        'engine_dict': None,
        'resource_dict': None
    }
    
    try:
        if hasattr(layer, 'engine_dict'):
            ed = layer.engine_dict
            if ed and isinstance(ed, dict):
                text_data['engine_dict'] = {k: str(v)[:500] for k, v in ed.items()}
        
        if hasattr(layer, 'resource_dict'):
            rd = layer.resource_dict
            if rd and isinstance(rd, dict):
                text_data['resource_dict'] = {k: str(v)[:500] for k, v in rd.items()}
    except:
        pass
    
    return text_data

def process_layer(layer, layer_path: str = "", depth: int = 0) -> Dict[str, Any]:
    """Processa layer completo"""
    current_path = f"{layer_path}/{layer.name}" if layer_path else layer.name
    
    print("  " * depth + f"📄 {layer.name} ({safe_get_attr(layer, 'kind', 'unknown')})")
    
    layer_data = {
        'name': layer.name,
        'path': current_path,
        'type': str(safe_get_attr(layer, 'kind', 'unknown')),
        'visible': safe_get_attr(layer, 'visible', True),
        'bounds': {
            'left': safe_get_attr(layer, 'left', 0),
            'top': safe_get_attr(layer, 'top', 0),
            'right': safe_get_attr(layer, 'right', 0),
            'bottom': safe_get_attr(layer, 'bottom', 0),
            'width': safe_get_attr(layer, 'width', 0),
            'height': safe_get_attr(layer, 'height', 0)
        },
        'effects': extract_layer_effects(layer),
        'text_data': extract_text_data(layer),
        'children': []
    }
    
    # Processar filhos
    if hasattr(layer, '__iter__'):
        try:
            for sublayer in layer:
                child_data = process_layer(sublayer, current_path, depth + 1)
                layer_data['children'].append(child_data)
        except:
            pass
    
    return layer_data

def extract_psd_complete(psd_path: str) -> Dict[str, Any]:
    """Extração completa do PSD"""
    print(f"\n{'='*70}")
    print(f"📂 PROCESSANDO: {psd_path}")
    print(f"{'='*70}\n")
    
    psd = PSDImage.open(psd_path)
    
    output_data = {
        'filename': os.path.basename(psd_path),
        'metadata': {
            'width': psd.width,
            'height': psd.height,
            'channels': safe_get_attr(psd, 'channels', 0),
            'depth': safe_get_attr(psd, 'depth', 8),
            'color_mode': str(safe_get_attr(psd, 'color_mode', 'RGB')),
        },
        'layers': []
    }
    
    # Processar layers
    layer_count = 0
    for layer in psd:
        layer_data = process_layer(layer)
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
            psd_data = extract_psd_complete(str(psd_file))
            all_data.append(psd_data)
        except Exception as e:
            print(f"\n❌ ERRO ao processar {psd_file}:")
            print(f"   {str(e)}")
    
    # Salvar JSON
    output_file = 'psd_effects_extraction.json'
    
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
    print(f"   ✓ Hierarquia completa de layers")
    print(f"   ✓ Propriedades básicas (blend mode, opacity)")
    print(f"   ✓ Geometria e bounds")
    print(f"   ✓ Estrutura de tagged blocks")
    print(f"   ✓ Dados de texto (quando disponíveis)")
    print(f"\n⚠️  Nota: A biblioteca psd-tools tem limitações para")
    print(f"   extrair parâmetros detalhados de Layer Styles.")
    print(f"   Os dados brutos dos blocos estão em 'effects_raw'.")

if __name__ == '__main__':
    # pip install psd-tools
    main()
