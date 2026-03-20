import boto3
import bcrypt
import os
from typing import Optional


class UserRepositoryDynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localstack:4566'),
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )
        self.table = self.dynamodb.Table(os.getenv('USERS_TABLE_NAME', 'users'))

    def exists(self, user_id: str) -> bool:
        """Retorna True si el user_id ya está registrado."""
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            return 'Item' in response
        except Exception:
            return False

    def create_user(self, user_id: str, password: str, role: str = 'user') -> dict:
        """Crea un nuevo usuario con la contraseña hasheada. Retorna el dict del usuario."""
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        item = {'user_id': user_id, 'password_hash': pw_hash, 'role': role}
        self.table.put_item(Item=item)
        return {'user_id': user_id, 'role': role}

    def authenticate(self, user_id: str, password: str) -> Optional[dict]:
        """
        Verifica credenciales contra la tabla DynamoDB de usuarios.
        Retorna el dict del usuario si las credenciales son válidas, None si no.
        """
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            item = response.get('Item')
            if not item:
                return None
            pw_hash = item.get('password_hash', '')
            if bcrypt.checkpw(password.encode('utf-8'), pw_hash.encode('utf-8')):
                return {'user_id': item['user_id'], 'role': item.get('role', 'user')}
            return None
        except Exception as e:
            print(f"[UserRepository] Error de autenticación: {e}")
            return None
