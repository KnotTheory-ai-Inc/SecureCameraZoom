from stencil_lib import CipherConfig


class AESConfig(CipherConfig):
    algo = "aes"
    def __init__(self, key: bytes, mode: int = None, **mode_params):
        # mode: AES.MODE_ECB (default, no params), AES.MODE_CBC (iv=),
        #        AES.MODE_CFB (iv=), AES.MODE_OFB (iv=), AES.MODE_CTR (nonce= or counter=),
        #        AES.MODE_GCM (nonce=), AES.MODE_EAX (nonce=), AES.MODE_CCM (nonce=),
        #        AES.MODE_SIV (nonce=), AES.MODE_OCB (nonce=), AES.MODE_OPENPGP (iv=)

        from Crypto.Cipher import AES
        self.parameters = {
            "key": key,
            "mode": mode if mode is not None else AES.MODE_ECB,
            "mode_params": mode_params,
        }
    def encrypt(self, plaintext: bytes, *args, **kwargs) -> bytes:
        from Crypto.Cipher import AES
        cipher = AES.new(self.parameters["key"], self.parameters["mode"], **self.parameters["mode_params"])
        return cipher.encrypt(plaintext)
    def decrypt(self, ciphertext: bytes, *args, **kwargs) -> bytes:
        from Crypto.Cipher import AES
        cipher = AES.new(self.parameters["key"], self.parameters["mode"], **self.parameters["mode_params"])
        return cipher.decrypt(ciphertext)


class CaesarConfig(CipherConfig):
    algo = "caesar"
    def __init__(self, shift: int):
        self.parameters = {"shift": shift}
    def encrypt(self, plaintext: bytes, *args, **kwargs) -> bytes:
        shift = self.parameters["shift"]
        return bytes((b + shift) % 256 for b in plaintext)
    def decrypt(self, ciphertext: bytes, *args, **kwargs) -> bytes:
        shift = self.parameters["shift"]
        return bytes((b - shift) % 256 for b in ciphertext)


class VigenereConfig(CipherConfig):
    algo = "vigenere"
    def __init__(self, keyword: bytes):
        self.parameters = {"keyword": keyword}
    def encrypt(self, plaintext: bytes, *args, **kwargs) -> bytes:
        key = self.parameters["keyword"]
        key_len = len(key)
        return bytes((b + key[i % key_len]) % 256 for i, b in enumerate(plaintext))
    def decrypt(self, ciphertext: bytes, *args, **kwargs) -> bytes:
        key = self.parameters["keyword"]
        key_len = len(key)
        return bytes((b - key[i % key_len]) % 256 for i, b in enumerate(ciphertext))
