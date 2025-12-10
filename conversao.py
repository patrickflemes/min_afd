"""
Módulo de conversão de gramática para autômato.

Este módulo é responsável por:
- Converter uma gramática regular em AFN (Autômato Finito Não-determinístico)
- Determinizar o AFN para AFD (Autômato Finito Determinístico)

A conversão segue o mapeamento padrão:
- Cada não-terminal vira um estado
- Cada produção a<B> vira uma transição δ(A, a) = B
- Produções apenas com terminal usam um estado FINAL auxiliar
- Produções epsilon tornam o estado final
"""

from automato import Automato, criar_nome_estado_conjunto
from gramatica import extrair_terminal_e_nao_terminal


# Estado especial para produções que terminam com apenas um terminal
ESTADO_FINAL = 'FINAL'


def converter_gramatica_para_afn(gramatica, nao_terminal_inicial):
    """
    Converte uma gramática regular para um AFN.
    
    Mapeamento:
        - Não-terminais → Estados
        - Produção a<B> → Transição δ(atual, a) = B
        - Produção a (só terminal) → Transição δ(atual, a) = FINAL
        - Produção ε → Estado atual é final
    
    Retorna: AFN equivalente à gramática
    """
    afn = Automato()
    
    # O não-terminal inicial da gramática é o estado inicial do AFN
    afn.definir_estado_inicial(nao_terminal_inicial)
    
    # Cada não-terminal é um estado
    for nao_terminal in gramatica:
        afn.adicionar_estado(nao_terminal)
    
    usa_estado_final = False
    
    # Processa cada produção
    for nao_terminal, producoes in gramatica.items():
        for producao in producoes:
            terminal, destino, eh_epsilon = extrair_terminal_e_nao_terminal(producao)
            
            if eh_epsilon:
                # Produção ε: estado é final (aceita palavra vazia)
                afn.adicionar_estado_final(nao_terminal)
            elif destino is not None:
                # Produção a<B>: transição para outro não-terminal
                afn.adicionar_transicao_afn(nao_terminal, terminal, destino)
            else:
                # Produção só com terminal: vai para estado FINAL
                usa_estado_final = True
                afn.adicionar_transicao_afn(nao_terminal, terminal, ESTADO_FINAL)
    
    # Adiciona estado FINAL se necessário
    if usa_estado_final:
        afn.adicionar_estado_final(ESTADO_FINAL)
    
    return afn


def determinizar_afn(afn):
    """
    Converte um AFN para AFD usando construção de subconjuntos.
    
    Algoritmo:
    1. Estado inicial do AFD = {estado inicial do AFN}
    2. Para cada conjunto de estados e símbolo, calcula o conjunto destino
    3. Novos conjuntos viram novos estados do AFD
    4. Um estado do AFD é final se contém algum estado final do AFN
    
    Retorna: AFD equivalente ao AFN
    """
    afd = Automato()
    
    # Estado inicial é o conjunto contendo apenas o estado inicial do AFN
    estado_inicial_conjunto = frozenset([afn.estado_inicial])
    nome_estado_inicial = criar_nome_estado_conjunto(estado_inicial_conjunto)
    
    afd.definir_estado_inicial(nome_estado_inicial)
    afd.alfabeto = afn.alfabeto.copy()
    
    # Se o estado inicial do AFN é final, o estado inicial do AFD também é
    if estado_inicial_conjunto & afn.estados_finais:
        afd.adicionar_estado_final(nome_estado_inicial)
    
    # Mapeia conjuntos de estados para nomes de estados do AFD
    mapeamento = {estado_inicial_conjunto: nome_estado_inicial}
    fila = [estado_inicial_conjunto]
    processados = set()
    
    # Processa cada conjunto de estados (BFS)
    while fila:
        conjunto_atual = fila.pop(0)
        
        if conjunto_atual in processados:
            continue
        
        processados.add(conjunto_atual)
        nome_atual = mapeamento[conjunto_atual]
        
        # Para cada símbolo do alfabeto
        for simbolo in afn.alfabeto:
            novo_conjunto = set()
            
            # Calcula a união dos destinos de todos os estados do conjunto
            for estado in conjunto_atual:
                transicao = afn.obter_transicao(estado, simbolo)
                if transicao is not None:
                    if isinstance(transicao, set):
                        novo_conjunto.update(transicao)
                    else:
                        novo_conjunto.add(transicao)
            
            # Ignora conjunto vazio
            if not novo_conjunto:
                continue
            
            novo_conjunto_frozen = frozenset(novo_conjunto)
            
            # Novo estado encontrado
            if novo_conjunto_frozen not in mapeamento:
                nome_novo = criar_nome_estado_conjunto(novo_conjunto_frozen)
                mapeamento[novo_conjunto_frozen] = nome_novo
                fila.append(novo_conjunto_frozen)
                
                # Estado é final se contém algum estado final do AFN
                if novo_conjunto_frozen & afn.estados_finais:
                    afd.adicionar_estado_final(nome_novo)
            
            # Adiciona transição no AFD
            nome_destino = mapeamento[novo_conjunto_frozen]
            afd.adicionar_transicao_afd(nome_atual, simbolo, nome_destino)
    
    return afd
