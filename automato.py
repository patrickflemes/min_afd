from dataclasses import dataclass, field


@dataclass
class Automato:
    estados: set = field(default_factory=set)
    alfabeto: set = field(default_factory=set)
    estado_inicial: str = ''
    estados_finais: set = field(default_factory=set)
    transicoes: dict = field(default_factory=dict)
    
    def adicionar_estado(self, estado):
        self.estados.add(estado)
    
    def adicionar_simbolo(self, simbolo):
        self.alfabeto.add(simbolo)
    
    def definir_estado_inicial(self, estado):
        self.estado_inicial = estado
        self.estados.add(estado)
    
    def adicionar_estado_final(self, estado):
        self.estados_finais.add(estado)
        self.estados.add(estado)
    
    def adicionar_transicao_afn(self, origem, simbolo, destino):
        self.estados.add(origem)
        self.estados.add(destino)
        self.alfabeto.add(simbolo)
        
        if origem not in self.transicoes:
            self.transicoes[origem] = {}
        
        if simbolo not in self.transicoes[origem]:
            self.transicoes[origem][simbolo] = set()
        
        self.transicoes[origem][simbolo].add(destino)
    
    def adicionar_transicao_afd(self, origem, simbolo, destino):
        self.estados.add(origem)
        self.estados.add(destino)
        self.alfabeto.add(simbolo)
        
        if origem not in self.transicoes:
            self.transicoes[origem] = {}
        
        self.transicoes[origem][simbolo] = destino
    
    def obter_transicao(self, estado, simbolo):
        if estado in self.transicoes and simbolo in self.transicoes[estado]:
            return self.transicoes[estado][simbolo]
        return None
    
    def copiar(self):
        novo = Automato()
        novo.estados = self.estados.copy()
        novo.alfabeto = self.alfabeto.copy()
        novo.estado_inicial = self.estado_inicial
        novo.estados_finais = self.estados_finais.copy()
        novo.transicoes = {}
        for estado in self.transicoes:
            novo.transicoes[estado] = {}
            for simbolo in self.transicoes[estado]:
                valor = self.transicoes[estado][simbolo]
                if isinstance(valor, set):
                    novo.transicoes[estado][simbolo] = valor.copy()
                else:
                    novo.transicoes[estado][simbolo] = valor
        return novo


def criar_nome_estado_conjunto(conjunto):
    if not conjunto:
        return '{}'
    elementos_ordenados = sorted(conjunto)
    return '{' + ','.join(elementos_ordenados) + '}'


def reconhecer_palavra(afd, palavra):
    estado_atual = afd.estado_inicial
    
    for simbolo in palavra:
        if simbolo not in afd.alfabeto:
            return False
        
        transicao = afd.obter_transicao(estado_atual, simbolo)
        if transicao is None:
            return False
        
        if isinstance(transicao, set):
            if len(transicao) == 1:
                estado_atual = next(iter(transicao))
            else:
                return False
        else:
            estado_atual = transicao
    
    return estado_atual in afd.estados_finais

