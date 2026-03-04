# FastTask — API REST con FastAPI

API REST de gestión de tareas con soporte de listas, construida con FastAPI y Pydantic v2.

---

## Decisiones de arquitectura

### Soft delete
Las tareas y listas nunca se eliminan directamente del almacenamiento. Al borrar una entidad se marca `is_deleted: true`, lo que la oculta de todos los listados activos. Esto permite restaurarlas y mantener un historial. El hard delete existe como operación explícita y destructiva.

### Separación de modelos
Se usan modelos Pydantic distintos con responsabilidades claras:
- `CreateTask` / `CreateList` — solo acepta los campos que el cliente puede enviar
- `UpdateTask` / `UpdateList` — todos los campos opcionales para actualizaciones parciales
- `GetTask` / `GetList` — modelo de respuesta, incluye los campos generados por el servidor

El servidor controla `id`, `is_completed` e `is_deleted` en todo momento — el cliente nunca puede manipularlos directamente.

### Fuente de verdad única
La relación tarea-lista se gestiona únicamente desde `task.list_id`. Las listas no almacenan referencias a sus tareas. El `task_count` de cada lista se calcula en tiempo de consulta cruzando ambos almacenamientos.

### Excepciones centralizadas
Todos los errores HTTP están definidos en `exceptions/exceptions.py` como métodos estáticos reutilizables organizados por tipo. Esto evita repetir `raise HTTPException(...)` en cada endpoint y centraliza los mensajes de error.

### UUIDs como identificadores
Se usa `uuid4` en lugar de IDs secuenciales para evitar colisiones y no exponer el volumen de datos de la API.

### Paginación flexible
Los endpoints de listado soportan dos modos: por `page` (número de página) o por `skip`/`limit` (offset manual). Si se proporciona `page`, sobreescribe `skip` automáticamente.

---

## Estructura

```
fastask/
├── data/
│   ├── data_handler.py     # Lectura y escritura del JSON
│   ├── tasks.json          # Almacenamiento de tareas
│   └── lists.json          # Almacenamiento de listas
├── exceptions/
│   └── exceptions.py       # Excepciones HTTP centralizadas
├── routers/
│   ├── tasks.py            # Endpoints de tareas
│   └── lists.py            # Endpoints de listas
├── schemas/
│   ├── task_models.py      # Modelos Pydantic de tareas
│   ├── list_models.py      # Modelos Pydantic de listas
│   └── responses.py        # Wrapper genérico ApiResponse[T]
├── main.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Endpoints

### Tareas `/tasks`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/tasks` | Listar tareas activas (con búsqueda y paginación) |
| `GET` | `/tasks/completed` | Listar tareas completadas |
| `GET` | `/tasks/deleted` | Listar tareas eliminadas |
| `GET` | `/tasks/{id}` | Obtener tarea por ID |
| `POST` | `/tasks` | Crear tarea |
| `PATCH` | `/tasks/{id}` | Actualizar título o descripción |
| `PATCH` | `/tasks/{id}/completed` | Marcar como completada |
| `PATCH` | `/tasks/{id}/uncompleted` | Marcar como no completada |
| `PATCH` | `/tasks/{id}/add/{list_id}` | Añadir tarea a una lista |
| `PATCH` | `/tasks/{id}/remove/{list_id}` | Quitar tarea de una lista |
| `PATCH` | `/tasks/{id}/restore` | Restaurar tarea eliminada |
| `DELETE` | `/tasks/{id}` | Soft delete |
| `DELETE` | `/tasks/{id}/hard` | Hard delete (permanente) |

### Listas `/lists`

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/lists` | Listar listas activas (con búsqueda y paginación) |
| `GET` | `/lists/deleted` | Listar listas eliminadas |
| `GET` | `/lists/{id}` | Obtener lista por ID |
| `GET` | `/lists/{id}/tasks` | Obtener tareas de una lista |
| `POST` | `/lists` | Crear lista |
| `PATCH` | `/lists/{id}` | Actualizar título o descripción |
| `PATCH` | `/lists/{id}/restore` | Restaurar lista eliminada |
| `DELETE` | `/lists/{id}` | Soft delete |
| `DELETE` | `/lists/{id}/hard` | Hard delete (permanente) |

---

## Stack

- **Python 3.12**
- **FastAPI**
- **Pydantic v2**
- **Uvicorn**
- **Docker + docker-compose**

---

## Arrancar el proyecto

### Con Docker

```bash
docker compose up
```

### Sin Docker

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

La documentación interactiva estará disponible en `http://localhost:8000/docs`.
