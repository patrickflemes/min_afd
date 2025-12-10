"""
Módulo principal do sistema de minimização de AFD.

FLUXO GERAL DO SISTEMA:
1. Leitura do arquivo de entrada contendo a gramática regular (BNF)
2. Parsing da gramática para estrutura de dados interna
3. Conversão da gramática para AFN (Autômato Finito Não-determinístico)
4. Determinização do AFN para AFD (Autômato Finito Determinístico)
5. Remoção de estados inalcançáveis
6. Completação do AFD com estado poço (se necessário)
7. Minimização do AFD usando algoritmo de particionamento
8. Remoção do estado poço para representação mais limpa
9. Salvamento do resultado em arquivo CSV
"""

import sys

from gramatica import ler_arquivo_texto, parsear_gramatica
from conversao import converter_gramatica_para_afn, determinizar_afn
from minimizacao import remover_inalcancaveis, completar_com_estado_poco, minimizar_afd, remover_estado_poco
from io_saida import salvar_afd_csv, imprimir_afd


def obter_argumentos():
    """
    Obtém os caminhos de entrada e saída dos argumentos da linha de comando.
    
    Uso: python main.py [entrada.txt] [saida.csv] [--verbose|-v]
    - Se nenhum argumento for passado, usa 'entrada.txt' e 'saida.csv' como padrão.
    """
    if len(sys.argv) >= 3:
        caminho_entrada = sys.argv[1]
        caminho_saida = sys.argv[2]
    elif len(sys.argv) == 2:
        caminho_entrada = sys.argv[1]
        caminho_saida = 'saida.csv'
    else:
        caminho_entrada = 'entrada.txt'
        caminho_saida = 'saida.csv'
    
    return caminho_entrada, caminho_saida


def executar_pipeline(caminho_entrada, caminho_saida, verbose=False):
    """
    Executa todo o pipeline de conversão e minimização.
    
    Etapas:
    1. Lê o arquivo de gramática
    2. Parseia a gramática (BNF)
    3. Converte gramática → AFN
    4. Determiniza AFN → AFD
    5. Remove estados inalcançáveis
    6. Completa com estado poço
    7. Minimiza o AFD
    8. Remove estado poço
    9. Salva resultado em CSV
    """
    # Etapa 1: Leitura do arquivo de entrada
    if verbose:
        print(f"Lendo arquivo: {caminho_entrada}")
    
    texto = ler_arquivo_texto(caminho_entrada)
    
    # Etapa 2: Parsing da gramática
    if verbose:
        print("Parseando gramática...")
    
    gramatica, nao_terminal_inicial = parsear_gramatica(texto)
    
    if verbose:
        print(f"Não-terminal inicial: {nao_terminal_inicial}")
        print(f"Produções encontradas:")
        for nt, prods in gramatica.items():
            print(f"  <{nt}> ::= {' | '.join(prods)}")
    
    # Etapa 3: Conversão da gramática para AFN
    if verbose:
        print("\nConvertendo gramática para AFN...")
    
    afn = converter_gramatica_para_afn(gramatica, nao_terminal_inicial)
    
    if verbose:
        print("AFN gerado:")
        imprimir_afd(afn)
    
    # Etapa 4: Determinização do AFN para AFD
    if verbose:
        print("\nDeterminizando AFN...")
    
    afd = determinizar_afn(afn)
    
    if verbose:
        print("AFD após determinização:")
        imprimir_afd(afd)
    
    # Etapa 5: Remoção de estados inalcançáveis
    if verbose:
        print("\nRemovendo estados inalcançáveis...")
    
    afd = remover_inalcancaveis(afd)
    
    if verbose:
        print("AFD após remoção de inalcançáveis:")
        imprimir_afd(afd)
    
    # Etapa 6: Completação com estado poço
    if verbose:
        print("\nCompletando AFD com estado poço...")
    
    afd = completar_com_estado_poco(afd)
    
    if verbose:
        print("AFD após completar com poço:")
        imprimir_afd(afd)
    
    # Etapa 7: Minimização do AFD
    if verbose:
        print("\nMinimizando AFD...")
    
    afd_minimo = minimizar_afd(afd)
    
    if verbose:
        print("AFD minimizado:")
        imprimir_afd(afd_minimo)
    
    # Etapa 8: Remoção do estado poço
    if verbose:
        print("\nRemovendo estado poço...")
    
    afd_minimo = remover_estado_poco(afd_minimo)
    
    if verbose:
        print("AFD após remoção do poço:")
        imprimir_afd(afd_minimo)
    
    # Etapa 9: Salvamento do resultado
    if verbose:
        print(f"\nSalvando resultado em: {caminho_saida}")
    
    salvar_afd_csv(afd_minimo, caminho_saida)
    
    if verbose:
        print("Processo concluído com sucesso!")
    
    return afd_minimo


def main():
    """
    Função principal que coordena a execução do programa.
    Trata erros de arquivo não encontrado e outros erros de processamento.
    """
    caminho_entrada, caminho_saida = obter_argumentos()
    
    # Verifica se modo verboso está ativado
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    try:
        executar_pipeline(caminho_entrada, caminho_saida, verbose)
        print(f"AFD minimizado salvo em: {caminho_saida}")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_entrada}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
