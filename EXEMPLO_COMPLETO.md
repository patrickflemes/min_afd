# Exemplo Completo: Passo a Passo

Este documento demonstra o processo completo de conversão de uma gramática regular para um AFD minimizado.

## Gramática de Entrada

```
<S> ::= a<A>
<A> ::= a<A> | b
```

**Linguagem gerada**: `a⁺b` (uma ou mais letras `a` seguidas de uma letra `b`)

**Palavras aceitas**: `ab`, `aab`, `aaab`, `aaaab`, ...

**Palavras rejeitadas**: `b`, `a`, `ba`, `abb`, ...

---

## Passo 1: Parsing da Gramática

O parser lê o arquivo e extrai as produções:

```
Não-terminal inicial: S

Produções:
  S → a<A>
  A → a<A>
  A → b
```

**Estrutura de dados resultante:**

```python
gramatica = {
    'S': ['a<A>'],
    'A': ['a<A>', 'b']
}
nao_terminal_inicial = 'S'
```

---

## Passo 2: Conversão para AFN

Cada produção é convertida em uma transição:

| Produção | Transição |
|----------|-----------|
| S → a\<A\> | δ(S, a) = {A} |
| A → a\<A\> | δ(A, a) = {A} |
| A → b | δ(A, b) = {FINAL} |

**AFN resultante:**

```
Estados: {S, A, FINAL}
Alfabeto: {a, b}
Estado inicial: S
Estados finais: {FINAL}

Tabela de transições:
┌────────┬───────────┬───────────┐
│ Estado │     a     │     b     │
├────────┼───────────┼───────────┤
│   S    │    {A}    │     ∅     │
│   A    │    {A}    │  {FINAL}  │
│ FINAL  │     ∅     │     ∅     │
└────────┴───────────┴───────────┘
```

**Diagrama do AFN:**

```
        a           b
  ┌──────────┐
  │          ▼
(S) ──a──▶ (A) ──b──▶ ((FINAL))
           ▲ │
           └─┘
            a
```

---

## Passo 3: Determinização (AFN → AFD)

A determinização usa o algoritmo de construção de subconjuntos.

### Processo:

**Estado inicial do AFD**: `{S}`

**Iteração 1** - Processar `{S}`:
- δ({S}, a) = δ(S, a) = {A} → novo estado `{A}`
- δ({S}, b) = δ(S, b) = ∅ → sem transição

**Iteração 2** - Processar `{A}`:
- δ({A}, a) = δ(A, a) = {A} → estado já existe
- δ({A}, b) = δ(A, b) = {FINAL} → novo estado `{FINAL}`

**Iteração 3** - Processar `{FINAL}`:
- δ({FINAL}, a) = ∅ → sem transição
- δ({FINAL}, b) = ∅ → sem transição

**AFD resultante:**

```
Estados: {{S}, {A}, {FINAL}}
Alfabeto: {a, b}
Estado inicial: {S}
Estados finais: {{FINAL}}

Tabela de transições:
┌──────────┬──────────┬──────────┐
│  Estado  │    a     │    b     │
├──────────┼──────────┼──────────┤
│   {S}    │   {A}    │    -     │
│   {A}    │   {A}    │ {FINAL}  │
│ {FINAL}  │    -     │    -     │
└──────────┴──────────┴──────────┘
```

**Diagrama do AFD após determinização:**

```
        a           b
({S}) ──────▶ ({A}) ──────▶ (({FINAL}))
               ▲ │
               └─┘
                a
```

---

## Passo 4: Remoção de Estados Inalcançáveis

Verificamos quais estados são alcançáveis a partir do estado inicial:

```
Alcançáveis a partir de {S}:
  {S} → (via a) → {A}
  {A} → (via a) → {A}
  {A} → (via b) → {FINAL}

Estados alcançáveis: {{S}, {A}, {FINAL}}
```

**Neste exemplo**: Todos os estados são alcançáveis, nenhum é removido.

---

## Passo 5: Completar com Estado Poço

Verificamos se existem transições indefinidas:

```
Transições indefinidas:
  δ({S}, b) = ?     → falta!
  δ({FINAL}, a) = ? → falta!
  δ({FINAL}, b) = ? → falta!
```

**Criamos o estado POÇO** e adicionamos as transições faltantes:

```
Estados: {{S}, {A}, {FINAL}, POCO}
Alfabeto: {a, b}
Estado inicial: {S}
Estados finais: {{FINAL}}

Tabela de transições completa:
┌──────────┬──────────┬──────────┐
│  Estado  │    a     │    b     │
├──────────┼──────────┼──────────┤
│   {S}    │   {A}    │   POCO   │
│   {A}    │   {A}    │ {FINAL}  │
│ {FINAL}  │   POCO   │   POCO   │
│   POCO   │   POCO   │   POCO   │
└──────────┴──────────┴──────────┘
```

**Diagrama do AFD completo:**

```
              a                b
      ┌──────────────▶ ({A}) ──────────▶ (({FINAL}))
      │                ▲ │                    │
    ({S})              └─┘                    │ a, b
      │                 a                     ▼
      │ b                              ┌───────────┐
      │                                │           │
      └───────────────────────────────▶│   POCO    │◀─┐
                                       │           │  │ a, b
                                       └───────────┘──┘
```

---

## Passo 6: Minimização

### 6.1 Partição Inicial

Dividimos os estados em finais e não-finais:

```
P₀ = { {FINAL} }           ← estados finais
P₁ = { {S}, {A}, POCO }    ← estados não-finais

Partição inicial: [ P₀, P₁ ]
Índices: P₀ = bloco 0, P₁ = bloco 1
```

### 6.2 Primeira Iteração de Refinamento

**Analisando bloco P₁ = {{S}, {A}, POCO}:**

