import os
from dotenv import load_dotenv
from Crypto.Cipher import AES
import base64
import demjson

load_dotenv()


class decrypter:

    @staticmethod
    def decrypt(text):
        key = os.environ['APP_KEY'].encode('UTF-8')

        decoded_text = demjson.decode(base64.b64decode(text))
        iv = base64.b64decode(decoded_text['iv'])

        crypt_object = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)

        decoded = base64.b64decode(decoded_text['value'])
        decrypted = crypt_object.decrypt(decoded)

        decrypted_string = ''.join(c for c in decrypted.decode('utf-8', 'ignore') if c.isprintable())

        return decrypted_string
