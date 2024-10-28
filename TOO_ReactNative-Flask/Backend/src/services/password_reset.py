# Backend/src/services/password_reset.py

import random
import string
import redis
import smtplib
from email.mime.text import MIMEText
from flask import current_app
from src.config import config_by_name

class PasswordResetService:
    def __init__(self):
        try:
            self.redis_client = redis.Redis.from_url(config_by_name['development'].REDIS_URL)
            self.redis_client.ping()  # Verificar conexión
            current_app.logger.info("Conexión a Redis exitosa.")
        except Exception as e:
            current_app.logger.error(f"Error conectando a Redis: {str(e)}")
            raise e

    def generate_code(self, length=6):
        code = ''.join(random.choices(string.digits, k=length))
        current_app.logger.debug(f"Código generado: {code}")
        return code

    def store_code(self, email, code):
        try:
            expiration = config_by_name['development'].PASSWORD_RESET_CODE_EXPIRATION
            self.redis_client.setex(f"password_reset:{email}", expiration, code)
            current_app.logger.info(f"Código de restablecimiento almacenado para {email}.")
        except Exception as e:
            current_app.logger.error(f"Error almacenando código en Redis para {email}: {str(e)}")
            raise e

    def send_reset_email(self, email, code):
        try:
            # Crear el mensaje MIME
            msg = MIMEText(f"Tu código de restablecimiento de contraseña es: {code}")
            msg['Subject'] = 'Restablecimiento de Contraseña'
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = email

            # Conectar al servidor SMTP
            server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
            server.ehlo()
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
                server.ehlo()

            # Iniciar sesión en el servidor SMTP
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])

            # Enviar el correo
            server.send_message(msg)
            server.quit()

            current_app.logger.info(f"Correo de restablecimiento enviado a {email}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error al enviar correo a {email}: {str(e)}")
            return False

    def verify_code(self, email, code):
        try:
            stored_code = self.redis_client.get(f"password_reset:{email}")
            current_app.logger.debug(f"Código almacenado para {email}: {stored_code}")
            if stored_code and stored_code.decode('utf-8') == code:
                self.redis_client.delete(f"password_reset:{email}")
                current_app.logger.info(f"Código de restablecimiento verificado para {email}.")
                return True
            current_app.logger.warning(f"Código de restablecimiento inválido o expirado para {email}.")
            return False
        except Exception as e:
            current_app.logger.error(f"Error verificando código en Redis para {email}: {str(e)}")
            return False