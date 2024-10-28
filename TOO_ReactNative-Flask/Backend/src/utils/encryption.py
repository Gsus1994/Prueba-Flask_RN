#Backend/src/utils/encryption.py

import base64
from src.config import Config
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Función para corregir la codificación del texto
def correct_encoding(text):
    try:
        # Intentar decodificar como ISO-8859-1 y recodificar como UTF-8
        text = text.encode('iso-8859-1').decode('utf-8')
    except UnicodeDecodeError:
        # Si falla, el texto ya está en UTF-8, así que no se hace nada
        pass
    return text

def decrypt_aes(data):
    try:
        cipher = AES.new(Config.AES_KEY, AES.MODE_ECB)
        decrypted = cipher.decrypt(base64.b64decode(data))
        # Unpad y decodificación a UTF-8
        decrypted_text = unpad(decrypted, AES.block_size).decode('utf-8')
        return correct_encoding(decrypted_text)
    except (UnicodeDecodeError, ValueError) as e:
        # Manejo de errores si la decodificación falla
        return f"Error al desencriptar: {str(e)}"

def encrypt_aes(data):
    try:
        cipher = AES.new(Config.AES_KEY, AES.MODE_ECB)
        # Pad y codificación a UTF-8
        encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        # Manejo de errores si la encriptación falla
        return f"Error al encriptar: {str(e)}"