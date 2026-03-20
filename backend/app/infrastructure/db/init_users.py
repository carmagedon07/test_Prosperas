#!/usr/bin/env python3
"""
Script to initialize users table in DynamoDB with initial users
"""
import boto3
import bcrypt
import os
import time
from datetime import datetime


def wait_for_localstack():
    """Wait for LocalStack to be ready"""
    dynamodb = boto3.client(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localstack:4566'),
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    for i in range(30):
        try:
            dynamodb.list_tables()
            print("LocalStack is ready!")
            return True
        except Exception as e:
            print(f"Waiting for LocalStack... ({i+1}/30)")
            time.sleep(2)
    
    return False


def create_users_table():
    """Create users table in DynamoDB"""
    dynamodb = boto3.client(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localstack:4566'),
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    table_name = 'users'
    
    # Check if table exists
    try:
        existing_tables = dynamodb.list_tables()['TableNames']
        if table_name in existing_tables:
            print(f"Table '{table_name}' already exists")
            return
    except Exception as e:
        print(f"Error checking tables: {e}")
    
    # Create table
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"Table '{table_name}' created successfully")
        time.sleep(2)  # Wait for table to be ready
    except Exception as e:
        print(f"Error creating table: {e}")
        raise


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def populate_users():
    """Populate users table with initial users"""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMODB_ENDPOINT', 'http://localstack:4566'),
        region_name='us-east-1',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    table = dynamodb.Table('users')
    
    # Initial users
    users = [
        {
            'user_id': 'superadmin',
            'password': 'superpassword',
            'role': 'admin'
        },
        {
            'user_id': 'user1',
            'password': 'password123',
            'role': 'user'
        },
        {
            'user_id': 'user2',
            'password': 'password456',
            'role': 'user'
        }
    ]
    
    for user in users:
        try:
            # Check if user already exists
            response = table.get_item(Key={'user_id': user['user_id']})
            if 'Item' in response:
                print(f"User '{user['user_id']}' already exists, skipping...")
                continue
            
            # Create user with hashed password
            table.put_item(
                Item={
                    'user_id': user['user_id'],
                    'password_hash': hash_password(user['password']),
                    'role': user['role'],
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            print(f"Created user: {user['user_id']} (role: {user['role']}, password: {user['password']})")
        except Exception as e:
            print(f"Error creating user {user['user_id']}: {e}")


def main():
    print("=== Initializing Users Table ===")
    
    if not wait_for_localstack():
        print("ERROR: LocalStack is not ready!")
        exit(1)
    
    create_users_table()
    populate_users()
    
    print("\n=== Users Table Initialization Complete ===")
    print("\nAvailable users:")
    print("  - superadmin / superpassword (admin)")
    print("  - user1 / password123 (user)")
    print("  - user2 / password456 (user)")


if __name__ == '__main__':
    main()
