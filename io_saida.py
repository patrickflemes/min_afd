"""
Módulo de entrada/saída para AFD.

Este módulo é responsável por:
- Salvar o AFD em formato CSV (transições)
- Salvar o AFD em formato de tabela
- Imprimir o AFD no terminal para debug
"""

import csv


def salvar_afd_csv(afd, caminho_saida):
    """
    Salva o AFD em formato CSV com uma linha por transição.
    
    Formato do CSV:
        estado,simbolo,destino,eh_inicial,eh_final
    
    Estados sem transições também são salvos (com símbolo/destino vazios).
    """
    with open(caminho_saida, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        
        # Cabeçalho
        escritor.writerow(['estado', 'simbolo', 'destino', 'eh_inicial', 'eh_final'])
        
        estados_com_transicao = set()
        
        # Escreve cada transição como uma linha
        for estado in sorted(afd.estados):
            eh_inicial = estado == afd.estado_inicial
            eh_final = estado in afd.estados_finais
            
            if estado in afd.transicoes:
                for simbolo in sorted(afd.transicoes[estado].keys()):
                    destino = afd.transicoes[estado][simbolo]
                    if isinstance(destino, set):
                        destino = ','.join(sorted(destino))
                    
                    escritor.writerow([
                        estado,
                        simbolo,
                        destino,
                        'true' if eh_inicial else 'false',
                        'true' if eh_final else 'false'
                    ])
                    estados_com_transicao.add(estado)
            
            # Estados sem transição (como estados finais sem saída)
            if estado not in estados_com_transicao:
                escritor.writerow([
                    estado,
                    '',
                    '',
                    'true' if eh_inicial else 'false',
                    'true' if eh_final else 'false'
                ])


def salvar_afd_tabela(afd, caminho_saida):
    """
    Salva o AFD em formato de tabela de transições.
    
    Formato:
        estado,inicial,final,simbolo1,simbolo2,...
        q0,true,false,q1,q2,...
    
    Cada linha representa um estado, colunas são os símbolos do alfabeto.
    """
    with open(caminho_saida, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        
        # Cabeçalho com símbolos do alfabeto
        simbolos = sorted(afd.alfabeto)
        cabecalho = ['estado', 'inicial', 'final'] + simbolos
        escritor.writerow(cabecalho)
        
        # Uma linha por estado
        for estado in sorted(afd.estados):
            eh_inicial = 'true' if estado == afd.estado_inicial else 'false'
            eh_final = 'true' if estado in afd.estados_finais else 'false'
            
            linha = [estado, eh_inicial, eh_final]
            
            # Destino para cada símbolo
            for simbolo in simbolos:
                transicao = afd.obter_transicao(estado, simbolo)
                if transicao is None:
                    linha.append('-')
                elif isinstance(transicao, set):
                    linha.append(','.join(sorted(transicao)))
                else:
                    linha.append(transicao)
            
            escritor.writerow(linha)


def imprimir_afd(afd):
    """
    Imprime o AFD no terminal de forma formatada.
    Útil para debug e visualização do autômato.
    """
    print("=" * 50)
    print("AUTÔMATO FINITO DETERMINÍSTICO")
    print("=" * 50)
    print(f"Estados: {sorted(afd.estados)}")
    print(f"Alfabeto: {sorted(afd.alfabeto)}")
    print(f"Estado inicial: {afd.estado_inicial}")
    print(f"Estados finais: {sorted(afd.estados_finais)}")
    print("Transições:")
    for estado in sorted(afd.estados):
        if estado in afd.transicoes:
            for simbolo in sorted(afd.transicoes[estado].keys()):
                destino = afd.transicoes[estado][simbolo]
                print(f"  δ({estado}, {simbolo}) = {destino}")
    print("=" * 50)
