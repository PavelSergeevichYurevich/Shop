import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
from contextlib import asynccontextmanager
from app.routes import auth, customer, item, order

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)
HOST = os.getenv("APP_HOST", "127.0.0.1")
PORT = int(os.getenv("APP_PORT", 8000))

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Starting server...')
    yield
    print('Server stopped')

app = FastAPI(
    title='Shop',
    lifespan=lifespan
)

app.include_router(auth.auth_router)
app.include_router(customer.customer_router)
app.include_router(item.item_router)
app.include_router(order.order_router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent.absolute() / "static"), name="static")

static_path = Path(__file__).parent.absolute() / "static"

if __name__ == '__main__':
    
    uvicorn.run(
        'main:app', 
        port=PORT, 
        host=HOST, 
        reload=True
    )
    
#PYTHONPATH=app ./env/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000