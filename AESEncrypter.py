import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import csv
import statistics
import matplotlib.pyplot as plt
import timeit


# Function to generate random files of specified sizes
def generate_random_files(sizes, folder="random_files"):
    for size in sizes:
        filename = os.path.join(folder, f"file_{size}.txt")
        with open(filename, "wb") as f:
            f.write(os.urandom(size))

# Function to encrypt data using AES-256
def aes_encrypt(data, key, iv, cipher):
    """ Explicação da class Cipher():
    
        - Algorithms: declaração do algoritmo a usar. Neste caso, AES
        
        - Modes: define o modo de funcionamento do AES, ou seja, a sua variação. Usamos
        neste caso o CBC, que combina cada bloco com o seu anterior por XOR, exceto o
        primeiro, que é encriptado segundo uma chave (iv) com o tamanho do bloco (16 bits)
        
        - Backend: define o script que realiza as operações criptográficas necessárias.
        Escolhemos o default_backend(), baseado em OpenSSL, por ser dos mais usados e testados.
    """

    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return encryptor.update(padded_data) + encryptor.finalize()

# Function to decrypt data using AES-256
def aes_decrypt(data, key, iv, cipher):
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    return unpadder.update(decrypted_data) + unpadder.finalize()

# Function to measure encryption and decryption times
def measure_aes_performance(folder, key, iv, mode_name, mode, iteration, writer, iterations=100):
    nFile = 0
    for filename in sorted(os.listdir(folder)):
        nFile += 1
        
        print(f"Iteration: {iteration}/1000\tFile: {nFile}/7\tMode: {mode_name}")
        
        filepath = os.path.join(folder, filename)
        with open(filepath, "rb") as f:
            data = f.read()

        encryption_times = []
        decryption_times = []

        for i in range(iterations):
            # Measure encryption time using timeit
            encryption_time = timeit.timeit(
                lambda: aes_encrypt(data, key, iv, mode),
                number=1
            ) * 1e6  # Convert to microseconds

            # Measure decryption time using timeit
            encrypted_data = aes_encrypt(data, key, iv, mode)  # Encrypt once for decryption timing
            decryption_time = timeit.timeit(
                lambda: aes_decrypt(encrypted_data, key, iv, mode),
                number=1
            ) * 1e6  # Convert to microseconds

            # Verify correctness
            decrypted_data = aes_decrypt(encrypted_data, key, iv, mode)
            assert data == decrypted_data, "Decrypted data does not match original!"
            
            # Write data to csv
            writer.writerow([f"AES-256-{mode_name}", len(data), i+1, encryption_time, decryption_time])

        # Delete the file after processing
        os.remove(filepath)
     
    print("-"*30)

# Main execution
def main():
    # File sizes in bytes
    sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]

    # AES-256 key and IV
    key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)   # 128-bit IV (block size for AES)


    # AES modes to test
    modes = {
        "CBC": Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()),
        "CFB": Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend()),
        "OFB": Cipher(algorithms.AES(key), modes.OFB(iv), backend=default_backend()),
        "CTR": Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    }

    # Perform 1000 iterations
    number_file_generations = 1000
    
    with open(os.path.join("Stats", "AES_performance.csv"), mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Algorithm-Mode", "File Size", "Iteration", "Encryption Time (µs)", "Decryption Time (µs)"])
        
        for mode_name, mode in modes.items():
            for iteration in range(number_file_generations):
                folder_name = f"random_files"
                generate_random_files(sizes, folder=folder_name)
                measure_aes_performance(folder_name, key, iv, mode_name, mode, iteration+1, writer)
            
if __name__ == "__main__":
    main()