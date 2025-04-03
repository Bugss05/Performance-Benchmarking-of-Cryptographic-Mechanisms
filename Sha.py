import os
import timeit
import csv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Definição dos tamanhos dos arquivos em bytes
tamanhos_arquivos = [8, 64, 512, 4096, 32768, 262144, 2097152]
# Número de arquivos a serem gerados para cada tamanho
num_arquivos = 1000
# Número de vezes que cada arquivo será processado
num_iteracoes = 100
# Nome do arquivo CSV para armazenar os resultados
csv_filename = "sha256_benchmark.csv"

# Função para gerar um arquivo com dados aleatórios
def gerar_arquivo(nome_arquivo, tamanho):
    with open(nome_arquivo, "wb") as f:
        f.write(os.urandom(tamanho))

# Função para calcular o hash SHA-256 de um arquivo
def calcular_hash(nome_arquivo):
    hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
    with open(nome_arquivo, "rb") as f:
        hasher.update(f.read())
    return hasher.finalize()

# Criar e abrir o arquivo CSV para armazenar os tempos com cabeçalho
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Tipo de Encriptação", "Tamanho do Arquivo (bytes)", "Tempo de Encriptação (μs)", "Tempo de Verificação (μs)"])
    
    # Lista para armazenar os nomes dos arquivos gerados
    arquivos_gerados = []
    
    # Loop pelos diferentes tamanhos de arquivo
    for tamanho in tamanhos_arquivos:
        for i in range(num_arquivos):
            nome_arquivo = f"arquivo_{tamanho}_{i}.bin"
            gerar_arquivo(nome_arquivo, tamanho)
            arquivos_gerados.append(nome_arquivo)
            
            for _ in range(num_iteracoes):
                # Medir tempo de hashing
                tempo_encriptacao = timeit.timeit(lambda: calcular_hash(nome_arquivo), number=1) * 1e6  # Convertendo para microssegundos
                
                # Medir tempo de verificação (recalculando o hash para simular a verificação)
                tempo_verificacao = timeit.timeit(lambda: calcular_hash(nome_arquivo), number=1) * 1e6  # Convertendo para microssegundos
                
                # Armazenar os dados no CSV
                writer.writerow(["SHA-256", tamanho, tempo_encriptacao, tempo_verificacao])
    
    # Remover todos os arquivos gerados após o processamento
        for arquivo in arquivos_gerados:
            os.remove(arquivo)
        arquivos_gerados.clear()

print(f"Processo concluído. Os resultados foram armazenados em '{csv_filename}', e os arquivos temporários foram removidos.")
