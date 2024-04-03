from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import User, Task
from database import engine
from schemas import UserCreateSchema, TaskCreateSchema, TaskUpdateSchema, TaskDeleteSchema, UserCheckSchema