Calculamos a assinatura de cada estado (para qual bloco cada símbolo leva):

| Estado | δ(·, a) | δ(·, b) | Bloco de δ(·, a) | Bloco de δ(·, b) | Assinatura |
|--------|---------|---------|------------------|------------------|------------|
| {S}    | {A}     | POCO    | 1                | 1                | (1, 1)     |
| {A}    | {A}     | {FINAL} | 1                | 0                | (1, 0)     |
| POCO   | POCO    | POCO    | 1                | 1                | (1, 1)     |

**Agrupando por assinatura:**
- Assinatura (1, 1): {{S}, POCO}
- Assinatura (1, 0): {{A}}

**Nova partição após iteração 1:**

```
P₀ = { {FINAL} }        ← bloco 0
P₁ = { {S}, POCO }      ← bloco 1 (assinatura 1,1)
P₂ = { {A} }            ← bloco 2 (assinatura 1,0)
```

**Houve mudança!** Continua refinando...

### 6.3 Segunda Iteração de Refinamento

**Analisando bloco P₁ = {{S}, POCO}:**

| Estado | δ(·, a) | δ(·, b) | Bloco de δ(·, a) | Bloco de δ(·, b) | Assinatura |
|--------|---------|---------|------------------|------------------|------------|
| {S}    | {A}     | POCO    | 2                | 1                | (2, 1)     |
| POCO   | POCO    | POCO    | 1                | 1                | (1, 1)     |

**Assinaturas diferentes!** O bloco é dividido:
- Assinatura (2, 1): {{S}}
- Assinatura (1, 1): {POCO}

**Nova partição após iteração 2:**

```
P₀ = { {FINAL} }    ← bloco 0
P₁ = { POCO }       ← bloco 1
P₂ = { {A} }        ← bloco 2
P₃ = { {S} }        ← bloco 3
```

### 6.4 Terceira Iteração de Refinamento

Todos os blocos têm tamanho 1, não há mais refinamento possível.

**Partição final:**

```
P₀ = { {FINAL} }    → q0 (final)
P₁ = { POCO }       → q1
P₂ = { {A} }        → q2
P₃ = { {S} }        → q3 (inicial)
```

### 6.5 Construção do AFD Mínimo

Renomeamos os blocos e construímos as transições usando um representante de cada bloco:

```
Mapeamento:
  {FINAL} → q0
  POCO    → q1
  {A}     → q2
  {S}     → q3

Transições (usando representantes):
  δ(q3, a) = q2   (pois δ({S}, a) = {A} que está em q2)
  δ(q3, b) = q1   (pois δ({S}, b) = POCO que está em q1)
  δ(q2, a) = q2   (pois δ({A}, a) = {A} que está em q2)
  δ(q2, b) = q0   (pois δ({A}, b) = {FINAL} que está em q0)
  δ(q1, a) = q1   (pois δ(POCO, a) = POCO que está em q1)
  δ(q1, b) = q1   (pois δ(POCO, b) = POCO que está em q1)
  δ(q0, a) = q1   (pois δ({FINAL}, a) = POCO que está em q1)
  δ(q0, b) = q1   (pois δ({FINAL}, b) = POCO que está em q1)
```

---

## Resultado Final: AFD Mínimo

```
Estados: {q0, q1, q2, q3}
Alfabeto: {a, b}
Estado inicial: q3
Estados finais: {q0}

Tabela de transições:
┌────────┬──────┬──────┐
│ Estado │   a  │   b  │
├────────┼──────┼──────┤
│   q3*  │  q2  │  q1  │
│   q2   │  q2  │  q0  │
│  (q0)  │  q1  │  q1  │
│   q1   │  q1  │  q1  │
└────────┴──────┴──────┘

* = inicial
( ) = final
```

**Diagrama do AFD mínimo:**

```
              a                b
      ┌──────────────▶ (q2) ──────────▶ ((q0))
      │                ▲ │                 │
    (q3)*              └─┘                 │ a, b
      │                 a                  ▼
      │ b                            ┌──────────┐
      │                              │          │
      └─────────────────────────────▶│   (q1)   │◀─┐
                                     │          │  │ a, b
                                     └──────────┘──┘
```

---

## Saída CSV

O arquivo `saida.csv` gerado:

```csv
estado,simbolo,destino,eh_inicial,eh_final
q0,a,q1,false,true
q0,b,q1,false,true
q1,a,q1,false,false
q1,b,q1,false,false
q2,a,q2,false,false
q2,b,q0,false,false
q3,a,q2,true,false
q3,b,q1,true,false
```

---

## Verificação

Testando algumas palavras:

| Palavra | Caminho | Aceita? |
|---------|---------|---------|
| `ab`    | q3 →(a)→ q2 →(b)→ q0 | ✓ Sim (q0 é final) |
| `aab`   | q3 →(a)→ q2 →(a)→ q2 →(b)→ q0 | ✓ Sim |
| `aaab`  | q3 →(a)→ q2 →(a)→ q2 →(a)→ q2 →(b)→ q0 | ✓ Sim |
| `b`     | q3 →(b)→ q1 | ✗ Não (q1 não é final) |
| `a`     | q3 →(a)→ q2 | ✗ Não (q2 não é final) |
| `ba`    | q3 →(b)→ q1 →(a)→ q1 | ✗ Não |
| `abb`   | q3 →(a)→ q2 →(b)→ q0 →(b)→ q1 | ✗ Não |

O AFD minimizado reconhece corretamente a linguagem `a⁺b`.

---

## Executando o Exemplo

```bash
# Criar arquivo de entrada
echo '<S> ::= a<A>
<A> ::= a<A> | b' > entrada.txt

# Executar com modo verbose
python3 main.py entrada.txt saida.csv --verbose

# Ver resultado
cat saida.csv
```

