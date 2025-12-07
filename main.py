import sys

from gramatica import ler_arquivo_texto, parsear_gramatica
from conversao import converter_gramatica_para_afn, determinizar_afn
from minimizacao import remover_inalcancaveis, completar_com_estado_poco, minimizar_afd, remover_estado_poco
from io_saida import salvar_afd_csv, imprimir_afd


def obter_argumentos():
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
    if verbose:
        print(f"Lendo arquivo: {caminho_entrada}")
    
    texto = ler_arquivo_texto(caminho_entrada)
    
    if verbose:
        print("Parseando gramática...")
    
    gramatica, nao_terminal_inicial = parsear_gramatica(texto)
    
    if verbose:
        print(f"Não-terminal inicial: {nao_terminal_inicial}")
        print(f"Produções encontradas:")
        for nt, prods in gramatica.items():
            print(f"  <{nt}> ::= {' | '.join(prods)}")
    
    if verbose:
        print("\nConvertendo gramática para AFN...")
    
    afn = converter_gramatica_para_afn(gramatica, nao_terminal_inicial)
    
    if verbose:
        print("AFN gerado:")
        imprimir_afd(afn)
    
    if verbose:
        print("\nDeterminizando AFN...")
    
    afd = determinizar_afn(afn)
    
    if verbose:
        print("AFD após determinização:")
        imprimir_afd(afd)
    
    if verbose:
        print("\nRemovendo estados inalcançáveis...")
    
    afd = remover_inalcancaveis(afd)
    
    if verbose:
        print("AFD após remoção de inalcançáveis:")
        imprimir_afd(afd)
    
    if verbose:
        print("\nCompletando AFD com estado poço...")
    
    afd = completar_com_estado_poco(afd)
    
    if verbose:
        print("AFD após completar com poço:")
        imprimir_afd(afd)
    
    if verbose:
        print("\nMinimizando AFD...")
    
    afd_minimo = minimizar_afd(afd)
    
    if verbose:
        print("AFD minimizado:")
        imprimir_afd(afd_minimo)
    
    if verbose:
        print(f"\nSalvando resultado em: {caminho_saida}")
    
    salvar_afd_csv(afd_minimo, caminho_saida)
    
    if verbose:
        print("Processo concluído com sucesso!")
    
    return afd_minimo


def main():
    caminho_entrada, caminho_saida = obter_argumentos()
    
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

