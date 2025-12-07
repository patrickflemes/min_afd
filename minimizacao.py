from automato import Automato


ESTADO_POCO = 'POCO'


def remover_inalcancaveis(afd):
    alcancaveis = set()
    fila = [afd.estado_inicial]
    
    while fila:
        estado = fila.pop(0)
        
        if estado in alcancaveis:
            continue
        
        alcancaveis.add(estado)
        
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
    
    novo_afd = Automato()
    novo_afd.alfabeto = afd.alfabeto.copy()
    novo_afd.estado_inicial = afd.estado_inicial
    novo_afd.estados = alcancaveis.copy()
    novo_afd.estados_finais = afd.estados_finais & alcancaveis
    
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
    precisa_poco = False
    
    for estado in afd.estados:
        for simbolo in afd.alfabeto:
            transicao = afd.obter_transicao(estado, simbolo)
            if transicao is None:
                precisa_poco = True
                break
        if precisa_poco:
            break
    
    if not precisa_poco:
        return afd
    
    novo_afd = afd.copiar()
    novo_afd.adicionar_estado(ESTADO_POCO)
    
    for estado in list(novo_afd.estados):
        for simbolo in novo_afd.alfabeto:
            transicao = novo_afd.obter_transicao(estado, simbolo)
            if transicao is None:
                novo_afd.adicionar_transicao_afd(estado, simbolo, ESTADO_POCO)
    
    return novo_afd


def minimizar_afd(afd):
    estados_nao_finais = afd.estados - afd.estados_finais
    
    if not estados_nao_finais:
        particao = [afd.estados_finais.copy()]
    elif not afd.estados_finais:
        particao = [estados_nao_finais.copy()]
    else:
        particao = [afd.estados_finais.copy(), estados_nao_finais.copy()]
    
    particao = [p for p in particao if p]
    
    def obter_bloco(estado, particao_atual):
        for i, bloco in enumerate(particao_atual):
            if estado in bloco:
                return i
        return -1
    
    def obter_destino_bloco(estado, simbolo, particao_atual):
        transicao = afd.obter_transicao(estado, simbolo)
        if transicao is None:
            return -1
        if isinstance(transicao, set):
            transicao = next(iter(transicao))
        return obter_bloco(transicao, particao_atual)
    
    mudou = True
    while mudou:
        mudou = False
        nova_particao = []
        
        for bloco in particao:
            if len(bloco) <= 1:
                nova_particao.append(bloco)
                continue
            
            sub_blocos = {}
            
            for estado in bloco:
                assinatura = tuple(
                    obter_destino_bloco(estado, simbolo, particao)
                    for simbolo in sorted(afd.alfabeto)
                )
                
                if assinatura not in sub_blocos:
                    sub_blocos[assinatura] = set()
                sub_blocos[assinatura].add(estado)
            
            if len(sub_blocos) > 1:
                mudou = True
            
            for sub_bloco in sub_blocos.values():
                nova_particao.append(sub_bloco)
        
        particao = nova_particao
    
    mapeamento_estado_para_bloco = {}
    nomes_blocos = {}
    
    for i, bloco in enumerate(particao):
        nome_bloco = 'q' + str(i)
        nomes_blocos[i] = nome_bloco
        for estado in bloco:
            mapeamento_estado_para_bloco[estado] = i
    
    afd_minimo = Automato()
    afd_minimo.alfabeto = afd.alfabeto.copy()
    
    bloco_inicial = mapeamento_estado_para_bloco[afd.estado_inicial]
    afd_minimo.estado_inicial = nomes_blocos[bloco_inicial]
    
    for i, bloco in enumerate(particao):
        nome_bloco = nomes_blocos[i]
        afd_minimo.adicionar_estado(nome_bloco)
        
        if bloco & afd.estados_finais:
            afd_minimo.adicionar_estado_final(nome_bloco)
    
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
    if ESTADO_POCO not in afd.estados:
        return afd
    
    eh_poco = True
    for simbolo in afd.alfabeto:
        transicao = afd.obter_transicao(ESTADO_POCO, simbolo)
        if transicao != ESTADO_POCO:
            eh_poco = False
            break
    
    if not eh_poco:
        return afd
    
    if ESTADO_POCO in afd.estados_finais:
        return afd
    
    novo_afd = Automato()
    novo_afd.alfabeto = afd.alfabeto.copy()
    novo_afd.estado_inicial = afd.estado_inicial
    novo_afd.estados = afd.estados - {ESTADO_POCO}
    novo_afd.estados_finais = afd.estados_finais - {ESTADO_POCO}
    
    for estado in novo_afd.estados:
        if estado in afd.transicoes:
            novo_afd.transicoes[estado] = {}
            for simbolo in afd.transicoes[estado]:
                destino = afd.transicoes[estado][simbolo]
                if destino != ESTADO_POCO:
                    novo_afd.transicoes[estado][simbolo] = destino
    
    return novo_afd

