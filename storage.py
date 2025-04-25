import json
import os
from typing import List, Dict, Any

class Storage:
    def __init__(self, arquivo: str = "data/estoque.json"):
        self.arquivo = arquivo
        self._criar_diretorio_se_nao_existir()
    
    def _criar_diretorio_se_nao_existir(self):
        """Cria o diretório data se não existir."""
        diretorio = os.path.dirname(self.arquivo)
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
    
    def carregar_insumos(self) -> List[Dict[str, Any]]:
        """
        Carrega os insumos do arquivo JSON.
        Retorna uma lista vazia se o arquivo não existir.
        """
        try:
            if os.path.exists(self.arquivo):
                with open(self.arquivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError:
            print(f"Erro ao ler o arquivo {self.arquivo}. Criando novo arquivo.")
        return []
    
    def salvar_insumos(self, insumos: List[Dict[str, Any]]) -> bool:
        """
        Salva os insumos no arquivo JSON.
        Retorna True se bem sucedido, False caso contrário.
        """
        try:
            with open(self.arquivo, 'w', encoding='utf-8') as f:
                json.dump(insumos, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar no arquivo {self.arquivo}: {str(e)}")
            return False
    
    def adicionar_insumo(self, insumo: Dict[str, Any]) -> bool:
        """
        Adiciona um novo insumo ao arquivo JSON.
        Retorna True se bem sucedido, False caso contrário.
        """
        insumos = self.carregar_insumos()
        insumos.append(insumo)
        return self.salvar_insumos(insumos)
    
    def atualizar_insumo(self, codigo: int, novos_dados: Dict[str, Any]) -> bool:
        """
        Atualiza um insumo existente no arquivo JSON.
        Retorna True se bem sucedido, False caso contrário.
        """
        insumos = self.carregar_insumos()
        for i, insumo in enumerate(insumos):
            if insumo['codigo'] == codigo:
                insumos[i] = {**insumo, **novos_dados}
                return self.salvar_insumos(insumos)
        return False
    
    def remover_insumo(self, codigo: int) -> bool:
        """
        Remove um insumo do arquivo JSON.
        Retorna True se bem sucedido, False caso contrário.
        """
        insumos = self.carregar_insumos()
        insumos = [i for i in insumos if i['codigo'] != codigo]
        return self.salvar_insumos(insumos)
    
    def buscar_insumo(self, codigo: int) -> Dict[str, Any]:
        """
        Busca um insumo pelo código.
        Retorna o insumo se encontrado, None caso contrário.
        """
        insumos = self.carregar_insumos()
        for insumo in insumos:
            if insumo['codigo'] == codigo:
                return insumo
        return None 