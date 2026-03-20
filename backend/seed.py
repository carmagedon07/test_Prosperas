"""
seed.py — Puebla la tabla DynamoDB de usuarios con datos de prueba.
Se ejecuta una sola vez al levantar el entorno local con docker compose.

Usuarios creados:
  superadmin / ${ADMIN_PASSWORD:-admin123}   -> rol admin
  usuario1   / ${TEST_PASSWORD:-test123}     -> rol user
"""
import boto3
import bcrypt
import os
import sys

DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', 'http://localstack:4566')
AWS_REGION        = os.getenv('AWS_REGION', 'us-east-1')
AWS_KEY           = os.getenv('AWS_ACCESS_KEY_ID', 'test')
AWS_SECRET        = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
USERS_TABLE       = os.getenv('USERS_TABLE_NAME', 'users')

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
)

table = dynamodb.Table(USERS_TABLE)

SEED_USERS = [
    {
        'user_id':  os.getenv('ADMIN_USER', 'superadmin'),
        'password': os.getenv('ADMIN_PASSWORD', 'admin123'),
        'role':     'admin',
    },
    {
        'user_id':  os.getenv('TEST_USER', 'usuario1'),
        'password': os.getenv('TEST_PASSWORD', 'test123'),
        'role':     'user',
    },
]

print("[SEED] Iniciando seed de usuarios...")

for u in SEED_USERS:
    pw_hash = bcrypt.hashpw(u['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    table.put_item(Item={
        'user_id':       u['user_id'],
        'password_hash': pw_hash,
        'role':          u['role'],
    })
    print(f"[SEED] ✓ Usuario creado: {u['user_id']}  (rol: {u['role']})")

print("[SEED] Seed completado.")
sys.exit(0)
