# ToDo challenge

## Tabla de Contenidos
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Tests](#tests)
- [Documentación de Endpoints](#documentación-de-endpoints)

## Requisitos Previos

Antes de comenzar, asegúrese de tener instalado lo siguiente donde se desea correr el servicio:

- Docker

## Instalación y Configuración

Siga estos pasos para levantar la aplicación:

1. Clone el repositorio:
```bash
git clone https://github.com/CIROBRUNO90/todo-challenge.git
cd todo-challenge
```

2. Construya y levante los contenedores Docker:
```bash
docker-compose up --build
```

> **Nota**: El comando `docker-compose up --build` combina la construcción y el levantamiento de los contenedores en un solo paso. Es la opción recomendada para asegurar que siempre se están utilizando las últimas versiones de las imágenes.

3. La aplicación estará disponible en:
```
http://localhost
```

### Comandos Útiles

- Para detener la aplicación:
```bash
docker-compose down
```

- Para ver los logs:
```bash
docker-compose logs -f
```

## Tests

Para ejecutar los tests del proyecto, siga estos pasos:

1. Asegúrese de que la aplicación esté corriendo:
```bash
docker-compose up -d
```

2. Conéctese al contenedor de la aplicación:
```bash
docker-compose exec app bash
```

3. Ejecute los tests con Pytest:
```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con más detalle
pytest -v

# Ejecutar tests con reporte de cobertura
pytest --cov=.
```

Los resultados de los tests se mostrarán en la terminal, indicando:
- Número total de tests ejecutados
- Tests exitosos y fallidos
- Tiempo de ejecución
- Resumen de la cobertura (cuando se usa el flag --cov)

## Documentación de Endpoints
- Todos los endpoints retornan las respuestas en formato JSON.
- Para los endpoints que requieren autenticación, se debe incluir el token JWT en el header de la siguiente manera:
  ```
  Authorization: Bearer <access_token>
  ```
- Los tokens JWT (access y refresh) se obtienen al registrarse o iniciar sesión.
- El `access_token` se usa para autenticación en endpoints protegidos.
- El `refresh_token` se usa para obtener un nuevo `access_token` cuando este expira.


### Endpoints de Usuarios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/register/` | Registra un nuevo usuario |
| POST | `/api/login/` | Inicia sesión para un usuario |
| POST | `/api/logout/` | Cierra sesión para un usuario |


#### Registro de Usuario
```http
POST /api/register/
HEADERS
Content-Type: application/json
BODY
{
  "username": "string",
  "email": "string",
  "password": "string",
  "phone_number": "string" [opcional]
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "phone_number": "string"
  },
  "refresh": "string",
  "access": "string"
}
```

#### Inicio de Sesión
```http
POST /api/login/
HEADERS
Content-Type: application/json
BODY
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "phone_number": "string"
  },
  "refresh": "string",
  "access": "string"
}
```


#### Cierre de Sesión
```http
POST /api/logout/
HEADERS
Content-Type: application/json
Authorization: Bearer <access_token>
BODY
{
  "refresh": "string"
}
```

**Response (200 OK):**
```json
{
  "detail": "Successfully logged out"
}
```



### Endpoints Tasks
#### Consideraciones
- Se requiere autenticación para todos los endpoints
- Los usuarios solo pueden ver y modificar sus propias tareas
- Las tareas se filtran automáticamente por el usuario actual

#### Base URL
```
/api/tasks/
```

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/tasks/` | Lista todas las tareas del usuario |
| POST | `/api/tasks/` | Crea una nueva tarea |
| PUT | `/api/tasks/{id}/` | Actualiza una tarea completa |
| PATCH | `/api/tasks/{id}/` | Actualiza parcialmente una tarea |
| DELETE | `/api/tasks/{id}/` | Elimina una tarea |
| POST | `/api/tasks/{id}/complete/` | Marca una tarea como completada |
| POST | `/api/tasks/{id}/reopen/` | Reabre una tarea completada |


#### Listado de tareas
Ejemplo:
```http
GET /api/tasks/
HEADERS
Authorization: Bearer <access_token>
```
La API permite filtrar tareas usando los siguientes query parameters:
- `status`: Filtra por estado de la tarea
- `priority`: Filtra por prioridad
- `title`: Busca por título (búsqueda parcial)
- `description`: Busca por descripción (búsqueda parcial)
- `id`: ID de la tarea a buscar

#### Crear una Nueva Tarea
```http
POST /api/tasks/
HEADERS
Content-Type: application/json
Authorization: Bearer <access_token>
BODY
{
    "title": "Nueva Tarea",
    "description": "Descripción de la tarea",
    "priority": "high",
    "due_date": "2024-12-31T23:59:59Z"
}
```

#### Completar Tarea
```http
POST /api/tasks/{id}/complete/
HEADERS
Authorization: Bearer <access_token>
```
- Marca la tarea como completada
- Establece la fecha de completado (completed_at)
- Cambia el status a 'completed'

#### Reabrir Tarea
```http
POST /api/tasks/{id}/reopen/
HEADERS
Authorization: Bearer <access_token>
```
- Reabre una tarea completada
- Elimina la fecha de completado
- Cambia el status a 'pending'



#### Actualizar una Tarea
```http
PUT /api/tasks/{id}/
HEADERS
Content-Type: application/json
Authorization: Bearer <access_token>
BODY
{
    "title": "Actualizar Tarea",
    "description": "Descripción de la tarea",
    "priority": "medium",
    "due_date": "2024-12-31T23:59:59Z"
}
```

#### Actualiza parcialmente una Tarea
```http
PATCH /api/tasks/{id}/
HEADERS
Content-Type: application/json
Authorization: Bearer <access_token>
BODY
{
    "priority": "low",
}
```

#### Borrar una Tarea
```http
DELETE /api/tasks/{id}/
HEADERS
Authorization: Bearer <access_token>
```