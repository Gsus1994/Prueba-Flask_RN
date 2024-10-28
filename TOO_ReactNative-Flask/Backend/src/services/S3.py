#Backend/src/services/S3.py

import os
import boto3
from flask import current_app

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET')

    def upload_file(self, file, filename):
        try:
            if file.content_length > 5 * 1024 * 1024:
                raise ValueError("El archivo excede el tamaño máximo permitido de 5 MB")

            self.s3.upload_fileobj(
                file,
                self.bucket_name,
                filename,
                ExtraArgs={"ContentType": file.content_type}
            )
            file_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{filename}"
            return file_url
        except Exception as e:
            current_app.logger.error(f"Error al subir el archivo a S3: {str(e)}")
            raise e

    def generate_presigned_url(self, filename, expiration=7200):
        try:
            url = self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': filename
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            current_app.logger.error(f"Error al generar la URL firmada: {str(e)}")
            raise e
        
    def delete_file(self, filename):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=filename)
        except Exception as e:
            current_app.logger.error(f"Error al eliminar el archivo {filename} de S3: {str(e)}")