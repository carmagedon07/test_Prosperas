from typing import Optional
import boto3
import os
import bcrypt
from datetime import datetime


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

    def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by user_id"""
        response = self.table.get_item(Key={'user_id': user_id})
        return response.get('Item')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_user(self, user_id: str, password: str, role: str = 'user') -> dict:
        """Create a new user with hashed password"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = {
            'user_id': user_id,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.utcnow().isoformat()
        }
        self.table.put_item(Item=user)
        return user

    def authenticate(self, user_id: str, password: str) -> Optional[dict]:
        """Authenticate user and return user info (without password)"""
        user = self.get_user(user_id)
        if not user:
            return None
        
        if not self.verify_password(password, user['password_hash']):
            return None
        
        # Return user without password_hash
        return {
            'user_id': user['user_id'],
            'role': user['role'],
            'created_at': user.get('created_at')
        }
