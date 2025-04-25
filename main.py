import os
import sys
import json
from typing import Optional
from storage import Storage
from oracle_gateway import OracleGateway
from estoque import Estoque
from utils import (
    validar_float,
    formatar_tabela,
    gerar_relatorio,
    limpar_tela,
    print_colorido,
    print_erro,
    print_sucesso,
    print_alerta
)
from datetime import datetime

def obter_input(mensagem: str, tipo: str = "texto") -> Optional[str]:
    """
    Obtém input do usuário com validação básica.
    """
    while True:
        try:
            valor = input(mensagem).strip()
            if not valor:
                print_erro("Valor não pode ser vazio.")
                continue
            
            if tipo == "numero":
                if validar_float(valor) is None:
                    print_erro("Valor inválido. Digite um número.")
                    continue
            
            return valor
        except KeyboardInterrupt:
            print("\nOperação cancelada pelo usuário.")
            return None
        except Exception as e:
            print_erro(f"Erro: {str(e)}")
            return None

def menu_principal():
    """
    Exibe o menu principal e retorna a opção escolhida.
    """
    limpar_tela()
    print_colorido("=== AgroStock Lite ===", "cyan")
    print("\n1) Ver estoque")
    print("2) Adicionar insumo")
    print("3) Registrar entrada")
    print("4) Registrar saída")
    print("5) Atualizar insumo")
    print("6) Remover insumo")
    print("7) Gerar relatório")
    print("8) Ver alertas")
    print("9) Sair")
    
    opcao = obter_input("\nEscolha uma opção: ", "numero")
    return int(opcao) if opcao else None

def ver_estoque(estoque: Estoque):
    """
    Exibe todos os insumos em formato de tabela.
    """
    insumos = estoque.listar_insumos()
    if not insumos:
        print_alerta("Nenhum insumo cadastrado.")
        return
    
    cabecalho = ["Código", "Nome", "Quantidade", "Unidade", "Preço Unitário", "Nível Mínimo"]
    print(formatar_tabela(insumos, cabecalho))

def adicionar_insumo(estoque: Estoque):
    """
    Adiciona um novo insumo ao estoque.
    """
    print_colorido("\n=== Adicionar Insumo ===", "cyan")
    
    codigo = obter_input("Código: ", "numero")
    if not codigo:
        return
    
    if estoque.buscar_insumo(int(codigo)):
        print_erro("Código já existe.")
        return
    
    nome = obter_input("Nome: ")
    if not nome:
        return
    
    quantidade = obter_input("Quantidade inicial: ", "numero")
    if not quantidade:
        return
    
    unidade = obter_input("Unidade (ex: kg, L, un): ")
    if not unidade:
        return
    
    preco = obter_input("Preço unitário: ", "numero")
    if not preco:
        return
    
    nivel_min = obter_input("Nível mínimo: ", "numero")
    if not nivel_min:
        return
    
    insumo = {
        'codigo': int(codigo),
        'nome': nome,
        'quantidade': float(quantidade),
        'unidade': unidade,
        'preco_unit': float(preco),
        'nivel_min': float(nivel_min)
    }
    
    estoque.adicionar_insumo(insumo)

def registrar_entrada(estoque: Estoque):
    """
    Registra entrada de insumo.
    """
    print_colorido("\n=== Registrar Entrada ===", "cyan")
    
    codigo = obter_input("Código do insumo: ", "numero")
    if not codigo:
        return
    
    quantidade = obter_input("Quantidade: ", "numero")
    if not quantidade:
        return
    
    estoque.registrar_entrada(int(codigo), float(quantidade))

def registrar_saida(estoque: Estoque):
    """
    Registra saída de insumo.
    """
    print_colorido("\n=== Registrar Saída ===", "cyan")
    
    codigo = obter_input("Código do insumo: ", "numero")
    if not codigo:
        return
    
    quantidade = obter_input("Quantidade: ", "numero")
    if not quantidade:
        return
    
    estoque.registrar_saida(int(codigo), float(quantidade))

