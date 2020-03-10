"""aes cipher"""
__author__ = 'clzou'
import base64
from Crypto.Cipher import AES

BS = 16
AES_DATA_PAD = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
AES_DATA_UNPAD = lambda s: s[0:-ord(s[-1])]


class AESCipher(object):
    """AES Cipher"""
    def __init__(self, key, init_value):
        """
        Requires hex encoded param as a key
        """
        self.key = key
        self.init_value = init_value
        self.cipher = AES.new(self.key, AES.MODE_CBC, self.init_value)

    def encrypt(self, raw):
        """
        Returns hex encoded encrypted value!
        """
        raw = AES_DATA_PAD(raw)
        message = self.cipher.encrypt(raw)
        return base64.b64encode(message)
        # return ( self.iv + cipher.encrypt( raw ) ).encode("hex")

    def decrypt(self, enc):
        """
        Requires hex encoded param to decrypt
        """
        data = base64.b64decode(enc)
        return AES_DATA_UNPAD(self.cipher.decrypt(data))
        # return cipher.decrypt(enc)


AES_KEY = "6A0989D1221D3625AAFA86227DFD2350"
AES_IV = "FCE68D90B6D023741C6E9BB12CA08A73"


def get_aes_cipher():
    """ get aes cipher"""
    return AESCipher(AES_KEY.decode("hex"), AES_IV.decode("hex"))
