import os
import timeit
import csv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

#-------------------------------------------------------

# Constantes:

# Tamanhos dos arquivos em bytes
tamanhos_arquivos = [8, 64, 512, 4096, 32768, 262144, 2097152]
# Número de arquivos a serem gerados para cada tamanho
num_arquivos = 1000
# Número de iterações por arquivo
num_iteracoes = 100
# Nome do arquivo CSV para armazenar os resultados
csv_filename = "sha256_benchmark.csv"

#-------------------------------------------------------


# Função para gerar um arquivo com dados aleatórios
import string
import random

# Função para gerar um arquivo com texto aleatório
def gerar_arquivo(nome_arquivo, tamanho):
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        # Gera um texto aleatório com caracteres alfanuméricos
        conteudo = ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))
        f.write(conteudo)

# Função para calcular o hash SHA-256 de um arquivo
def calcular_hash(nome_arquivo):
    """ Explicação da class Hash():
    
        - hash: declaração da função de hashing a usar. Neste caso, SHA-256.
        
        - backend: define o script que realiza as operações criptográficas necessárias.
        Escolhemos o default_backend(), baseado em OpenSSL, por ser dos mais usados e testados.
    """
    hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
    with open(nome_arquivo, "rb") as f:
        hasher.update(f.read())
    return hasher.finalize()


def main():
    # Criar e abrir o arquivo CSV para armazenar os tempos com cabeçalho
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Tipo de Encriptação", "Tamanho do Arquivo (bytes)", "Iteração", "Tempo de Geração (μs)"])

        # Lista para armazenar os nomes dos arquivos gerados
        arquivos_gerados = []

        # Loop pelos diferentes tamanhos de arquivo
        for tamanho in tamanhos_arquivos:
            for i in range(num_arquivos):
                nome_arquivo = f"arquivo_{tamanho}_{i}.txt"
                gerar_arquivo(nome_arquivo, tamanho)
                arquivos_gerados.append(nome_arquivo)

                for iteracao in range(num_iteracoes):
                    # Medir tempo de hashing em microsegundos (s * 1e6)
                    tempo_geracao = timeit.timeit(lambda: calcular_hash(nome_arquivo), number=1) * 1e6

                    # Armazenar os dados no CSV
                    writer.writerow(["SHA-256", tamanho, iteracao + 1, tempo_geracao])

        # Remover todos os arquivos gerados após o processamento
            for arquivo in arquivos_gerados:
                os.remove(arquivo)
            arquivos_gerados.clear()

    print(f"Processo concluído. Os resultados foram armazenados em '{csv_filename}', e os arquivos temporários foram removidos.")

if __name__ == "__main__":
    main()