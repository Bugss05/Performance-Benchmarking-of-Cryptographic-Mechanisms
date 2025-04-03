import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import csv
import statistics
import matplotlib.pyplot as plt


# Function to generate random files of specified sizes
def generate_random_files(sizes, folder="random_files"):
    os.makedirs(folder, exist_ok=True)
    for size in sizes:
        filename = os.path.join(folder, f"file_{size}.txt")
        with open(filename, "wb") as f:
            f.write(os.urandom(size))

# Function to encrypt data using AES-256
def aes_encrypt(data, key, iv):
    """ Explicação da class Cipher():
    
        - Algorithms: declaração do algoritmo a usar. Neste caso, AES
        
        - Modes: define o modo de funcionamento do AES, ou seja, a sua variação. Usamos
        neste caso o CBC, que combina cada bloco com o seu anterior por XOR, exceto o
        primeiro, que é encriptado segundo uma chave (iv) com o tamanho do bloco (16 bits)
        
        - Backend: define o script que realiza as operações criptográficas necessárias.
        Escolhemos o default_backend(), baseado em OpenSSL, por ser dos mais usados e testados.
    """
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return encryptor.update(padded_data) + encryptor.finalize()

# Function to decrypt data using AES-256
def aes_decrypt(data, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    return unpadder.update(decrypted_data) + unpadder.finalize()

# Function to measure encryption and decryption times
def measure_aes_performance(folder, key, iv, iteration, iterations=1000):
    results = {}
    nFile = 0
    for filename in sorted(os.listdir(folder)):
        nFile += 1
        print(f"Iteration: {iteration}/1000\tFile: {nFile}/7")
        filepath = os.path.join(folder, filename)
        with open(filepath, "rb") as f:
            data = f.read()

        encryption_times = []
        decryption_times = []

        for _ in range(iterations):
            # Measure encryption time
            start_time = time.time()
            encrypted_data = aes_encrypt(data, key, iv)
            encryption_times.append(time.time() - start_time)

            # Measure decryption time
            start_time = time.time()
            decrypted_data = aes_decrypt(encrypted_data, key, iv)
            decryption_times.append(time.time() - start_time)

            # Verify correctness
            assert data == decrypted_data, "Decrypted data does not match original!"

        # Calculate average times
        avg_encryption_time = sum(encryption_times) / iterations
        avg_decryption_time = sum(decryption_times) / iterations

        # Extract file size from filename
        file_size = int(filename.split('_')[1].split('.')[0])
        results[file_size] = (avg_encryption_time, avg_decryption_time)

    
        # Delete the file after processing
        os.remove(filepath)
     
    print("-"*30)
    return results

# Save results to CSV
def save_results_to_csv(results, output_file="performance_results.csv"):
    with open(output_file, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File Size (bytes)", "Average Encryption Time (s)", "Average Decryption Time (s)"])
        for file_size, times in sorted(results.items()):
            writer.writerow([file_size, times[0], times[1]])

# Main execution
def main():
    
    # File sizes in bytes
    sizes = [8, 64, 512, 4096, 32768, 262144, 2097152]

    # AES-256 key and IV
    key = os.urandom(32)  # 256-bit key
    iv = os.urandom(16)   # 128-bit IV (block size for AES)

    # Perform 1000 iterations
    all_results = {}

    for iteration in range(1000):
        folder_name = f"random_files"
        generate_random_files(sizes, folder=folder_name)
        results = measure_aes_performance(folder_name, key, iv, iteration)
        
        # Aggregate results
        for file_size, times in results.items():
            if file_size not in all_results:
                all_results[file_size] = {"encryption_times": [], "decryption_times": []}
            all_results[file_size]["encryption_times"].append(times[0])
            all_results[file_size]["decryption_times"].append(times[1])

    # Calculate averages and medians excluding the first 5 iterations
    processed_results = {}
    for file_size, times in all_results.items():
        encryption_times = times["encryption_times"][5:]  # Exclude first 5 iterations
        decryption_times = times["decryption_times"][5:]  # Exclude first 5 iterations

        # Convert times to microseconds
        encryption_times_micro = [t * 1_000_000 for t in encryption_times]
        decryption_times_micro = [t * 1_000_000 for t in decryption_times]

        avg_encryption_time = sum(encryption_times_micro) / len(encryption_times_micro)
        avg_decryption_time = sum(decryption_times_micro) / len(decryption_times_micro)

        median_encryption_time = statistics.median(encryption_times_micro)
        median_decryption_time = statistics.median(decryption_times_micro)

        processed_results[file_size] = (avg_encryption_time, avg_decryption_time, median_encryption_time, median_decryption_time)

    # Save to CSV
    with open("performance_results.csv", mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File Size (bytes)", "Average Encryption Time (µs)", "Average Decryption Time (µs)", 
                         "Median Encryption Time (µs)", "Median Decryption Time (µs)"])
        for file_size, times in sorted(processed_results.items()):
            writer.writerow([file_size, times[0], times[1], times[2], times[3]])
            
if __name__ == "__main__":
    main()

    
