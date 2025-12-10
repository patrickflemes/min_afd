"""
Módulo de minimização de AFD.

Este módulo implementa o algoritmo de minimização de autômatos finitos
determinísticos, incluindo:
- Remoção de estados inalcançáveis
- Completação com estado poço
- Minimização por particionamento (algoritmo de Hopcroft simplificado)
- Remoção do estado poço após minimização

O algoritmo de minimização agrupa estados equivalentes (que não podem
ser distinguidos por nenhuma palavra) em um único estado.
"""

from automato import Automato


# Nome do estado poço (estado de "lixo" que absorve transições indefinidas)
ESTADO_POCO = 'POCO'


def remover_inalcancaveis(afd):
    """
    Remove estados que não são alcançáveis a partir do estado inicial.
    
    Usa BFS para encontrar todos os estados alcançáveis,
    depois cria um novo AFD apenas com esses estados.
    
    Retorna: AFD sem estados inalcançáveis
    """
    # BFS para encontrar estados alcançáveis
    alcancaveis = set()
    fila = [afd.estado_inicial]
    
    while fila:
        estado = fila.pop(0)
        
        if estado in alcancaveis:
            continue
        
        alcancaveis.add(estado)
        
        # Adiciona destinos das transições à fila
        if estado in afd.transicoes:
            for simbolo in afd.transicoes[estado]:
                destino = afd.transicoes[estado][simbolo]
                if isinstance(destino, set):
                    for d in destino:
                        if d not in alcancaveis:
                            fila.append(d)
                else:
                    if destino not in alcancaveis:
                        fila.append(destino)
    
    # Cria novo AFD apenas com estados alcançáveis
    novo_afd = Automato()
    novo_afd.alfabeto = afd.alfabeto.copy()
    novo_afd.estado_inicial = afd.estado_inicial
    novo_afd.estados = alcancaveis.copy()
    novo_afd.estados_finais = afd.estados_finais & alcancaveis
    
    # Copia apenas transições de estados alcançáveis
    for estado in alcancaveis:
        if estado in afd.transicoes:
            novo_afd.transicoes[estado] = {}
            for simbolo in afd.transicoes[estado]:
                destino = afd.transicoes[estado][simbolo]
                if isinstance(destino, set):
                    destinos_validos = destino & alcancaveis
                    if destinos_validos:
                        novo_afd.transicoes[estado][simbolo] = destinos_validos
                else:
                    if destino in alcancaveis:
                        novo_afd.transicoes[estado][simbolo] = destino
    
    return novo_afd


def completar_com_estado_poco(afd):
    """
    Torna o AFD completo adicionando um estado poço.
    
    O estado poço absorve todas as transições indefinidas.
    Todas as transições do estado poço vão para ele mesmo.
    
    Necessário para o algoritmo de minimização funcionar corretamente.
    
    Retorna: AFD completo (todas as transições definidas)
    """
    # Verifica se precisa de estado poço
    precisa_poco = False
    
    for estado in afd.estados:
        for simbolo in afd.alfabeto:
            transicao = afd.obter_transicao(estado, simbolo)
            if transicao is None:
                precisa_poco = True
                break
        if precisa_poco:
            break
    
    # Retorna original se já está completo
    if not precisa_poco:
        return afd
    
    # Cria cópia com estado poço
    novo_afd = afd.copiar()
    novo_afd.adicionar_estado(ESTADO_POCO)
    
    # Adiciona transições faltantes para o estado poço
    for estado in list(novo_afd.estados):
        for simbolo in novo_afd.alfabeto:
            transicao = novo_afd.obter_transicao(estado, simbolo)
            if transicao is None:
                novo_afd.adicionar_transicao_afd(estado, simbolo, ESTADO_POCO)
    
    return novo_afd


