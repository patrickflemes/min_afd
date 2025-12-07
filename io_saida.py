import csv


def salvar_afd_csv(afd, caminho_saida):
    with open(caminho_saida, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        
        escritor.writerow(['estado', 'simbolo', 'destino', 'eh_inicial', 'eh_final'])
        
        estados_com_transicao = set()
        
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
            
            if estado not in estados_com_transicao:
                escritor.writerow([
                    estado,
                    '',
                    '',
                    'true' if eh_inicial else 'false',
                    'true' if eh_final else 'false'
                ])


def salvar_afd_tabela(afd, caminho_saida):
    with open(caminho_saida, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        
        simbolos = sorted(afd.alfabeto)
        cabecalho = ['estado', 'inicial', 'final'] + simbolos
        escritor.writerow(cabecalho)
        
        for estado in sorted(afd.estados):
            eh_inicial = 'true' if estado == afd.estado_inicial else 'false'
            eh_final = 'true' if estado in afd.estados_finais else 'false'
            
            linha = [estado, eh_inicial, eh_final]
            
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

