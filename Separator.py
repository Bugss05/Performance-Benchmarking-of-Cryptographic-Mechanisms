import pandas as pd
import os

def mainB(): 
    # Carregar o arquivo CSV
    input_file = 'Stats\\AES_performance.csv'
    data = pd.read_csv(input_file)

    # Garantir que a coluna 'Algorithm-Mode' existe
    if 'Algorithm-Mode' not in data.columns:
        raise ValueError("O arquivo CSV de entrada deve conter uma coluna 'Algorithm-Mode'.")

    # Agrupar por 'Algorithm-Mode' e salvar cada grupo em um arquivo CSV separado
    for mode, group in data.groupby('Algorithm-Mode'):
        output_file = os.path.join('Stats', f"{mode}.csv")
        group.to_csv(output_file, index=False)
        print(f"Salvo: {output_file}")
    
    # Remover o csv inicial para poupar espaco
    os.remove(input_file)
    print(f"Removido: {input_file}")
    
if __name__ == "__main__":
    mainB()