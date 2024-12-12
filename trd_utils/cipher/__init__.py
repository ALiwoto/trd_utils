
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from base64 import b64encode, b64decode
from os import urandom


class AESCipher:
    def __init__(self, key: str, fav_letter: str):
        if len(key) > 32:
            raise ValueError("Key length must be 32 bytes or less")
        elif len(key) < 32:
            key = key.ljust(len(key) + (32 - len(key) % 32), fav_letter)

        key = key.encode('utf-8')
        if len(key) != 32:
            raise ValueError("Key length must be 32 bytes")
        
        self.key = key
        self.backend = default_backend()

    def encrypt(self, plaintext):
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        iv = urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return b64encode(iv + ciphertext).decode('utf-8')

    def decrypt(self, b64_encrypted_data):
        encrypted_data = b64decode(b64_encrypted_data)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        unpadder = padding.PKCS7(128).unpadder()
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext
