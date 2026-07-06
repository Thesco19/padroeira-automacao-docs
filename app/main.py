from fastapi import FastAPI
from app.routers import todos

app = FastAPI()

app.include_router(todos.router)
