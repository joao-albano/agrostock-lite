import logging
from typing import List, Dict, Any, Optional, Union
import cx_Oracle

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oracle_gateway')

class OracleGateway:
    def __init__(
        self,
        username: str = "agrostock",
        password: str = "agrostock123",
        host: str = "localhost",
        port: int = 1521,
        service_name: str = "XE",
        # Parâmetros antigos para compatibilidade
        usuario: str = None,
        senha: str = None,
        dsn: str = None
    ):
        """
        Inicializa o gateway para o banco de dados Oracle.
        
        Args:
            username: Nome de usuário para conexão
            password: Senha para conexão
            host: Endereço do servidor Oracle
            port: Porta do servidor Oracle
            service_name: Nome do serviço Oracle
            
            # Parâmetros antigos (para compatibilidade)
            usuario: Nome de usuário (alternativa em português)
            senha: Senha de usuário (alternativa em português)
            dsn: String de conexão completa (ex: "localhost:1521/XE")
        """
        # Priorizar parâmetros em português se fornecidos (para compatibilidade)
        if usuario is not None:
            self.username = usuario
        else:
            self.username = username
            
        if senha is not None:
            self.password = senha
        else:
            self.password = password
            
        # Se dsn for fornecido, usar diretamente
        if dsn is not None:
            self.dsn = dsn
            self.host = None
            self.port = None
            self.service_name = None
        else:
            self.host = host
            self.port = port
            self.service_name = service_name
            self.dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        
        self.connection = None
        
        # Tentar iniciar o cliente Oracle automaticamente (opcional)
        try:
            cx_Oracle.init_oracle_client()
            logger.info("Oracle Client inicializado automaticamente.")
        except Exception as e:
            # Se falhar, assumimos que o cliente já está inicializado ou precisa ser configurado manualmente
            logger.warning(f"Atenção ao inicializar cliente Oracle: {str(e)}")
    
    def conectar(self) -> bool:
        """
        Estabelece a conexão com o banco de dados Oracle.
        
        Returns:
            bool: True se a conexão foi estabelecida com sucesso, False caso contrário.
        """
        try:
            if self.connection and not self.connection.ping():
                # Conexão existente mas inválida
                self.connection = None
                
            if not self.connection:
                self.connection = cx_Oracle.connect(
                    user=self.username,
                    password=self.password,
                    dsn=self.dsn,
                    encoding="UTF-8"
                )
                logger.info("Conexão com Oracle estabelecida com sucesso.")
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logger.error(f"Erro ao conectar ao Oracle: {error.message}")
            return False
    
    def desconectar(self) -> None:
        """
        Encerra a conexão com o banco de dados Oracle.
        """
        if self.connection:
            try:
                self.connection.close()
                logger.info("Conexão com Oracle encerrada.")
            except cx_Oracle.DatabaseError as e:
                error, = e.args
                logger.error(f"Erro ao desconectar do Oracle: {error.message}")
            finally:
                self.connection = None
    
    def executar_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Executa uma consulta SQL no banco de dados.
        
        Args:
            sql: String SQL a ser executada
            params: Parâmetros para a consulta (opcional)
            
        Returns:
            List[Dict[str, Any]]: Lista de resultados como dicionários ou None em caso de erro
        """
        if not self.conectar():
            return None
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Obter nomes das colunas
            columns = [col[0].lower() for col in cursor.description] if cursor.description else []
            
            # Converter resultados para lista de dicionários
            results = []
            for row in cursor:
                results.append({columns[i]: row[i] for i in range(len(columns))})
            
            cursor.close()
            return results
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logger.error(f"Erro ao executar query: {error.message}")
            logger.error(f"SQL: {sql}")
            if params:
                logger.error(f"Parâmetros: {params}")
            return None
    
    def executar_dml(self, sql: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Executa uma operação DML (INSERT, UPDATE, DELETE) no banco de dados.
        
        Args:
            sql: String SQL a ser executada
            params: Parâmetros para a operação (opcional)
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.conectar():
            return False
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Operação DML executada com sucesso. Linhas afetadas: {affected_rows}")
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logger.error(f"Erro ao executar DML: {error.message}")
            logger.error(f"SQL: {sql}")
            if params:
                logger.error(f"Parâmetros: {params}")
            
            try:
                self.connection.rollback()
            except:
                pass
            
            return False
    
    # --- Métodos específicos para a aplicação ---
    
    def listar_insumos(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os insumos cadastrados.
        
        Returns:
            List[Dict[str, Any]]: Lista de insumos
        """
        sql = """
        SELECT 
            CODIGO, NOME, QUANTIDADE, UNIDADE, PRECO_UNIT, NIVEL_MIN,
            DATA_CRIACAO, DATA_ATUALIZACAO
        FROM INSUMOS
        ORDER BY NOME
        """
        
        resultados = self.executar_query(sql)
        return resultados if resultados else []
    
    def buscar_insumo(self, codigo: int) -> Optional[Dict[str, Any]]:
        """
        Busca um insumo pelo código.
        
        Args:
            codigo: Código do insumo
            
        Returns:
            Dict[str, Any]: Dados do insumo ou None se não encontrado
        """
        sql = """
        SELECT 
            CODIGO, NOME, QUANTIDADE, UNIDADE, PRECO_UNIT, NIVEL_MIN,
            DATA_CRIACAO, DATA_ATUALIZACAO
        FROM INSUMOS
        WHERE CODIGO = :codigo
        """
        
        resultados = self.executar_query(sql, {"codigo": codigo})
        return resultados[0] if resultados else None
    
    def inserir_insumo(self, insumo: Dict[str, Any]) -> bool:
        """
        Insere um novo insumo no banco de dados.
        
        Args:
            insumo: Dicionário com os dados do insumo
            
        Returns:
            bool: True se a inserção foi bem-sucedida, False caso contrário
        """
        sql = """
        INSERT INTO INSUMOS (
            CODIGO, NOME, QUANTIDADE, UNIDADE, PRECO_UNIT, NIVEL_MIN
        ) VALUES (
            :codigo, :nome, :quantidade, :unidade, :preco_unit, :nivel_min
        )
        """
        
        return self.executar_dml(sql, {
            "codigo": insumo.get('codigo'),
            "nome": insumo.get('nome'),
            "quantidade": insumo.get('quantidade'),
            "unidade": insumo.get('unidade'),
            "preco_unit": insumo.get('preco_unit'),
            "nivel_min": insumo.get('nivel_min')
        })
    
    def atualizar_insumo(self, codigo: int, insumo: Dict[str, Any]) -> bool:
        """
        Atualiza os dados de um insumo existente.
        
        Args:
            codigo: Código do insumo a ser atualizado
            insumo: Dicionário com os novos dados do insumo
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        # Construir a query dinamicamente com base nos campos fornecidos
        campos_update = []
        params = {"codigo": codigo}
        
        # Mapear campos permitidos para atualização
        campos_permitidos = {
            'nome': 'NOME',
            'quantidade': 'QUANTIDADE',
            'unidade': 'UNIDADE',
            'preco_unit': 'PRECO_UNIT',
            'nivel_min': 'NIVEL_MIN'
        }
        
        # Adicionar apenas campos presentes no insumo
        for campo, coluna in campos_permitidos.items():
            if campo in insumo:
                campos_update.append(f"{coluna} = :{campo}")
                params[campo] = insumo[campo]
        
        # Se não houver campos para atualizar, retorna False
        if not campos_update:
            logger.warning("Atualização de insumo solicitada sem campos para atualizar.")
            return False
        
        # Construir e executar a query
        sql = f"""
        UPDATE INSUMOS
        SET {', '.join(campos_update)}
        WHERE CODIGO = :codigo
        """
        
        return self.executar_dml(sql, params)
    
    def remover_insumo(self, codigo: int) -> bool:
        """
        Remove um insumo do banco de dados.
        
        Args:
            codigo: Código do insumo a ser removido
            
        Returns:
            bool: True se a remoção foi bem-sucedida, False caso contrário
        """
        sql = "DELETE FROM INSUMOS WHERE CODIGO = :codigo"
        return self.executar_dml(sql, {"codigo": codigo})
    
    def registrar_entrada(self, codigo: int, quantidade: float) -> bool:
        """
        Registra entrada de insumo utilizando o procedimento armazenado.
        
        Args:
            codigo: Código do insumo
            quantidade: Quantidade a ser adicionada
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.conectar():
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.callproc("REGISTRAR_ENTRADA", [codigo, quantidade])
            self.connection.commit()
            cursor.close()
            logger.info(f"Entrada registrada com sucesso. Código: {codigo}, Quantidade: {quantidade}")
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logger.error(f"Erro ao registrar entrada: {error.message}")
            try:
                self.connection.rollback()
            except:
                pass
            return False
    
    def registrar_saida(self, codigo: int, quantidade: float) -> bool:
        """
        Registra saída de insumo utilizando o procedimento armazenado.
        
        Args:
            codigo: Código do insumo
            quantidade: Quantidade a ser removida
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.conectar():
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.callproc("REGISTRAR_SAIDA", [codigo, quantidade])
            self.connection.commit()
            cursor.close()
            logger.info(f"Saída registrada com sucesso. Código: {codigo}, Quantidade: {quantidade}")
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logger.error(f"Erro ao registrar saída: {error.message}")
            try:
                self.connection.rollback()
            except:
                pass
            return False
    
    def verificar_alertas(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de insumos com quantidade abaixo do nível mínimo.
        
        Returns:
            List[Dict[str, Any]]: Lista de insumos em alerta
        """
        sql = """
        SELECT 
            CODIGO, NOME, QUANTIDADE, UNIDADE, NIVEL_MIN
        FROM VW_INSUMOS_CRITICOS
        ORDER BY NOME
        """
        
        resultados = self.executar_query(sql)
        return resultados if resultados else []
    
    def obter_relatorio_estoque(self) -> List[Dict[str, Any]]:
        """
        Retorna o relatório completo de estoque.
        
        Returns:
            List[Dict[str, Any]]: Lista com o relatório de estoque
        """
        sql = """
        SELECT 
            CODIGO, NOME, QUANTIDADE, UNIDADE, PRECO_UNIT, 
            NIVEL_MIN, VALOR_TOTAL, STATUS
        FROM VW_RELATORIO_ESTOQUE
        ORDER BY NOME
        """
        
        resultados = self.executar_query(sql)
        return resultados if resultados else []


if __name__ == "__main__":
    # Teste simples de conexão
    gateway = OracleGateway()
    if gateway.conectar():
        print("Conexão bem-sucedida com o banco de dados Oracle!")
        insumos = gateway.listar_insumos()
        print(f"Total de insumos: {len(insumos)}")
        gateway.desconectar()
    else:
        print("Falha ao conectar com o banco de dados Oracle.") 