def minimizar_afd(afd):
    """
    Minimiza o AFD usando algoritmo de particionamento.
    
    Algoritmo:
    1. Partição inicial: {estados finais} e {estados não-finais}
    2. Refina partições: estados com mesma "assinatura" ficam juntos
       (assinatura = para cada símbolo, índice do bloco destino)
    3. Repete até não haver mais refinamentos
    4. Cada bloco da partição final vira um estado do AFD mínimo
    
    Retorna: AFD mínimo equivalente
    """
    # Partição inicial: finais vs não-finais
    estados_nao_finais = afd.estados - afd.estados_finais
    
    if not estados_nao_finais:
        particao = [afd.estados_finais.copy()]
    elif not afd.estados_finais:
        particao = [estados_nao_finais.copy()]
    else:
        particao = [afd.estados_finais.copy(), estados_nao_finais.copy()]
    
    particao = [p for p in particao if p]
    
    def obter_bloco(estado, particao_atual):
        """Retorna o índice do bloco que contém o estado."""
        for i, bloco in enumerate(particao_atual):
            if estado in bloco:
                return i
        return -1
    
    def obter_destino_bloco(estado, simbolo, particao_atual):
        """Retorna o índice do bloco destino para uma transição."""
        transicao = afd.obter_transicao(estado, simbolo)
        if transicao is None:
            return -1
        if isinstance(transicao, set):
            transicao = next(iter(transicao))
        return obter_bloco(transicao, particao_atual)
    
    # Refina partições até estabilizar
    mudou = True
    while mudou:
        mudou = False
        nova_particao = []
        
        for bloco in particao:
            # Blocos com um único estado não precisam ser divididos
            if len(bloco) <= 1:
                nova_particao.append(bloco)
                continue
            
            # Agrupa estados pela assinatura (blocos destino para cada símbolo)
            sub_blocos = {}
            
            for estado in bloco:
                # Assinatura: tupla de índices de blocos destino
                assinatura = tuple(
                    obter_destino_bloco(estado, simbolo, particao)
                    for simbolo in sorted(afd.alfabeto)
                )
                
                if assinatura not in sub_blocos:
                    sub_blocos[assinatura] = set()
                sub_blocos[assinatura].add(estado)
            
            # Se dividiu em mais de um sub-bloco, houve refinamento
            if len(sub_blocos) > 1:
                mudou = True
            
            for sub_bloco in sub_blocos.values():
                nova_particao.append(sub_bloco)
        
        particao = nova_particao
    
    # Constrói o AFD mínimo a partir da partição final
    mapeamento_estado_para_bloco = {}
    nomes_blocos = {}
    
    for i, bloco in enumerate(particao):
        nome_bloco = 'q' + str(i)
        nomes_blocos[i] = nome_bloco
        for estado in bloco:
            mapeamento_estado_para_bloco[estado] = i
    
    afd_minimo = Automato()
    afd_minimo.alfabeto = afd.alfabeto.copy()
    
    # Define estado inicial
    bloco_inicial = mapeamento_estado_para_bloco[afd.estado_inicial]
    afd_minimo.estado_inicial = nomes_blocos[bloco_inicial]
    
    # Adiciona estados e marca finais
    for i, bloco in enumerate(particao):
        nome_bloco = nomes_blocos[i]
        afd_minimo.adicionar_estado(nome_bloco)
        
        # Bloco é final se contém algum estado final original
        if bloco & afd.estados_finais:
            afd_minimo.adicionar_estado_final(nome_bloco)
    
    # Adiciona transições (usa qualquer estado do bloco como representante)
    for i, bloco in enumerate(particao):
        nome_bloco = nomes_blocos[i]
        estado_representante = next(iter(bloco))
        
        for simbolo in afd.alfabeto:
            transicao = afd.obter_transicao(estado_representante, simbolo)
            if transicao is not None:
                if isinstance(transicao, set):
                    transicao = next(iter(transicao))
                bloco_destino = mapeamento_estado_para_bloco[transicao]
                nome_destino = nomes_blocos[bloco_destino]
                afd_minimo.adicionar_transicao_afd(nome_bloco, simbolo, nome_destino)
    
    return afd_minimo


def remover_estado_poco(afd):
    """
    Remove o estado poço do AFD, se existir.
    
    O estado poço pode ser removido após a minimização para
    obter uma representação mais compacta.
    
    Identifica o estado poço pelo comportamento:
    - Não é estado final
    - Não é estado inicial  
    - Todas as suas transições vão para ele mesmo
    
    Retorna: AFD sem o estado poço
    """
    # Encontra estado poço pelo comportamento
    estado_poco = None
    
    for estado in afd.estados:
        # Poço não pode ser final nem inicial
        if estado in afd.estados_finais:
            continue
        if estado == afd.estado_inicial:
            continue
        
        # Verifica se todas as transições vão para si mesmo
        eh_poco = True
        for simbolo in afd.alfabeto:
            transicao = afd.obter_transicao(estado, simbolo)
            if transicao != estado:
                eh_poco = False
                break
        
        if eh_poco:
            estado_poco = estado
            break
    
    # Se não encontrou estado poço, retorna original
    if estado_poco is None:
        return afd
    
    # Cria novo AFD sem o estado poço
    novo_afd = Automato()
    novo_afd.alfabeto = afd.alfabeto.copy()
    novo_afd.estado_inicial = afd.estado_inicial
    novo_afd.estados = afd.estados - {estado_poco}
    novo_afd.estados_finais = afd.estados_finais.copy()
    
    # Remove transições que vão para o estado poço
    for estado in novo_afd.estados:
        if estado in afd.transicoes:
            novo_afd.transicoes[estado] = {}
            for simbolo in afd.transicoes[estado]:
                destino = afd.transicoes[estado][simbolo]
                if destino != estado_poco:
                    novo_afd.transicoes[estado][simbolo] = destino
    
    return novo_afd
