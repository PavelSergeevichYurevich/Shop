from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
from base_module import engine, Base
from models import User, Task
from routes import tasks_router

app = FastAPI(title='My ToDo List')
app.include_router(tasks_router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent.absolute() / "static"), name="static")

HOST = '127.0.0.1'
if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    print('Starting server')
    uvicorn.run('main:app', port=8000, host=HOST, reload=True)
    print('Server stopped')