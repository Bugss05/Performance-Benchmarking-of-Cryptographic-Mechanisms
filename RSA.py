import os
import random
import string
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import timeit
from statistics import median

def create_random_files(base_directory, files_number=1000):
    # Ensure the base directory exists
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    # Create directories for size categories
    size_categories = {
        "2_bytes": os.path.join(base_directory, "2_bytes"),
        "4_bytes": os.path.join(base_directory, "4_bytes"),
        "8_bytes": os.path.join(base_directory, "8_bytes"),
        "16_bytes": os.path.join(base_directory, "16_bytes"),
        "32_bytes": os.path.join(base_directory, "32_bytes"),
        "64_bytes": os.path.join(base_directory, "64_bytes"),
        "128_bytes": os.path.join(base_directory, "128_bytes"),
    }

    for category in size_categories.values():
        if not os.path.exists(category):
            os.makedirs(category)  # Create the directory if it doesn't exist

    sizes = [2, 4, 8, 16, 32, 64, 128]  # Define the sizes in bytes

    # Generate 100 random files
    for file_size in sizes:
        for i in range(files_number):

            file_content = ''.join(random.choices(string.ascii_letters + string.digits, k=file_size))
            file_name = f"file_{i + 1}.txt"

            # Determine the correct directory based on file size
            match file_size:
                case 2:
                    target_directory = size_categories["2_bytes"]
                case 4:
                    target_directory = size_categories["4_bytes"]
                case 8:
                    target_directory = size_categories["8_bytes"]
                case 16:
                    target_directory = size_categories["16_bytes"]
                case 32:
                    target_directory = size_categories["32_bytes"]
                case 64:
                    target_directory = size_categories["64_bytes"]
                case 128:
                    target_directory = size_categories["128_bytes"]
                case _:
                    target_directory = size_categories["others"]

            # Write the file to the appropriate directory
            with open(os.path.join(target_directory, file_name), "w") as file:
                file.write(file_content)

        print(str(files_number) + " random files with " + str(file_size) + " bytes created in directory " + target_directory)
    
def create_csv_file():
    file = os.path.join(os.getcwd(), "RSA_Stats.csv")
    return file

def RSA_encrypt(public_key, data):
    # Start timer
    start_time = timeit.default_timer()
    
    # Do encryption operations
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Stop timer and get final time
    encryption_time = (timeit.default_timer() - start_time) * 1_000_000  # Convert to microseconds
    return ciphertext, encryption_time

def RSA_decrypt(private_key, ciphertext, original_data):
    # Start timer
    start_time = timeit.default_timer()
    
    # Do decryption operations
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Stop timer and get final time
    decryption_time = (timeit.default_timer() - start_time) * 1_000_000  # Convert to microseconds
    # Verify if decryption was successful
    assert plaintext == original_data, "Decryption failed!"
    return decryption_time

def generate_RSA_keys():
    """ Explicação dos argumentos em rsa.generate_private_key():
        - public_exponent: O valor do expoente público, tipicamente definido como 65537, devido
        ao equilíbrio entre segurança e desempenho.
        
        - key_size: O tamanho da chave RSA em bits. Neste caso, 2048.
        
        - backend: define o script que realiza as operações criptográficas necessárias.
        Escolhemos o default_backend(), baseado em OpenSSL, por ser dos mais usados e testados.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    return private_key, public_key

def main(directory, iter_per_file=100):
    
    create_random_files(directory) # if wanted, add the number of files to be different from 1000
    results_file = create_csv_file()

    # Generate RSA keys
    private_key, public_key = generate_RSA_keys()
    
    # Iterate through each size category and encrypt/decrypt files
    for size in [2, 4, 8, 16, 32, 64, 128]:
        directory = os.path.join(directory, f"{size}_bytes")

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as file:
                data = file.read()

            for i in range(iter_per_file):
                encrypted_data, encryption_time = RSA_encrypt(public_key, data)
                decryption_time = RSA_decrypt(private_key, encrypted_data, data)

                with open(results_file, "a") as f:
                    f.write(f"RSA, {size}, {i+1}, {encryption_time}, {decryption_time}\n")

            # Print disabled for better performance and speed
            # print(f"File: {filename}, Size: {size}")

        directory = os.path.dirname(directory)  # Update the directory to its parent

    os.remove(directory)  # Remove the directory after processing


directory = os.path.join(os.getcwd(), "RSA_files")

if __name__ == "__main__":

    # Run the RSA encryption and decryption process 
    main(directory)
                    