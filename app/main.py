from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
from contextlib import asynccontextmanager
from app.routes import auth, customer, item, order
from app.core.settings import settings
from app.core.errors import http_exception_handler, request_validation_error_handler, exception_handler
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger('shop')
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting server')
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        raise RuntimeError('SECRET_KEY отсутствует или не соответствует')
    yield
    logger.info('Server stopped')

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

app.exception_handler(HTTPException)(http_exception_handler)
app.exception_handler(RequestValidationError)(request_validation_error_handler)
app.exception_handler(Exception)(exception_handler)
app.exception_handler(StarletteHTTPException)(http_exception_handler)

if __name__ == '__main__':
    
    uvicorn.run(
        'main:app', 
        port=settings.APP_PORT, 
        host=settings.APP_HOST, 
        reload=settings.DEBUG
    )
    
#PYTHONPATH=app ./env/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000