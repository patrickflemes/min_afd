import re


def ler_arquivo_texto(caminho):
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()


def normalizar_simbolo_nao_terminal(token):
    token = token.strip()
    if token.startswith('<') and token.endswith('>'):
        return token[1:-1]
    return token


def parsear_gramatica(texto):
    gramatica = {}
    nao_terminal_inicial = None
    
    linhas = texto.strip().split('\n')
    
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        
        if '::=' not in linha:
            continue
        
        partes = linha.split('::=')
        if len(partes) != 2:
            continue
        
        lado_esquerdo = partes[0].strip()
        lado_direito = partes[1].strip()
        
        nao_terminal = normalizar_simbolo_nao_terminal(lado_esquerdo)
        
        if nao_terminal_inicial is None:
            nao_terminal_inicial = nao_terminal
        
        alternativas = lado_direito.split('|')
        producoes = []
        
        for alt in alternativas:
            alt = alt.strip()
            if alt:
                producoes.append(alt)
        
        if nao_terminal in gramatica:
            gramatica[nao_terminal].extend(producoes)
        else:
            gramatica[nao_terminal] = producoes
    
    return gramatica, nao_terminal_inicial


def extrair_terminal_e_nao_terminal(producao):
    producao = producao.strip()
    
    if producao == 'ε' or producao == '':
        return None, None, True
    
    padrao = re.match(r'^(.)<([^>]+)>$', producao)
    if padrao:
        terminal = padrao.group(1)
        nao_terminal = padrao.group(2)
        return terminal, nao_terminal, False
    
    padrao_multi = re.match(r'^(.+)<([^>]+)>$', producao)
    if padrao_multi:
        terminal = padrao_multi.group(1)
        nao_terminal = padrao_multi.group(2)
        return terminal, nao_terminal, False
    
    if '<' not in producao and '>' not in producao:
        return producao, None, False
    
    return producao, None, False

