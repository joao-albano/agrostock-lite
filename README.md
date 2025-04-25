# AgroStock Lite

Sistema de controle de estoque para insumos agrícolas desenvolvido como trabalho para a FIAP.

## Funcionalidades

- Cadastro e gerenciamento de insumos agrícolas
- Controle de entradas e saídas de produtos
- Alertas para níveis de estoque baixo
- Geração de relatórios
- Integração com banco de dados Oracle
- Armazenamento local como backup

## Requisitos

- Python 3.6+
- Oracle Database (XE, 11g ou superior)
- Oracle Instant Client
- cx_Oracle

## Configuração

1. Execute o script `setup_oracle.sql` para configurar o banco de dados:
   - Conecte como SYS ou SYSTEM
   - Execute a primeira parte do script para criar o usuário
   - Conecte como usuário agrostock
   - Execute a segunda parte do script para criar as tabelas e objetos

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure as credenciais do Oracle no arquivo `main.py`:
```python
oracle = OracleGateway(
    usuario="agrostock",
    senha="agrostock123",
    dsn="localhost:1521/XE"
)
```

## Uso

Execute o programa principal:
```
python main.py
```

## Estrutura do Projeto

- `main.py`: Programa principal e interface de linha de comando
- `estoque.py`: Classe para gerenciamento de estoque
- `storage.py`: Armazenamento local em JSON
- `oracle_gateway.py`: Integração com Oracle Database
- `utils.py`: Funções utilitárias
- `setup_oracle.sql`: Script de configuração do banco de dados

## Autores

- [Seu Nome] - [Seu RM]
