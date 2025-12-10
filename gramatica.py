"""
Módulo para leitura e parsing de gramáticas regulares em formato BNF.

Este módulo é responsável por:
- Ler arquivos de texto contendo gramáticas
- Parsear gramáticas no formato BNF (Backus-Naur Form)
- Extrair terminais e não-terminais das produções

Formato esperado da gramática:
    <S> ::= a<A> | b<B>
    <A> ::= a | a<A>
    <B> ::= b | ε
"""

import re


def ler_arquivo_texto(caminho):
    """
    Lê o conteúdo de um arquivo de texto.
    Retorna o conteúdo como string.
    """
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()


def normalizar_simbolo_nao_terminal(token):
    """
    Remove os delimitadores < > de um não-terminal.
    Ex: '<S>' -> 'S', '<Estado>' -> 'Estado'
    """
    token = token.strip()
    if token.startswith('<') and token.endswith('>'):
        return token[1:-1]
    return token


def parsear_gramatica(texto):
    """
    Parseia uma gramática em formato BNF e retorna sua estrutura.
    
    Formato de entrada:
        <NT> ::= producao1 | producao2 | ...
    
    Retorna:
        - gramatica: dict {nao_terminal: [lista de producoes]}
        - nao_terminal_inicial: primeiro não-terminal encontrado
    """
    gramatica = {}
    nao_terminal_inicial = None
    
    linhas = texto.strip().split('\n')
    
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        
        # Ignora linhas sem o separador de produção
        if '::=' not in linha:
            continue
        
        partes = linha.split('::=')
        if len(partes) != 2:
            continue
        
        lado_esquerdo = partes[0].strip()
        lado_direito = partes[1].strip()
        
        # Extrai o nome do não-terminal
        nao_terminal = normalizar_simbolo_nao_terminal(lado_esquerdo)
        
        # O primeiro não-terminal encontrado é o inicial
        if nao_terminal_inicial is None:
            nao_terminal_inicial = nao_terminal
        
        # Separa as alternativas (produções separadas por |)
        alternativas = lado_direito.split('|')
        producoes = []
        
        for alt in alternativas:
            alt = alt.strip()
            if alt:
                producoes.append(alt)
        
        # Acumula produções se o não-terminal já existir
        if nao_terminal in gramatica:
            gramatica[nao_terminal].extend(producoes)
        else:
            gramatica[nao_terminal] = producoes
    
    return gramatica, nao_terminal_inicial


def extrair_terminal_e_nao_terminal(producao):
    """
    Analisa uma produção e extrai o terminal e não-terminal.
    
    Tipos de produção:
        - 'ε' ou '': produção epsilon (palavra vazia)
        - 'a<B>': terminal 'a' seguido de não-terminal 'B'
        - 'a': apenas terminal 'a' (produção que finaliza)
    
    Retorna: (terminal, nao_terminal, eh_epsilon)
    """
    producao = producao.strip()
    
    # Produção epsilon (palavra vazia)
    if producao == 'ε' or producao == '':
        return None, None, True
    
    # Padrão: um caractere terminal seguido de <nao_terminal>
    padrao = re.match(r'^(.)<([^>]+)>$', producao)
    if padrao:
        terminal = padrao.group(1)
        nao_terminal = padrao.group(2)
        return terminal, nao_terminal, False
    
    # Padrão: múltiplos caracteres terminais seguidos de <nao_terminal>
    padrao_multi = re.match(r'^(.+)<([^>]+)>$', producao)
    if padrao_multi:
        terminal = padrao_multi.group(1)
        nao_terminal = padrao_multi.group(2)
        return terminal, nao_terminal, False
    
    # Produção com apenas terminais (sem não-terminal)
    if '<' not in producao and '>' not in producao:
        return producao, None, False
    
    # Fallback para casos não reconhecidos
    return producao, None, False
