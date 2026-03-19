"# test_Prosperas" 


Flujo propuesto

[React]
   ↓
[FastAPI - ECS]
   ↓
[PostgreSQL - RDS]  ← guarda job (PENDIENTE)
   ↓
[SQS Queue] ← mensaje
   ↓
[Worker - ECS]
   ↓
procesa (sleep)
   ↓
[PostgreSQL - RDS] ← actualiza estado
   ↓
[React (polling)]
