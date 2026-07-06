from fastapi import APIRouter, Depends, HTTPException
from app.crud import get_todo, get_todos, create_todo, update_todo, delete_todo
from app.database import get_db
from app.schemas import TodoCreate, TodoUpdate, TodoResponse
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/todos", response_model=TodoResponse)
def create_new_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    return create_todo(db, todo)

@router.get("/todos", response_model=list[TodoResponse])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_todos(db, skip, limit)

@router.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Tarefa com ID {} não encontrada".format(todo_id))
    return db_todo

@router.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo_item(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = update_todo(db, todo_id, todo)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Tarefa com ID {} não encontrada".format(todo_id))
    return db_todo

@router.delete("/todos/{todo_id}")
def delete_todo_item(todo_id: int, db: Session = Depends(get_db)):
    if delete_todo(db, todo_id):
        return {"message": "Tarefa excluída com sucesso"}
    raise HTTPException(status_code=404, detail="Tarefa com ID {} não encontrada".format(todo_id))
