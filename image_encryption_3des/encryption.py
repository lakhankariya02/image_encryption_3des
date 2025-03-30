import os
import numpy as np
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from PIL import Image

# Generate a secure 24-byte key
def generate_key():
    return DES3.adjust_key_parity(os.urandom(24))

# Encrypt an image using 3DES
def encrypt_image(input_path, output_path, key):
    img = Image.open(input_path).convert("RGB")
    img_data = np.array(img)
    img_bytes = img_data.tobytes()

    # Encrypt with 3DES
    cipher = DES3.new(key, DES3.MODE_ECB)
    encrypted_data = cipher.encrypt(pad(img_bytes, DES3.block_size))

    # Save encrypted data as a binary file
    with open(output_path, "wb") as f:
        f.write(encrypted_data)

    return key, img.size  # Return key & original image size

# Decrypt an image using 3DES
def decrypt_image(input_path, output_path, key, image_size):
    with open(input_path, "rb") as f:
        encrypted_data = f.read()

    # Decrypt with 3DES
    cipher = DES3.new(key, DES3.MODE_ECB)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), DES3.block_size)

    # Convert back to image
    decrypted_array = np.frombuffer(decrypted_data, dtype=np.uint8)[:image_size[0] * image_size[1] * 3]
    decrypted_image = Image.frombytes("RGB", image_size, decrypted_array)

    decrypted_image.save(output_path)
