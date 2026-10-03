from typing import Optional

from fastapi import FastAPI, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, model_validator

app = FastAPI(title="Task API", version="1.0", description="CRUD for a to-do list, stored in memory")


# ---------- Errors: every error is JSON ----------

class NotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id


@app.exception_handler(NotFound)
async def not_found_handler(request, exc: NotFound):
    return JSONResponse(status_code=404, content={"error": f"Task {exc.task_id} not found"})


@app.exception_handler(RequestValidationError)
async def invalid_body_handler(request, exc: RequestValidationError):
    problems = [
        f"{'.'.join(str(p) for p in e['loc'] if p != 'body')}: {e['msg']}".strip(": ")
        for e in exc.errors()
    ]
    return JSONResponse(status_code=400, content={"error": "Invalid request body", "details": problems})


# ---------- Models (validation rules) ----------

def clean_title(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("title must not be empty")
    return value


class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        return clean_title(v)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
        return clean_title(v) if v is not None else v

    @model_validator(mode="after")
    def needs_a_field(self):
        if self.title is None and self.done is None:
            raise ValueError("send title and/or done")
        return self


# ---------- In-memory storage ----------

tasks: list[dict] = [
    {"id": 1, "title": "Learn HTTP methods", "done": True},
    {"id": 2, "title": "Build the CRUD API", "done": False},
    {"id": 3, "title": "Publish to GitHub", "done": False},
]
next_id = 4


def find_task(task_id: int) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise NotFound(task_id)


# ---------- Endpoints ----------

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return find_task(task_id)


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    global next_id
    task = {"id": next_id, "title": body.title, "done": False}
    next_id += 1
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    task = find_task(task_id)
    if body.title is not None:
        task["title"] = body.title
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    tasks.remove(find_task(task_id))
    return Response(status_code=204)
