from automato import Automato, criar_nome_estado_conjunto
from gramatica import extrair_terminal_e_nao_terminal


ESTADO_FINAL = 'FINAL'


def converter_gramatica_para_afn(gramatica, nao_terminal_inicial):
    afn = Automato()
    
    afn.definir_estado_inicial(nao_terminal_inicial)
    
    for nao_terminal in gramatica:
        afn.adicionar_estado(nao_terminal)
    
    usa_estado_final = False
    
    for nao_terminal, producoes in gramatica.items():
        for producao in producoes:
            terminal, destino, eh_epsilon = extrair_terminal_e_nao_terminal(producao)
            
            if eh_epsilon:
                afn.adicionar_estado_final(nao_terminal)
            elif destino is not None:
                afn.adicionar_transicao_afn(nao_terminal, terminal, destino)
            else:
                usa_estado_final = True
                afn.adicionar_transicao_afn(nao_terminal, terminal, ESTADO_FINAL)
    
    if usa_estado_final:
        afn.adicionar_estado(ESTADO_FINAL)
        afn.adicionar_estado_final(ESTADO_FINAL)
    
    return afn


def determinizar_afn(afn):
    afd = Automato()
    
    estado_inicial_conjunto = frozenset([afn.estado_inicial])
    nome_estado_inicial = criar_nome_estado_conjunto(estado_inicial_conjunto)
    
    afd.definir_estado_inicial(nome_estado_inicial)
    afd.alfabeto = afn.alfabeto.copy()
    
    if estado_inicial_conjunto & afn.estados_finais:
        afd.adicionar_estado_final(nome_estado_inicial)
    
    mapeamento = {estado_inicial_conjunto: nome_estado_inicial}
    fila = [estado_inicial_conjunto]
    processados = set()
    
    while fila:
        conjunto_atual = fila.pop(0)
        
        if conjunto_atual in processados:
            continue
        
        processados.add(conjunto_atual)
        nome_atual = mapeamento[conjunto_atual]
        
        for simbolo in afn.alfabeto:
            novo_conjunto = set()
            
            for estado in conjunto_atual:
                transicao = afn.obter_transicao(estado, simbolo)
                if transicao is not None:
                    if isinstance(transicao, set):
                        novo_conjunto.update(transicao)
                    else:
                        novo_conjunto.add(transicao)
            
            if not novo_conjunto:
                continue
            
            novo_conjunto_frozen = frozenset(novo_conjunto)
            
            if novo_conjunto_frozen not in mapeamento:
                nome_novo = criar_nome_estado_conjunto(novo_conjunto_frozen)
                mapeamento[novo_conjunto_frozen] = nome_novo
                fila.append(novo_conjunto_frozen)
                
                if novo_conjunto_frozen & afn.estados_finais:
                    afd.adicionar_estado_final(nome_novo)
            
            nome_destino = mapeamento[novo_conjunto_frozen]
            afd.adicionar_transicao_afd(nome_atual, simbolo, nome_destino)
    
    return afd

