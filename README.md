# Minimizador de AFD a partir de Gramática Regular

## Execução

```bash
python3 main.py entrada.txt saida.csv
```

## Formato de Entrada

```
<S> ::= a<A> | b<B>
<A> ::= a<A> | a
<B> ::= b | ε
```

## Formato de Saída (CSV)

```
estado,simbolo,destino,eh_inicial,eh_final
q0,a,q1,true,false
q1,b,q0,false,true
```

