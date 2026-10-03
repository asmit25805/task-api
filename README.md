# Task API

A small CRUD API for a to-do list, built with FastAPI. Data lives in memory, so it resets when the server restarts.

## Run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000/docs to try every endpoint.

## Endpoints

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | / | API description | 200 | — |
| GET | /health | Liveness check | 200 | — |
| GET | /tasks | List all tasks | 200 | — |
| GET | /tasks/{id} | Get one task | 200 | 404 |
| POST | /tasks | Create a task | 201 | 400 |
| PUT | /tasks/{id} | Update title and/or done | 200 | 400, 404 |
| DELETE | /tasks/{id} | Delete a task | 204 | 404 |

## Example

```
[paste your curl -i output here]
```

## Swagger UI

![Swagger UI](screenshot.png)

## Notes

Data is stored in a Python list, so restarting the server resets it. A database would fix that.
