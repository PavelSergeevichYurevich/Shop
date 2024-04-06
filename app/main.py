from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
from database.database import engine, Base
from models.customer_model import Customer
from models.order_model import Order
from models.item_model import Item
from models.orderitem_model import OrderItem
from routes import auth, customer, item, order

app = FastAPI(title='My Shop')
app.include_router(auth.app_router)
app.include_router(customer.customer_router)
app.include_router(item.item_router)
app.include_router(order.order_router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent.absolute() / "static"), name="static")

HOST = '127.0.0.1'
if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    print('Starting server')
    uvicorn.run('main:app', port=8000, host=HOST, reload=True)
    print('Server stopped')