def atualizar_insumo(estoque: Estoque):
    """
    Atualiza dados de um insumo.
    """
    print_colorido("\n=== Atualizar Insumo ===", "cyan")
    
    codigo = obter_input("Código do insumo: ", "numero")
    if not codigo:
        return
    
    insumo = estoque.buscar_insumo(int(codigo))
    if not insumo:
        print_erro("Insumo não encontrado.")
        return
    
    print("\nDeixe em branco para manter o valor atual.")
    nome = obter_input(f"Nome [{insumo['nome']}]: ")
    unidade = obter_input(f"Unidade [{insumo['unidade']}]: ")
    preco = obter_input(f"Preço unitário [{insumo['preco_unit']}]: ", "numero")
    nivel_min = obter_input(f"Nível mínimo [{insumo['nivel_min']}]: ", "numero")
    
    novos_dados = {}
    if nome:
        novos_dados['nome'] = nome
    if unidade:
        novos_dados['unidade'] = unidade
    if preco:
        novos_dados['preco_unit'] = float(preco)
    if nivel_min:
        novos_dados['nivel_min'] = float(nivel_min)
    
    if novos_dados:
        estoque.atualizar_insumo(int(codigo), novos_dados)
    else:
        print_alerta("Nenhuma alteração realizada.")

def remover_insumo(estoque: Estoque):
    """
    Remove um insumo do estoque.
    """
    print_colorido("\n=== Remover Insumo ===", "cyan")
    
    codigo = obter_input("Código do insumo: ", "numero")
    if not codigo:
        return
    
    confirmacao = obter_input("Tem certeza que deseja remover este insumo? (s/n): ")
    if confirmacao.lower() == 's':
        estoque.remover_insumo(int(codigo))

def gerar_relatorio_estoque(estoque: Estoque):
    """
    Gera e exibe relatório do estoque.
    """
    print_colorido("\n=== Gerar Relatório ===", "cyan")
    
    insumos = estoque.listar_insumos()
    if not insumos:
        print_alerta("Nenhum insumo cadastrado.")
        return
    
    nome_arquivo = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    relatorio = gerar_relatorio(insumos, nome_arquivo)
    print_sucesso(f"Relatório gerado e salvo em {nome_arquivo}")
    print("\n" + relatorio)

def ver_alertas(estoque: Estoque):
    """
    Exibe alertas de insumos com quantidade abaixo do nível mínimo.
    """
    print_colorido("\n=== Alertas ===", "cyan")
    
    alertas = estoque.verificar_alertas()
    if not alertas:
        print_sucesso("Nenhum alerta ativo.")
        return
    
    cabecalho = ["Código", "Nome", "Quantidade", "Unidade", "Nível Mínimo"]
    print(formatar_tabela(alertas, cabecalho))

def main():
    """
    Função principal do programa.
    """
    # Inicializa componentes
    storage = Storage()
    oracle = OracleGateway(
        usuario="seu_usuario",
        senha="sua_senha",
        dsn="localhost:1521/XE"
    )
    estoque = Estoque(storage, oracle)
    
    # Loop principal
    while True:
        opcao = menu_principal()
        
        if opcao is None:
            continue
        
        if opcao == 1:
            ver_estoque(estoque)
        elif opcao == 2:
            adicionar_insumo(estoque)
        elif opcao == 3:
            registrar_entrada(estoque)
        elif opcao == 4:
            registrar_saida(estoque)
        elif opcao == 5:
            atualizar_insumo(estoque)
        elif opcao == 6:
            remover_insumo(estoque)
        elif opcao == 7:
            gerar_relatorio_estoque(estoque)
        elif opcao == 8:
            ver_alertas(estoque)
        elif opcao == 9:
            print_sucesso("Encerrando o programa...")
            break
        else:
            print_erro("Opção inválida.")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main() 