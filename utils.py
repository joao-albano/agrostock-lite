import os
from datetime import datetime
from colorama import init, Fore, Style

# Inicializa o colorama
init()

def validar_float(valor: str) -> float:
    """
    Valida se uma string pode ser convertida para float.
    Retorna o valor convertido ou None se inválido.
    """
    try:
        return float(valor)
    except ValueError:
        return None

def formatar_tabela(dados: list, cabecalho: list) -> str:
    """
    Formata uma lista de dicionários em uma tabela alinhada.
    """
    if not dados:
        return "Nenhum dado encontrado."
    
    # Calcula largura das colunas
    larguras = [len(str(h)) for h in cabecalho]
    for linha in dados:
        for i, valor in enumerate(linha.values()):
            larguras[i] = max(larguras[i], len(str(valor)))
    
    # Cria linha de separação
    separador = "+" + "+".join("-" * (l + 2) for l in larguras) + "+"
    
    # Formata cabeçalho
    tabela = [separador]
    cabecalho_formatado = "|" + "|".join(f" {h:<{l}} " for h, l in zip(cabecalho, larguras)) + "|"
    tabela.append(cabecalho_formatado)
    tabela.append(separador)
    
    # Formata linhas de dados
    for linha in dados:
        linha_formatada = "|" + "|".join(f" {str(v):<{l}} " for v, l in zip(linha.values(), larguras)) + "|"
        tabela.append(linha_formatada)
    
    tabela.append(separador)
    return "\n".join(tabela)

def gerar_relatorio(dados: list, nome_arquivo: str = None) -> str:
    """
    Gera um relatório formatado e opcionalmente salva em arquivo.
    """
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    relatorio = f"Relatório gerado em: {data_hora}\n\n"
    
    if dados:
        relatorio += formatar_tabela(dados, ["Código", "Nome", "Quantidade", "Unidade", "Preço Unitário", "Nível Mínimo"])
    else:
        relatorio += "Nenhum dado encontrado."
    
    if nome_arquivo:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(relatorio)
    
    return relatorio

def limpar_tela():
    """
    Limpa a tela do terminal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colorido(texto: str, cor: str = Fore.WHITE):
    """
    Imprime texto colorido no terminal.
    """
    print(f"{cor}{texto}{Style.RESET_ALL}")

def print_erro(mensagem: str):
    """
    Imprime mensagem de erro em vermelho.
    """
    print_colorido(f"Erro: {mensagem}", Fore.RED)

def print_sucesso(mensagem: str):
    """
    Imprime mensagem de sucesso em verde.
    """
    print_colorido(f"Sucesso: {mensagem}", Fore.GREEN)

def print_alerta(mensagem: str):
    """
    Imprime mensagem de alerta em amarelo.
    """
    print_colorido(f"Alerta: {mensagem}", Fore.YELLOW) 