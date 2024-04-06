# роутер операция с товарами
from datetime import datetime
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from dependencies.dependency import get_db
from models.item_model import Item
from schemas.item_schema import ItemCreateSchema

item_router = APIRouter(
    prefix='/item',
    tags=['Items']
)
templates = Jinja2Templates(directory="templates")

