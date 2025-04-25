from typing import List, Dict, Any, Optional
from storage import Storage
from oracle_gateway import OracleGateway
from utils import validar_float, print_erro, print_sucesso, print_alerta

class Estoque:
    def __init__(self, storage: Storage, oracle: OracleGateway):
        self.storage = storage
        self.oracle = oracle
        self.insumos = self._carregar_insumos()
    
    def _carregar_insumos(self) -> List[Dict[str, Any]]:
        """
        Carrega insumos do Oracle (se disponível) ou do JSON.
        """
        if self.oracle.conectar():
            insumos = self.oracle.listar_insumos()
            self.oracle.desconectar()
            if insumos:
                return insumos
        
        return self.storage.carregar_insumos()
    
    def _sincronizar(self):
        """
        Sincroniza os dados entre Oracle e JSON.
        """
        if self.oracle.conectar():
            for insumo in self.insumos:
                if not self.oracle.buscar_insumo(insumo['codigo']):
                    self.oracle.inserir_insumo(insumo)
                else:
                    self.oracle.atualizar_insumo(insumo['codigo'], insumo)
            self.oracle.desconectar()
        
        self.storage.salvar_insumos(self.insumos)
    
    def listar_insumos(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os insumos.
        """
        return self.insumos
    
    def buscar_insumo(self, codigo: int) -> Optional[Dict[str, Any]]:
        """
        Busca um insumo pelo código.
        """
        for insumo in self.insumos:
            if insumo['codigo'] == codigo:
                return insumo
        return None
    
    def adicionar_insumo(self, insumo: Dict[str, Any]) -> bool:
        """
        Adiciona um novo insumo.
        """
        if self.buscar_insumo(insumo['codigo']):
            print_erro("Código de insumo já existe.")
            return False
        
        self.insumos.append(insumo)
        self._sincronizar()
        print_sucesso("Insumo adicionado com sucesso.")
        return True
    
    def atualizar_insumo(self, codigo: int, novos_dados: Dict[str, Any]) -> bool:
        """
        Atualiza um insumo existente.
        """
        for i, insumo in enumerate(self.insumos):
            if insumo['codigo'] == codigo:
                self.insumos[i] = {**insumo, **novos_dados}
                self._sincronizar()
                print_sucesso("Insumo atualizado com sucesso.")
                return True
        
        print_erro("Insumo não encontrado.")
        return False
    
    def remover_insumo(self, codigo: int) -> bool:
        """
        Remove um insumo.
        """
        for i, insumo in enumerate(self.insumos):
            if insumo['codigo'] == codigo:
                del self.insumos[i]
                self._sincronizar()
                print_sucesso("Insumo removido com sucesso.")
                return True
        
        print_erro("Insumo não encontrado.")
        return False
    
    def registrar_entrada(self, codigo: int, quantidade: float) -> bool:
        """
        Registra entrada de insumo.
        """
        insumo = self.buscar_insumo(codigo)
        if not insumo:
            print_erro("Insumo não encontrado.")
            return False
        
        quantidade = validar_float(quantidade)
        if quantidade is None or quantidade <= 0:
            print_erro("Quantidade inválida.")
            return False
        
        insumo['quantidade'] += quantidade
        self._sincronizar()
        print_sucesso(f"Entrada de {quantidade} {insumo['unidade']} registrada.")
        return True
    
    def registrar_saida(self, codigo: int, quantidade: float) -> bool:
        """
        Registra saída de insumo.
        """
        insumo = self.buscar_insumo(codigo)
        if not insumo:
            print_erro("Insumo não encontrado.")
            return False
        
        quantidade = validar_float(quantidade)
        if quantidade is None or quantidade <= 0:
            print_erro("Quantidade inválida.")
            return False
        
        if insumo['quantidade'] < quantidade:
            print_erro("Quantidade insuficiente em estoque.")
            return False
        
        insumo['quantidade'] -= quantidade
        self._sincronizar()
        
        if insumo['quantidade'] <= insumo['nivel_min']:
            print_alerta(f"Atenção: Nível mínimo atingido para {insumo['nome']}!")
        
        print_sucesso(f"Saída de {quantidade} {insumo['unidade']} registrada.")
        return True
    
    def verificar_alertas(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de insumos com quantidade abaixo do nível mínimo.
        """
        return [
            {
                'codigo': insumo['codigo'],
                'nome': insumo['nome'],
                'quantidade': insumo['quantidade'],
                'unidade': insumo['unidade'],
                'nivel_min': insumo['nivel_min']
            }
            for insumo in self.insumos
            if insumo['quantidade'] <= insumo['nivel_min']
        ] 