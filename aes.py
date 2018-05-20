import md5, base64, os, random, struct
import Crypto.Random
from Crypto.Cipher import AES

#key = '0123456789abcdef'
key = Crypto.Random.OSRNG.posix.new().read(AES.block_size)
print key
IV = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
mode = AES.MODE_CBC
encryptor = AES.new(key, mode, IV)

text = 'loki dies'
if len(text) % 16 != 0:
	text += 'z' * (16 - len(text) % 16)
ciphertext = encryptor.encrypt(text)
print ciphertext

decryptor = AES.new(key, mode, IV=IV)
plain = decryptor.decrypt(ciphertext)
plain = plain.replace("z", '')
print plain

def generate_key(self, uid):
    m = md5.new()
    m.update(os.urandom(random.randint(15,25)))
    m.update(uid)
    return base64.standard_b64encode(m.digest())
