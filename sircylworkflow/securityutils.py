from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

class SymmetricKey(object):
    def __init__(self, secret):
        secret = secret[:48]
        self.key = secret[0:32].encode()
        self.algorithm = algorithms.AES(self.key)
        self.mode = modes.CTR(secret[32:].encode())
        self.cipher = Cipher(self.algorithm, self.mode)

    def encrypt_str(self, value: str, encoding:str =  "utf-8") -> bytes:
        return self.encrypt(bytes(value, encoding))

    def decrypt_str(self, value: str, encoding:str =  "utf-8") -> bytes:
        return self.decrypt(bytes(value, encoding))

    def encrypt(self, value: bytes) -> bytes | None:
        if not value:
            return None
        encryptor = self.cipher.encryptor()
        message_encrypted = encryptor.update(value) + encryptor.finalize()
        return message_encrypted

    def decrypt(self, value: bytes) -> bytes| None:
        if not value:
            return None
        decryptor = self.cipher.decryptor()
        message_decrypted = decryptor.update(value) + decryptor.finalize()
        return message_decrypted