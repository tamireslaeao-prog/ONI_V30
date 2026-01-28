"""
Script V4 - Leitura DIRETA do binário PSD
Bypassa psd-tools e lê os Layer Effects diretamente do arquivo
"""

import os
import json
import struct
from pathlib import Path
from psd_tools import PSDImage
from typing import Dict, List, Any

class PSDRawReader:
    """Leitor de dados brutos do PSD"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'rb') as f:
            self.data = f.read()
        self.pos = 0
    
    def read_bytes(self, n):
        """Lê n bytes"""
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result
    
    def read_int32(self):
        """Lê int de 4 bytes (big-endian)"""
        return struct.unpack('>i', self.read_bytes(4))[0]
    
    def read_uint32(self):
        """Lê unsigned int de 4 bytes"""
        return struct.unpack('>I', self.read_bytes(4))[0]
    
    def read_int16(self):
        """Lê int de 2 bytes"""
        return struct.unpack('>h', self.read_bytes(2))[0]
    
    def read_uint16(self):
        """Lê unsigned int de 2 bytes"""
        return struct.unpack('>H', self.read_bytes(2))[0]
    
    def read_uint8(self):
        """Lê byte"""
        return struct.unpack('>B', self.read_bytes(1))[0]
    
    def read_string(self, length):
        """Lê string de tamanho fixo"""
        return self.read_bytes(length).decode('latin-1', errors='ignore')
    
    def find_signature(self, sig):
        """Procura por uma signature no arquivo"""
        if isinstance(sig, str):
            sig = sig.encode('latin-1')
        idx = self.data.find(sig, self.pos)
        if idx != -1:
            self.pos = idx
            return True
        return False

def extract_effects_from_raw(psd_path):
    """Extrai efeitos lendo diretamente o binário"""
    reader = PSDRawReader(psd_path)
    effects_data = []
    
    # Procurar por signatures de Layer Effects
    effect_signatures = [
        b'dsdw',  # Drop Shadow
        b'isdw',  # Inner Shadow
        b'oglw',  # Outer Glow
        b'iglw',  # Inner Glow
        b'bevl',  # Bevel
        b'sofi',  # Satin
        b'SoCo',  # Color Overlay
        b'GrFl',  # Gradient Overlay
        b'FrFX',  # Stroke
    ]
    
    for sig in effect_signatures:
        # Resetar posição
        reader.pos = 0
        
        while reader.find_signature(sig):
            try:
                effect_type = sig.decode('latin-1')
                reader.pos += 4  # Skip signature
                
                # Tentar ler estrutura do efeito
                version = reader.read_uint32()
                
                effect_data = {
                    'type': effect_type,
                    'signature_position': reader.pos - 8,
                    'version': version,
                    'raw_values': {}
                }
                
                # Ler próximos valores (formato comum)
                try:
                    # Muitos efeitos têm blur/size logo depois
                    value1 = reader.read_int32()  # Pode ser blur, size, etc
                    value2 = reader.read_int32()  # Pode ser intensity, spread, etc
                    value3 = reader.read_int32()  # Pode ser angle
                    value4 = reader.read_int32()  # Pode ser distance
                    
                    effect_data['raw_values'] = {
                        'value1': value1,
                        'value2': value2, 
                        'value3': value3,
                        'value4': value4,
                        'value1_fixed': value1 / 65536.0,
                        'value2_fixed': value2 / 65536.0,
                        'value3_fixed': value3 / 65536.0,
                        'value4_fixed': value4 / 65536.0,
                    }
                except:
                    pass
                
                effects_data.append(effect_data)
                
            except:
                reader.pos += 1  # Continuar procurando
    
    return effects_data

def combine_psdtools_and_raw(psd_path):
    """Combina dados do psd-tools com leitura raw"""
    
    # Carregar com psd-tools
    psd = PSDImage.open(psd_path)
    
    # Extrair efeitos raw
    raw_effects = extract_effects_from_raw(psd_path)
    
    # Processar layers
    def process_layer(layer, path="", depth=0):
        current_path = f"{path}/{layer.name}" if path else layer.name
        
        layer_data = {
            'name': layer.name,
            'path': current_path,
            'type': str(getattr(layer, 'kind', 'unknown')),
            'visible': getattr(layer, 'visible', True),
            'blend_mode': str(getattr(layer, 'blend_mode', 'normal')),
            'opacity': getattr(layer, 'opacity', 255),
            'bounds': {
                'left': getattr(layer, 'left', 0),
                'top': getattr(layer, 'top', 0),
                'width': getattr(layer, 'width', 0),
                'height': getattr(layer, 'height', 0)
            },
            'effects_detected': {},
            'text': None,
            'children': []
        }
        
        # Tentar extrair efeitos via psd-tools
        try:
            if hasattr(layer, '_record') and layer._record:
                if hasattr(layer._record, 'tagged_blocks'):
                    for block in layer._record.tagged_blocks:
                        try:
                            # Capturar QUALQUER informação do bloco
                            block_info = {}
                            
                            # Tentar diferentes formas de acessar
                            for attr in ['key', 'tag', 'code', 'data', 'value']:
                                if hasattr(block, attr):
                                    val = getattr(block, attr)
                                    if val is not None:
                                        if isinstance(val, bytes):
                                            if len(val) < 50:
                                                block_info[attr] = val.hex()
                                            else:
                                                # Dados maiores - tentar parsear
                                                block_info[attr + '_hex'] = val[:100].hex()
                                                block_info[attr + '_len'] = len(val)
                                        else:
                                            block_info[attr] = str(val)[:200]
                            
                            if block_info:
                                block_key = block_info.get('key', block_info.get('tag', f'block_{len(layer_data["effects_detected"])}'))
                                layer_data['effects_detected'][block_key] = block_info
                        except:
                            pass
        except:
            pass
        
        # Adicionar texto
        if hasattr(layer, 'text'):
            layer_data['text'] = {
                'content': str(getattr(layer, 'text', ''))
            }
        
        # Processar filhos
        if hasattr(layer, '__iter__'):
            try:
                for sublayer in layer:
                    layer_data['children'].append(process_layer(sublayer, current_path, depth + 1))
            except:
                pass
        
        return layer_data
    
    result = {
        'filename': os.path.basename(psd_path),
        'width': psd.width,
        'height': psd.height,
        'raw_effects_found': raw_effects,
        'layers': [process_layer(layer) for layer in psd]
    }
    
    return result

def main():
    """Função principal"""
    psd_files = list(Path('.').glob('*.psd'))
    
    if not psd_files:
        print("❌ Nenhum PSD encontrado!")
        return
    
    output_dir = Path('psd_raw_extraction')
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n🔍 Encontrados {len(psd_files)} arquivo(s) PSD")
    print(f"🔬 Usando leitura DIRETA do binário + psd-tools\n")
    
    for psd_file in psd_files:
        try:
            print(f"{'='*70}")
            print(f"📂 Processando: {psd_file.name}")
            print(f"{'='*70}")
            
            # Combinar métodos
            data = combine_psdtools_and_raw(str(psd_file))
            
            # Salvar JSON
            json_path = output_dir / f"{psd_file.stem}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            size_kb = os.path.getsize(json_path) / 1024
            
            # Estatísticas
            effects_count = len(data.get('raw_effects_found', []))
            print(f"✅ Efeitos brutos encontrados: {effects_count}")
            print(f"✅ Salvo: {json_path.name} ({size_kb:.1f} KB)\n")
            
        except Exception as e:
            print(f"❌ Erro: {e}\n")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    print(f"✅ CONCLUÍDO!")
    print(f"{'='*70}")
    print(f"📁 Pasta de saída: {output_dir}/")
    print(f"\n💡 O JSON contém:")
    print(f"   • 'raw_effects_found' - Efeitos encontrados no binário")
    print(f"   • 'layers.effects_detected' - Blocos detectados por layer")
    print(f"   • Valores em hexadecimal + tentativas de conversão")

if __name__ == '__main__':
    main()
