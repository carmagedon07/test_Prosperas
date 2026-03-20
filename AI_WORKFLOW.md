# AI_WORKFLOW.md — Evidencia de uso de IA en este proyecto

## Herramienta utilizada

**GitHub Copilot** (Claude Sonnet 4.6) integrado en VS Code, en modo de agente (Copilot Chat con acceso a herramientas de edición de archivos, terminal y búsqueda en el codebase).

---

## Qué se usó con IA y qué no

| Componente | Generado con IA | Intervención manual |
|---|---|---|
| Estructura base FastAPI (dominio, use cases, repos) | Parcial (esqueleto inicial) | Refactorización de capas, ajuste de interfaces |
| Docker Compose + LocalStack | Sí | Corrección del orden de dependencias `depends_on` |
| Terraform IaC completo (`infra/`) | Sí | Verificación de ARNs, corrección de `lifecycle` en ECS |
| GitHub Actions workflow | Sí | Ajuste de caché de `index.html` (no-cache) |
| Fix del bug `t.join()` en worker | Sí | Revisión del flujo de eliminación de mensajes SQS |
| TECHNICAL_DOCS.md | Sí | Revisión de tabla de trade-offs |
| SKILL.md | Sí | Revisión de sección de errores comunes |
| Tests unitarios | No — escritos a mano | — |

---

## Cómo se usó: ejemplo de prompts representativos

### 1. Análisis de brechas / gap analysis

**Prompt:**
> "Revisá todo el proyecto y decime qué riesgos de descalificación hay según los requisitos del enunciado"

**Output del modelo:** Identificó 5 riesgos: falta de CI/CD, worker síncrono (`t.join()`), `sleep(60)` en lugar de `random.uniform(5,30)`, `endpoint_url` hardcodeado a localstack, y ausencia de documentación.

**Corrección necesaria:** El modelo inicialmente no detectó que `endpoint_url=os.getenv('X', 'http://localstack:4566')` fallaba en producción; hubo que señalarlo explícitamente.

---

### 2. Infraestructura Terraform

**Prompt (después de preguntar detalles de configuración):**
> "Creá el archivo `infra/ecs.tf` completo con: cluster ECS, task definitions para backend y worker (JWT desde SSM, no env var), 2 servicios ECS, sin NAT gateway"

**Output del modelo:** Generó el archivo correcto. Se tuvo que corregir que `assign_public_ip = true` estaba dentro de `network_configuration` (posición incorrecta en el bloque).

---

### 3. Fix del worker síncrono

**Prompt:**
> "El worker tiene `t.start(); t.join()` que lo hace síncrono. Fixealo para que sea realmente concurrente y que el mensaje se elimine de SQS dentro del thread cuando termine"

**Output del modelo:** Propuso correctamente mover `delete_message` al `finally` block dentro de `process_job` y eliminar `t.join()`.

---

### 4. SKILL.md

**Prompt:**
> "Generá el SKILL.md completo para este proyecto. Debe servir para que una IA pueda operar sobre el código sin leer los archivos. Incluí: descripción, mapa del repo, patrones, comandos, errores comunes, cómo extender"

**Output del modelo:** Generó el 90% del contenido. Se ajustó la sección de "errores comunes" para incluir el error de `DYNAMODB_ENDPOINT` vacío en producción, que el modelo no incluyó inicialmente.

---

## Limitaciones encontradas

1. **Contexto de ventana**: En la misma sesión larga, el modelo a veces perdía contexto de decisiones anteriores (p.ej. olvidó que se había decidido usar Default VPC en lugar de crear una nueva). Se resolvía recordándoselo explícitamente.

2. **Hardcoded defaults**: El modelo generó varias veces `os.getenv("X", "http://localstack:4566")`, asumiendo que el default era inofensivo. En producción esto rompe la conectividad a AWS real. Hubo que pedirle explícitamente que usara `os.getenv("X") or None`.

3. **Terraform lifecycle**: En el task definition de ECS, el modelo no añadió `lifecycle { ignore_changes = [task_definition] }` la primera vez, lo que haría que Terraform sobreescriba la versión del task definition en cada `apply`.

4. **Caché de CloudFront para SPA**: El modelo no distinguió inicialmente entre `index.html` (no cacheable) y los demás assets (cacheables indefinidamente). Hubo que pedir el ajuste del `Cache-Control` específico para `index.html`.

---

## Evaluación del proceso

El uso de IA aceleró significativamente la creación de boilerplate (Terraform, GitHub Actions, docker-compose) y redujo errores de sintaxis. Sin embargo, **la revisión humana fue esencial** para detectar bugs sutiles de comportamiento en producción (endpoints hardcodeados, worker síncrono, caché HTTP). El valor del agente no fue "escribe código correcto a la primera" sino "genera una base sólida rápidamente que se puede revisar y corregir".
