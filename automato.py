"""
Módulo que define a estrutura de dados do Autômato Finito.

Este módulo contém a classe Automato que representa tanto AFN (Autômato Finito
Não-determinístico) quanto AFD (Autômato Finito Determinístico), além de
funções auxiliares para manipulação de autômatos.
"""

from dataclasses import dataclass, field


@dataclass
class Automato:
    """
    Representa um autômato finito (AFN ou AFD).
    
    Atributos:
        estados: Conjunto de todos os estados do autômato
        alfabeto: Conjunto de símbolos do alfabeto de entrada
        estado_inicial: Estado inicial do autômato
        estados_finais: Conjunto de estados de aceitação
        transicoes: Dicionário de transições {estado: {simbolo: destino(s)}}
    """
    estados: set = field(default_factory=set)
    alfabeto: set = field(default_factory=set)
    estado_inicial: str = ''
    estados_finais: set = field(default_factory=set)
    transicoes: dict = field(default_factory=dict)
    
    def adicionar_estado(self, estado):
        """Adiciona um estado ao conjunto de estados."""
        self.estados.add(estado)
    
    def adicionar_simbolo(self, simbolo):
        """Adiciona um símbolo ao alfabeto."""
        self.alfabeto.add(simbolo)
    
    def definir_estado_inicial(self, estado):
        """Define o estado inicial e o adiciona ao conjunto de estados."""
        self.estado_inicial = estado
        self.estados.add(estado)
    
    def adicionar_estado_final(self, estado):
        """Marca um estado como final e o adiciona ao conjunto de estados."""
        self.estados_finais.add(estado)
        self.estados.add(estado)
    
    def adicionar_transicao_afn(self, origem, simbolo, destino):
        """
        Adiciona uma transição para AFN (não-determinístico).
        Permite múltiplos destinos para o mesmo par (estado, símbolo).
        """
        self.estados.add(origem)
        self.estados.add(destino)
        self.alfabeto.add(simbolo)
        
        if origem not in self.transicoes:
            self.transicoes[origem] = {}
        
        if simbolo not in self.transicoes[origem]:
            self.transicoes[origem][simbolo] = set()
        
        self.transicoes[origem][simbolo].add(destino)
    
    def adicionar_transicao_afd(self, origem, simbolo, destino):
        """
        Adiciona uma transição para AFD (determinístico).
        Cada par (estado, símbolo) tem exatamente um destino.
        """
        self.estados.add(origem)
        self.estados.add(destino)
        self.alfabeto.add(simbolo)
        
        if origem not in self.transicoes:
            self.transicoes[origem] = {}
        
        self.transicoes[origem][simbolo] = destino
    
    def obter_transicao(self, estado, simbolo):
        """
        Retorna o(s) estado(s) destino para uma transição.
        Retorna None se a transição não existir.
        """
        if estado in self.transicoes and simbolo in self.transicoes[estado]:
            return self.transicoes[estado][simbolo]
        return None
    
    def copiar(self):
        """Cria uma cópia profunda do autômato."""
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
    """
    Cria um nome legível para um estado que representa um conjunto de estados.
    Usado na determinização para nomear estados compostos.
    Ex: {q0, q1, q2} -> '{q0,q1,q2}'
    """
    if not conjunto:
        return '{}'
    elementos_ordenados = sorted(conjunto)
    return '{' + ','.join(elementos_ordenados) + '}'


def reconhecer_palavra(afd, palavra):
    """
    Verifica se o AFD reconhece (aceita) uma palavra.
    
    Percorre o autômato símbolo por símbolo e verifica se
    termina em um estado final.
    
    Retorna True se a palavra é aceita, False caso contrário.
    """
    estado_atual = afd.estado_inicial
    
    for simbolo in palavra:
        # Símbolo não está no alfabeto
        if simbolo not in afd.alfabeto:
            return False
        
        transicao = afd.obter_transicao(estado_atual, simbolo)
        if transicao is None:
            return False
        
        # Trata caso de transição em AFN (conjunto de estados)
        if isinstance(transicao, set):
            if len(transicao) == 1:
                estado_atual = next(iter(transicao))
            else:
                return False
        else:
            estado_atual = transicao
    
    return estado_atual in afd.estados_finais
