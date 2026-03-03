# Task API - Una API REST con FastAPI

API REST de gestión de tareas construida con FastAPI y Pydantic v2.

---

## Decisiones de arquitectura

### Soft delete
Las tareas nunca se eliminan directamente del almacenamiento. Al borrar una tarea se marca `is_deleted: true`, lo que la oculta de todos los listados activos. Esto permite restaurarlas y mantener un historial. El hard delete existe como operación explícita y destructiva.

### Separación de modelos
Se usan tres modelos Pydantic distintos con responsabilidades claras:
- `CreateTask` — solo acepta los campos que el cliente puede enviar
- `UpdateTask` — todos los campos opcionales para actualizaciones parciales
- `GetTask` — modelo de respuesta, incluye los campos generados por el servidor (`id`, `is_deleted`, `is_completed`)

El servidor controla `id`, `is_completed` e `is_deleted` en todo momento — el cliente nunca puede manipularlos directamente.

### Excepciones centralizadas
Todos los errores HTTP están definidos en `exceptions/tasks_exceptions.py` como funciones reutilizables. Esto evita repetir `raise HTTPException(...)` en cada endpoint y centraliza los mensajes de error.

### UUIDs como identificadores
Se usa `uuid4` en lugar de IDs secuenciales para evitar colisiones al crear tareas y para no exponer el volumen de datos de la API.

### Paginación flexible
Los endpoints de listado soportan dos modos de paginación: por `page` (número de página) o por `skip`/`limit` (offset manual). Si se proporciona `page`, sobreescribe `skip` automáticamente.

---

## Puntos fuertes

- **Validación automática** — Pydantic valida longitudes, tipos y valores por defecto antes de que el código se ejecute
- **Documentación automática** — Swagger UI generada automáticamente en `/docs` con summaries, docstrings y descripciones de campos
- **Errores consistentes** — todos los endpoints devuelven el mismo formato de respuesta via `ApiResponse[T]`
- **Imports explícitos** — sin `import *`, cada módulo importa solo lo que usa

---

## Estructura

```
task-api/
├── data/
│   ├── data_handler.py     # Lectura y escritura del JSON
│   └── tasks.json          # Almacenamiento
├── exceptions/
│   └── tasks_exceptions.py # Excepciones HTTP centralizadas
├── routers/
│   └── tasks.py            # Endpoints de tareas
├── schemas/
│   ├── models.py           # Modelos Pydantic
│   └── responses.py        # Wrapper genérico de respuesta
├── main.py
└── requirements.txt
```

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/tasks` | Listar tareas activas |
| `GET` | `/tasks/completed` | Listar tareas completadas |
| `GET` | `/tasks/deleted` | Listar tareas eliminadas |
| `GET` | `/tasks/{id}` | Obtener tarea por ID |
| `POST` | `/tasks` | Crear tarea |
| `PATCH` | `/tasks/{id}` | Actualizar título o descripción |
| `PATCH` | `/tasks/{id}/completed` | Marcar como completada |
| `PATCH` | `/tasks/{id}/uncompleted` | Marcar como no completada |
| `PATCH` | `/tasks/{id}/restore` | Restaurar tarea eliminada |
| `DELETE` | `/tasks/{id}` | Soft delete |
| `DELETE` | `/tasks/{id}/hard` | Hard delete (permanente) |

---

## Stack

- **Python 3.12**
- **FastAPI**
- **Pydantic v2**