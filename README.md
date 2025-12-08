# Minimizador de AFD a partir de Gramática Regular


## Visão Geral

O programa realiza as seguintes etapas:

1. **Leitura e parsing** da gramática regular (formato BNF)
2. **Conversão** da gramática para AFN (Autômato Finito Não-determinístico)
3. **Determinização** do AFN para AFD
4. **Remoção de estados inalcançáveis**
5. **Completamento** com estado poço (se necessário)
6. **Minimização** do AFD usando o algoritmo de particionamento
7. **Exportação** do resultado em formato CSV

---

## Execução

### Uso básico

```bash
python3 main.py entrada.txt saida.csv
```

### Parâmetros

| Argumento | Descrição | Valor padrão |
|-----------|-----------|--------------|
| `entrada.txt` | Arquivo com a gramática regular | `entrada.txt` |
| `saida.csv` | Arquivo de saída com o AFD minimizado | `saida.csv` |
| `--verbose` ou `-v` | Exibe detalhes de cada etapa do processamento | desativado |

### Exemplos

```bash
# Execução simples
python3 main.py

# Com arquivos específicos
python3 main.py minha_gramatica.txt resultado.csv

# Com modo verbose (detalhado)
python3 main.py entrada.txt saida.csv --verbose
```

---

## Formato de Entrada

A gramática deve estar no formato BNF (Backus-Naur Form) para gramáticas regulares à direita:

```
<S> ::= a<A> | b<B>
<A> ::= a<A> | a
<B> ::= b | ε
```

### Regras de sintaxe

- **Não-terminais**: Delimitados por `< >` (ex: `<S>`, `<A>`)
- **Terminais**: Caracteres simples (ex: `a`, `b`, `0`, `1`)
- **Produções**: Separadas por `|` (pipe)
- **Epsilon (ε)**: Representa a cadeia vazia
- **Definição**: Usa `::=` para separar lado esquerdo e direito

### Exemplo de entrada (`entrada.txt`)

```
<S> ::= a<A>
<A> ::= a<A> | b
```

Esta gramática gera a linguagem: `a+b` (uma ou mais letras `a` seguidas de uma letra `b`).

---

## Formato de Saída

O AFD minimizado é salvo em formato CSV com as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| `estado` | Nome do estado |
| `simbolo` | Símbolo de entrada da transição |
| `destino` | Estado de destino |
| `eh_inicial` | `true` se for o estado inicial |
| `eh_final` | `true` se for um estado de aceitação |

### Exemplo de saída (`saida.csv`)

```csv
estado,simbolo,destino,eh_inicial,eh_final
q0,a,q0,true,false
q0,b,q1,true,false
q1,,,false,true
```

---

## Arquitetura do Código

```
min_afd/
├── main.py          # Ponto de entrada e pipeline principal
├── automato.py      # Classe Automato e funções auxiliares
├── gramatica.py     # Parsing de gramáticas regulares
├── conversao.py     # Conversão gramática→AFN e determinização
├── minimizacao.py   # Algoritmos de minimização
├── io_saida.py      # Funções de entrada/saída
└── entrada.txt      # Exemplo de gramática
```

### Descrição dos módulos

| Módulo | Responsabilidade |
|--------|-----------------|
| `main.py` | Orquestra o pipeline de conversão e minimização |
| `automato.py` | Define a estrutura de dados `Automato` com estados, transições e alfabeto |
| `gramatica.py` | Lê e parseia gramáticas no formato BNF |
| `conversao.py` | Converte gramática → AFN e AFN → AFD (determinização) |
| `minimizacao.py` | Remove inalcançáveis, completa com poço e minimiza o AFD |
| `io_saida.py` | Exporta o AFD para CSV e imprime no console |

---

## Algoritmo de Minimização

O algoritmo de minimização implementado é baseado no **Algoritmo de Particionamento** (também conhecido como algoritmo de refinamento de partições ou algoritmo de Moore/Hopcroft simplificado).

### Objetivo

Dado um AFD, encontrar o **AFD mínimo equivalente** — ou seja, o autômato com o menor número de estados que reconhece a mesma linguagem.

### Princípio Fundamental

Dois estados são **equivalentes** se, para qualquer cadeia de entrada, ambos levam a estados que têm o mesmo comportamento (ambos aceitam ou ambos rejeitam).

O algoritmo funciona identificando estados **distinguíveis** (não-equivalentes) e agrupando os **indistinguíveis** em um único estado.

### Etapas do Algoritmo

#### 1. Partição Inicial

O algoritmo começa dividindo os estados em duas partições:
- **P₀**: Estados finais (de aceitação)
- **P₁**: Estados não-finais (de rejeição)

Esta divisão inicial é válida porque estados finais e não-finais são claramente distinguíveis — a cadeia vazia os diferencia.

```python
if not estados_nao_finais:
    particao = [afd.estados_finais.copy()]
elif not afd.estados_finais:
    particao = [estados_nao_finais.copy()]
else:
    particao = [afd.estados_finais.copy(), estados_nao_finais.copy()]
```

#### 2. Refinamento Iterativo

O algoritmo então refina as partições iterativamente:

