"""
Script V3 - DEEP DECODER
Extrai valores numéricos reais (não apenas Hex) dos efeitos do PSD.
Requer: pip install psd-tools
"""

import os
import json
from pathlib import Path
from psd_tools import PSDImage
# Importações para checagem de tipos específicos do psd_tools
try:
    from psd_tools.psd.descriptor import Descriptor, List, Integer, Double, UnitFloat, Boolean, String, Enum, Reference, Class, Alias, ObjectArray, RawData
except ImportError:
    pass # Falha silenciosa se não detalhado, usaremos duck-typing

def safe_get_attr(obj, attr, default=None):
    try:
        return getattr(obj, attr, default)
    except:
        return default

def decode_descriptor(obj):
    """
    Função recursiva MÁGICA para transformar objetos complexos do psd-tools
    em dicionários/listas limpas com valores reais.
    """
    # 1. Dicionários e Descriptors
    if hasattr(obj, 'items') and callable(obj.items):
        data = {}
        for k, v in obj.items():
            # Limpar chave (bytes p/ str)
            key = k.decode('latin-1') if isinstance(k, bytes) else str(k)
            key = key.strip()
            data[key] = decode_descriptor(v)
        return data

    # 2. Listas
    if isinstance(obj, list) or (hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes))):
        return [decode_descriptor(x) for x in obj]

    # 3. Tipos Primitivos do Photoshop (UnitFloat, Double, Integer)
    # UnitFloat geralmente tem .value e .unit
    if hasattr(obj, 'value') and hasattr(obj, 'unit'):
        return {
            'value': obj.value,
            'unit': str(obj.unit).split('.')[-1] # Ex: 'PERCENT'
        }
    
    # Enum (geralmente tem .type e .enum)
    if hasattr(obj, 'items') and not callable(obj.items): # Alguns Enums se comportam assim
        return str(obj)

    # 4. Valores com propriedade .value direta (Integer, Double, Boolean)
    if hasattr(obj, 'value'):
        return obj.value

    # 5. Bytes (Converter para Hex se for longo, ou ignorar)
    if isinstance(obj, bytes):
        if len(obj) < 50:
             try:
                 return obj.decode('latin-1')
             except:
                 pass
        return "HEX_DATA_" + obj.hex()[:20] + "..."

    # 6. Fallback para String
    return str(obj)

def extract_layer_effects(layer):
    effects = {
        'blend_mode': str(safe_get_attr(layer, 'blend_mode', 'normal')),
        'opacity': safe_get_attr(layer, 'opacity', 255),
        'visible': safe_get_attr(layer, 'visible', True),
        'effects_deep': {} 
    }
    
    # Acessar Tagged Blocks
    blocks = None
    try:
        if hasattr(layer, '_record') and layer._record:
            record = layer._record
            if hasattr(record, 'tagged_blocks'): blocks = record.tagged_blocks
            elif hasattr(record, '_tagged_blocks'): blocks = record._tagged_blocks
            
            if blocks:
                for block in blocks:
                    key = None
                    # Descobrir chave (DrSh, IrSh, ebbl, etc.)
                    if hasattr(block, 'key'): key = block.key
                    elif hasattr(block, 'code'): key = block.code
                    
                    if key:
                        if isinstance(key, bytes): 
                            key = key.decode('latin-1').strip()
                        
                        # Se for um bloco de efeitos (ObjectBasedEffects ou similar)
                        # Geralmente contém um 'descriptor' dentro
                        if hasattr(block, 'descriptor'):
                            effects['effects_deep'][key] = decode_descriptor(block.descriptor)
                        elif hasattr(block, 'data'):
                             # Alguns blocos tem .data que pode ser um Descriptor
                             effects['effects_deep'][key] = decode_descriptor(block.data)
                        else:
                             # Tenta varrer atributos se não tiver descriptor explícito
                             pass 

    except Exception as e:
        effects['error'] = str(e)
        
    return effects

def process_layer(layer):
    return {
        'name': layer.name,
        'kind': str(layer.kind),
        'bounds': {
            'left': layer.left, 'top': layer.top, 
            'right': layer.right, 'bottom': layer.bottom
        },
        'effects': extract_layer_effects(layer),
        'layers': [process_layer(x) for x in layer] if layer.is_group() else []
    }

def main():
    current_dir = Path('.')
    psd_files = list(current_dir.glob('*.psd'))
    
    all_data = []
    
    print(f"🚀 Iniciando Extração V3 (Deep Decode)...")
    
    for f in psd_files:
        try:
            print(f"Processando: {f.name}")
            psd = PSDImage.open(f)
            data = {'filename': f.name, 'layers': []}
            for layer in psd:
                data['layers'].append(process_layer(layer))
            all_data.append(data)
        except Exception as e:
            print(f"Erro em {f}: {e}")

    with open('psd_decoded_v3.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
        
    print("✅ Concluído! Salvo em: psd_decoded_v3.json")

if __name__ == '__main__':
    main()
