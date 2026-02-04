from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager
from app.routes import auth, customer, item, order
from app.core.settings import settings

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
static_path = Path(__file__).parent.absolute() / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == '__main__':
    
    uvicorn.run(
        'main:app', 
        port=settings.APP_PORT, 
        host=settings.APP_HOST, 
        reload=settings.DEBUG
    )
    
#PYTHONPATH=app ./env/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000