Para cada bloco da partição atual:
1. Calcular a **assinatura** de cada estado
2. Agrupar estados com a mesma assinatura
3. Se um bloco foi dividido, marcar que houve mudança

**Assinatura de um estado**: Tupla indicando para qual bloco da partição cada símbolo do alfabeto leva o estado.

```python
for estado in bloco:
    assinatura = tuple(
        obter_destino_bloco(estado, simbolo, particao)
        for simbolo in sorted(afd.alfabeto)
    )
    
    if assinatura not in sub_blocos:
        sub_blocos[assinatura] = set()
    sub_blocos[assinatura].add(estado)
```

**Exemplo visual:**

```
Partição inicial: {q0, q1, q2} | {q3, q4}
                   (não-finais)   (finais)

Alfabeto: {a, b}

Assinaturas (para qual bloco cada símbolo leva):
  q0: δ(q0,a)→bloco0, δ(q0,b)→bloco1  →  assinatura (0, 1)
  q1: δ(q1,a)→bloco0, δ(q1,b)→bloco1  →  assinatura (0, 1)
  q2: δ(q2,a)→bloco1, δ(q2,b)→bloco0  →  assinatura (1, 0)

Refinamento: {q0, q1} | {q2} | {q3, q4}
              (mesma)  (diferente)
```

#### 3. Critério de Parada

O algoritmo termina quando uma iteração não produz mais divisões — ou seja, todos os estados em cada bloco são indistinguíveis entre si.

```python
mudou = True
while mudou:
    mudou = False
    # ... refinamento ...
    if len(sub_blocos) > 1:
        mudou = True
```

#### 4. Construção do AFD Mínimo

Após a convergência:
1. Cada bloco da partição final torna-se um estado do AFD mínimo
2. Um representante de cada bloco é usado para determinar as transições
3. O estado inicial é o bloco que contém o estado inicial original
4. Estados finais são os blocos que contêm pelo menos um estado final original

```python
for i, bloco in enumerate(particao):
    nome_bloco = nomes_blocos[i]
    estado_representante = next(iter(bloco))
    
    for simbolo in afd.alfabeto:
        transicao = afd.obter_transicao(estado_representante, simbolo)
        if transicao is not None:
            bloco_destino = mapeamento_estado_para_bloco[transicao]
            nome_destino = nomes_blocos[bloco_destino]
            afd_minimo.adicionar_transicao_afd(nome_bloco, simbolo, nome_destino)
```

### Complexidade

- **Tempo**: O(n² × |Σ|) no pior caso, onde n é o número de estados e |Σ| é o tamanho do alfabeto
- **Espaço**: O(n) para armazenar as partições

### Exemplo Completo

**Entrada**: AFD com estados {A, B, C, D, E} onde D e E são finais

```
Passo 1 - Partição inicial:
  Π₀ = { {D, E}, {A, B, C} }

Passo 2 - Primeira iteração:
  Analisar {A, B, C}:
    A: (bloco de δ(A,0), bloco de δ(A,1)) = (1, 0)
    B: (bloco de δ(B,0), bloco de δ(B,1)) = (1, 0)
    C: (bloco de δ(C,0), bloco de δ(C,1)) = (0, 1)
  
  Π₁ = { {D, E}, {A, B}, {C} }

Passo 3 - Segunda iteração:
  Nenhuma divisão adicional possível
  
  Π_final = { {D, E}, {A, B}, {C} }

Resultado: AFD mínimo com 3 estados
  - q0 representa {A, B}
  - q1 representa {C}  
  - q2 representa {D, E}
```

---

## Pipeline Completo

O fluxo completo de execução:

```
┌─────────────────┐
│  Gramática BNF  │
│  (entrada.txt)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Parsing      │  ← gramatica.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Gramática →   │  ← conversao.py
│      AFN        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Determinização │  ← conversao.py
│   AFN → AFD     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Remoção de   │  ← minimizacao.py
│  Inalcançáveis  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Completar com  │  ← minimizacao.py
│   Estado Poço   │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│    MINIMIZAÇÃO      │  ← minimizacao.py
│  (Particionamento)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────┐
│   AFD Mínimo    │
│   (saida.csv)   │
└─────────────────┘
```

---

## Modo Verbose

Execute com `--verbose` ou `-v` para ver cada etapa:

```bash
python3 main.py entrada.txt saida.csv -v
```

Saída exemplo:

```
Lendo arquivo: entrada.txt
Parseando gramática...
Não-terminal inicial: S
Produções encontradas:
  <S> ::= a<A>
  <A> ::= a<A> | b

Convertendo gramática para AFN...
AFN gerado:
==================================================
AUTÔMATO FINITO DETERMINÍSTICO
==================================================
Estados: ['A', 'FINAL', 'S']
Alfabeto: ['a', 'b']
Estado inicial: S
Estados finais: ['FINAL']
Transições:
  δ(A, a) = {'A'}
  δ(A, b) = {'FINAL'}
  δ(S, a) = {'A'}
==================================================

Determinizando AFN...
...
Minimizando AFD...
...
AFD minimizado salvo em: saida.csv
```
