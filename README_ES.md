# FastTask — API REST con FastAPI

API REST de gestión de tareas con soporte de listas, construida con FastAPI y Pydantic v2.

---

## Decisiones de arquitectura

### Separación de modelos
Se usan modelos Pydantic distintos con responsabilidades claras:
- `CreateTask` / `CreateList` — solo acepta los campos que el cliente puede enviar
- `UpdateTask` / `UpdateList` — todos los campos opcionales para actualizaciones parciales
- `GetTask` / `GetList` — modelo de respuesta, incluye los campos generados por el servidor

 El servidor controla `id`, `is_completed` e `is_deleted` en todo momento — el cliente nunca puede manipularlos directamente.

### Fuente de verdad única
La relación tarea-lista se gestiona únicamente desde `task.list_id`. Las listas no almacenan referencias a sus tareas — las tareas son la fuente de verdad. El `task_count` de cada lista se calcula en tiempo de consulta cruzando ambos almacenamientos.

> Eliminar una lista no elimina sus tareas. Las tareas quedan activas y accesibles, y su gestión es responsabilidad del cliente. Esto es consecuencia directa de que la fuente de verdad son las tareas, no las listas.

### Excepciones centralizadas
Todos los errores HTTP están definidos en `exceptions/exceptions.py` como métodos estáticos reutilizables organizados por tipo. Esto evita repetir `raise HTTPException(...)` en cada endpoint y centraliza los mensajes de error.

### UUIDs como identificadores
Se usa `uuid4` en lugar de IDs secuenciales para evitar colisiones y no exponer el volumen de datos de la API.

### Paginación flexible
Los endpoints de listado soportan dos modos: por `page` (número de página) o por `skip`/`limit` (offset manual). Si se proporciona `page`, sobreescribe `skip` automáticamente. La lógica está centralizada en `dependencies/pagination.py` mediante el sistema de dependencias de FastAPI (`Depends`), evitando repetirla en cada endpoint.

>[!Warning]
> **Limitación conocida:** la paginación se aplica después de cargar todo el JSON en memoria. Con un volumen alto de datos sería el primer cuello de botella. La solución estructural es migrar a una base de datos que soporte `LIMIT/OFFSET` a nivel de consulta.

### Aislamiento de tareas y listas
Las operaciones de borrado y actualización sobre listas **no se propagan** a sus tareas. Borrar una lista no borra sus tareas — estas siguen activas y accesibles. Es una decisión consciente: la API trata cada recurso de forma independiente y delega al cliente la decisión de qué hacer con las tareas huérfanas (reasignarlas, borrarlas, etc.).

### Soft delete
Las tareas y listas nunca se eliminan directamente del almacenamiento. Al borrar una entidad se marca `is_deleted: true`, lo que la oculta de todos los listados activos. Esto permite restaurarlas y mantener un historial. El hard delete existe como operación explícita y destructiva. 
>[!IMPORTANT]
> ### Hard delete con barrera de seguridad
> El hard delete (permanente) solo está permitido sobre entidades que ya están en estado soft-deleted. Intentar hacer hard delete sobre una entidad activa devuelve un `409 Conflict`. Esto crea fricción intencional para evitar pérdidas de datos accidentales.


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
| `DELETE` | `/tasks/{id}/hard` | Hard delete (permanente) tiene que estar soft-deleted primero |

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
| `DELETE` | `/lists/{id}/hard` | Hard delete (permanente) tiene que estar soft-deleted primero|

---

## Stack

- **Python 3.12**
- **FastAPI**
- **Pydantic v2**
- **Uvicorn**
- **Docker + docker-compose**

---

## Arrancar el proyecto

### Desde GHCR (recomendado)

```bash
docker pull ghcr.io/nico-barroso/fastask:latest
docker run -p 8000:8000 ghcr.io/nico-barroso/fastask:latest
```

### Con Docker

```bash
docker compose up
```

### Sin Docker

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.
