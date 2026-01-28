"""
Sistema de Controle Total do AutoCAD 2021 para IA
Permite envio de comandos sem bloqueios com execução completa
"""

import win32com.client
import pythoncom
import time
from typing import Any, List, Tuple, Optional
import threading
import queue


class AutoCADController:
    """Controlador completo do AutoCAD 2021"""
    
    def __init__(self):
        self.acad = None
        self.doc = None
        self.model_space = None
        self.command_queue = queue.Queue()
        self.running = False
        
    def connect(self) -> bool:
        """Conecta ao AutoCAD 2021"""
        try:
            # Inicializa COM
            pythoncom.CoInitialize()
            
            # Tenta conectar ao AutoCAD existente
            try:
                # CRITICAL: EnsureDispatch garante Early Binding (evita erro <unknown>)
                try:
                    self.acad = win32com.client.gencache.EnsureDispatch("AutoCAD.Application.24")
                except:
                    # Fallback generico
                    self.acad = win32com.client.gencache.EnsureDispatch("AutoCAD.Application")
                    
                print("✓ Conectado ao AutoCAD 2021 existente")
            except:
                # Se não existir, cria nova instância
                self.acad = win32com.client.Dispatch("AutoCAD.Application")
                print("✓ Nova instância do AutoCAD iniciada")
            
            # Torna visível
            self.acad.Visible = True
            
            # Obtém documento ativo ou cria novo
            try:
                self.doc = self.acad.ActiveDocument
            except:
                self.doc = self.acad.Documents.Add()
            
            self.model_space = self.doc.ModelSpace
            
            print("✓ Controle total estabelecido")
            return True
            
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}")
            return False
            
    def _retry_call(self, func, *args, **kwargs):
        """Executa função COM com retry automático para RPC_E_CALL_REJECTED"""
        for attempt in range(50):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 0x80010001 (Call Rejected) or -2147418111
                if "-2147418111" in str(e) or "80010001" in str(e): 
                    time.sleep(0.5)
                    if attempt == 49: 
                        print(f"✗ Falha após 50 tentativas: {e}")
                        raise e
                    continue
                raise e
    
    def send_command(self, command: str, wait: bool = True) -> bool:
        """
        Envia comando direto ao AutoCAD
        
        Args:
            command: Comando a ser executado
            wait: Aguardar conclusão
        """
        try:
            if not command.endswith('\n'):
                command += '\n'
            
            # RETRY LOGIC FOR RPC REJECTION
            for attempt in range(50):
                try:
                    self.doc.SendCommand(command)
                    break
                except Exception as e:
                    if "-2147418111" in str(e) or "80010001" in str(e): # RPC_E_CALL_REJECTED
                        time.sleep(0.5)
                        if attempt == 49: raise e
                        continue
                    raise e
            
            if wait:
                time.sleep(0.1)  # Pequeno delay para processamento
            
            return True
        except Exception as e:
            print(f"✗ Erro ao enviar comando: {e}")
            return False
    
    def execute_lisp(self, lisp_code: str) -> Any:
        """Executa código AutoLISP"""
        try:
            result = self.doc.Application.ActiveDocument.SendCommand(
                f"(command {lisp_code})\n"
            )
            return result
        except Exception as e:
            print(f"✗ Erro LISP: {e}")
            return None
    
    # ==================== OPERAÇÕES DE DESENHO ====================
    
    def draw_line(self, x1: float, y1: float, z1: float,
                  x2: float, y2: float, z2: float) -> Any:
        """Desenha linha"""
        try:
            def _action():
                p1 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x1, y1, z1])
                p2 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x2, y2, z2])
                return self.model_space.AddLine(p1, p2)
            
            line = self._retry_call(_action)
            # self.doc.Regen(1)
            return line
        except Exception as e:
            print(f"✗ Erro ao desenhar linha: {e}")
            return None
    
    def draw_circle(self, x: float, y: float, z: float, radius: float) -> Any:
        """Desenha círculo"""
        try:
            def _action():
                center = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y, z])
                return self.model_space.AddCircle(center, radius)
            
            circle = self._retry_call(_action)
            # self.doc.Regen(1)
            return circle
        except Exception as e:
            print(f"✗ Erro ao desenhar círculo: {e}")
            return None
    
    def draw_rectangle(self, x: float, y: float, width: float, height: float) -> Any:
        """Desenha retângulo"""
        try:
            def _action():
                p1 = [x, y, 0]
                p2 = [x + width, y, 0]
                p3 = [x + width, y + height, 0]
                p4 = [x, y + height, 0]
                
                points = [p1, p2, p3, p4, p1]
                flat_points = [coord for point in points for coord in point]
                
                pts = win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8, 
                    flat_points
                )
                
                pline = self.model_space.AddPolyline(pts)
                pline.Closed = True
                return pline
            
            pline = self._retry_call(_action)
            # self.doc.Regen(1)
            return pline
        except Exception as e:
            print(f"✗ Erro ao desenhar retângulo: {e}")
            return None
    
    def draw_text(self, text: str, x: float, y: float, z: float, height: float = 2.5) -> Any:
        """Adiciona texto"""
        try:
            def _action():
                point = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y, z])
                return self.model_space.AddText(text, point, height)
            
            text_obj = self._retry_call(_action)
            # self.doc.Regen(1)
            return text_obj
        except Exception as e:
            print(f"✗ Erro ao adicionar texto: {e}")
            return None
    
    def draw_polyline(self, points: List[Tuple[float, float, float]]) -> Any:
        """Desenha polilinha"""
        try:
            def _action():
                flat_points = [coord for point in points for coord in point]
                pts = win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8, 
                    flat_points
                )
                return self.model_space.AddPolyline(pts)
            
            pline = self._retry_call(_action)
            # self.doc.Regen(1)
            return pline
        except Exception as e:
            print(f"✗ Erro ao desenhar polilinha: {e}")
            return None

    def add_dim_aligned(self, x1: float, y1: float, z1: float,
                        x2: float, y2: float, z2: float,
                        x_text: float, y_text: float, z_text: float) -> Any:
        """Cria cota alinhada"""
        try:
            def _action():
                p1 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x1, y1, z1])
                p2 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x2, y2, z2])
                pt_text = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x_text, y_text, z_text])
                return self.model_space.AddDimAligned(p1, p2, pt_text)
            
            dim = self._retry_call(_action)
            # self.doc.Regen(1)
            return dim
        except Exception as e:
            print(f"✗ Erro ao criar cota: {e}")
            return None

    # ==================== OPERAÇÕES 3D SOLIDS ====================

    def add_box(self, x: float, y: float, z: float, length: float, width: float, height: float) -> Any:
        """Cria Box 3D"""
        try:
            origin = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y, z])
            box = self.model_space.AddBox(origin, length, width, height)
            return box
        except Exception as e:
            print(f"✗ Erro ao criar Box: {e}")
            return None

    def add_cylinder(self, x: float, y: float, z: float, radius: float, height: float) -> Any:
        """Cria Cilindro 3D"""
        try:
            center = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x, y, z])
            cyl = self.model_space.AddCylinder(center, radius, height)
            return cyl
        except Exception as e:
            print(f"✗ Erro ao criar Cilindro: {e}")
            return None

    def solid_boolean(self, target: Any, operation: str, tool: Any) -> bool:
        """
        Executa operacao booleana.
        Operations: 'UNION', 'SUBTRACT', 'INTERSECT'
        """
        try:
            op_map = {
                'UNION': 0,
                'INTERSECT': 1,
                'SUBTRACT': 2
            }
            if operation.upper() not in op_map:
                print(f"✗ Operação desconhecida: {operation}")
                return False
            
            target.Boolean(op_map[operation.upper()], tool)
            return True
        except Exception as e:
            print(f"✗ Erro Boolean: {e}")
            return False
    
    # ==================== OPERAÇÕES DE MODIFICAÇÃO ====================
    
    def move_entity(self, entity: Any, from_x: float, from_y: float, 
                    to_x: float, to_y: float) -> bool:
        """Move entidade"""
        try:
            from_pt = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_R8, 
                [from_x, from_y, 0]
            )
            to_pt = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_R8, 
                [to_x, to_y, 0]
            )
            entity.Move(from_pt, to_pt)
            self.doc.Regen(1)
            return True
        except Exception as e:
            print(f"✗ Erro ao mover: {e}")
            return False
    
    def rotate_entity(self, entity: Any, base_x: float, base_y: float, 
                      angle: float) -> bool:
        """Rotaciona entidade (ângulo em radianos) no plano XY"""
        try:
            base_pt = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_R8, 
                [base_x, base_y, 0]
            )
            entity.Rotate(base_pt, angle)
            self.doc.Regen(1)
            return True
        except Exception as e:
            print(f"✗ Erro ao rotacionar: {e}")
            return False

    def rotate3d_entity(self, entity: Any, x1: float, y1: float, z1: float, 
                        x2: float, y2: float, z2: float, angle: float) -> bool:
        """
        Rotaciona entidade em 3D (ângulo em radianos) em torno de eixo definido por p1 e p2.
        """
        try:
            p1 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x1, y1, z1])
            p2 = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [x2, y2, z2])
            entity.Rotate3D(p1, p2, angle)
            self.doc.Regen(1)
            return True
        except Exception as e:
            print(f"✗ Erro ao rotacionar 3D: {e}")
            return False
    
    def scale_entity(self, entity: Any, base_x: float, base_y: float, 
                     factor: float) -> bool:
        """Escala entidade"""
        try:
            base_pt = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_R8, 
                [base_x, base_y, 0]
            )
            entity.ScaleEntity(base_pt, factor)
            self.doc.Regen(1)
            return True
        except Exception as e:
            print(f"✗ Erro ao escalar: {e}")
            return False
    
    def delete_entity(self, entity: Any) -> bool:
        """Deleta entidade"""
        try:
            entity.Delete()
            self.doc.Regen(1)
            return True
        except Exception as e:
            print(f"✗ Erro ao deletar: {e}")
            return False
    
    # ==================== OPERAÇÕES DE LAYER ====================
    
    def create_layer(self, name: str, color: int = 7) -> Any:
        """Cria novo layer"""
        try:
            def _action():
                return self.doc.Layers.Add(name)
            
            layer = self._retry_call(_action)
            layer.color = color
            return layer
        except Exception as e:
            print(f"✗ Erro ao criar layer: {e}")
            return None
    
    def set_active_layer(self, name: str) -> bool:
        """Define layer ativo"""
        try:
            def _action():
                self.doc.ActiveLayer = self.doc.Layers.Item(name)
            
            self._retry_call(_action)
            return True
        except Exception as e:
            print(f"✗ Erro ao ativar layer: {e}")
            return False
    
    # ==================== OPERAÇÕES DE VISUALIZAÇÃO ====================
    
    def zoom_extents(self) -> bool:
        """Zoom extents"""
        try:
            self.send_command("ZOOM E ")
            return True
        except Exception as e:
            print(f"✗ Erro no zoom: {e}")
            return False
    
    def zoom_window(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Zoom window"""
        try:
            self.send_command(f"ZOOM W {x1},{y1} {x2},{y2} ")
            return True
        except Exception as e:
            print(f"✗ Erro no zoom window: {e}")
            return False
    
    def regen(self) -> bool:
        """Regenera desenho"""
        try:
            self.doc.Regen(1)
            return True
        except Exception as e:
            print(f"✗ Erro no regen: {e}")
            return False
    
    # ==================== OPERAÇÕES DE ARQUIVO ====================
    
    def save_as(self, filepath: str) -> bool:
        """Salva desenho"""
        try:
            self.doc.SaveAs(filepath)
            print(f"✓ Salvo em: {filepath}")
            return True
        except Exception as e:
            print(f"✗ Erro ao salvar: {e}")
            return False
    
    def open_drawing(self, filepath: str) -> bool:
        """Abre desenho"""
        try:
            self.doc = self.acad.Documents.Open(filepath)
            self.model_space = self.doc.ModelSpace
            print(f"✓ Aberto: {filepath}")
            return True
        except Exception as e:
            print(f"✗ Erro ao abrir: {e}")
            return False
    
    def new_drawing(self) -> bool:
        """Cria novo desenho"""
        try:
            self.doc = self.acad.Documents.Add()
            self.model_space = self.doc.ModelSpace
            print("✓ Novo desenho criado")
            return True
        except Exception as e:
            print(f"✗ Erro ao criar: {e}")
            return False
    
    # ==================== SISTEMA DE FILA DE COMANDOS ====================
    
    def start_command_processor(self):
        """Inicia processador de comandos em thread separada"""
        self.running = True
        thread = threading.Thread(target=self._process_commands, daemon=True)
        thread.start()
        print("✓ Processador de comandos iniciado")
    
    def _process_commands(self):
        """Processa comandos da fila"""
        # CRITICAL: Inicializa COM na nova thread
        pythoncom.CoInitialize()
        
        while self.running:
            try:
                if not self.command_queue.empty():
                    cmd_data = self.command_queue.get(timeout=0.1)
                    cmd_type = cmd_data.get('type')
                    
                    try:
                        if cmd_type == 'command':
                            self.send_command(cmd_data['command'])
                        elif cmd_type == 'function':
                            func = cmd_data['function']
                            args = cmd_data.get('args', ())
                            kwargs = cmd_data.get('kwargs', {})
                            func(*args, **kwargs)
                    except Exception as e:
                        print(f"✗ Erro executando item da fila: {e}")
                        
                else:
                    time.sleep(0.01)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"✗ Erro no processador: {e}")
        
        # Opcional: Desinicializa ao sair
        pythoncom.CoUninitialize()
    
    def queue_command(self, command: str):
        """Adiciona comando à fila"""
        self.command_queue.put({'type': 'command', 'command': command})
    
    def queue_function(self, func, *args, **kwargs):
        """Adiciona função à fila"""
        self.command_queue.put({
            'type': 'function',
            'function': func,
            'args': args,
            'kwargs': kwargs
        })
    
    def stop_command_processor(self):
        """Para processador de comandos"""
        self.running = False
        print("✓ Processador parado")
    
    # ==================== UTILIDADES ====================
    
    def get_all_entities(self) -> List[Any]:
        """Retorna todas as entidades do model space"""
        entities = []
        try:
            for entity in self.model_space:
                entities.append(entity)
        except Exception as e:
            print(f"✗ Erro ao obter entidades: {e}")
        return entities
    
    def clear_drawing(self) -> bool:
        """Limpa todo o desenho"""
        try:
            entities = self.get_all_entities()
            for entity in entities:
                entity.Delete()
            self.doc.Regen(1)
            print("✓ Desenho limpo")
            return True
        except Exception as e:
            print(f"✗ Erro ao limpar: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do AutoCAD"""
        try:
            self.stop_command_processor()
            pythoncom.CoUninitialize()
            print("✓ Desconectado")
        except Exception as e:
            print(f"✗ Erro ao desconectar: {e}")


# ==================== EXEMPLO DE USO ====================

if __name__ == "__main__":
    # Inicializa controlador
    cad = AutoCADController()
    
    if cad.connect():
        print("\n=== SISTEMA PRONTO PARA IA ===\n")
        
        # Exemplo: Desenhos básicos
        print("Desenhando elementos...")
        cad.draw_line(0, 0, 0, 100, 0, 0)
        cad.draw_circle(50, 50, 0, 25)
        cad.draw_rectangle(10, 10, 80, 30)
        cad.draw_text("Controle IA", 20, 60, 0, 5)
        
        # Exemplo: Comandos diretos
        print("\nExecutando comandos...")
        cad.send_command("CIRCLE 150,150 20")
        cad.send_command("LINE 0,0 200,200 ")
        
        # Exemplo: Sistema de fila (THREADING DESATIVADO POR QUESTOES DE COM MARSHALLING)
        # print("\nIniciando sistema de fila...")
        # cad.start_command_processor()
        
        # for i in range(5):
        #     cad.queue_function(cad.draw_circle, 50*i, 100, 0, 10)
        
        # Zoom extents
        time.sleep(1)
        cad.zoom_extents()
        
        print("\n✓ Sistema funcionando! Pronto para receber comandos da IA")
        print("\n✓ Sistema funcionando! Pronto para receber comandos da IA")
        # print("Pressione Ctrl+C para encerrar")
        
        # Desconecta e finaliza para teste automatizado
        cad.disconnect()
        print("Teste concluído com sucesso.")

