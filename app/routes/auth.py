from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Annotated, Optional
from dotenv import load_dotenv
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.dependency import get_db
from app.models.models import Customer

env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Утилиты ---

def hashing_pass(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(data: dict):
    to_encode = data.copy()
    # Используем современный способ работы с UTC (актуально для 2026)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_db)
) -> Customer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    # Ищем пользователя в БД через инъекцию зависимости db
    user = db.scalar(select(Customer).where(Customer.email == email))
    if user is None:
        raise credentials_exception
    return user

# Зависимость для проверки прав админа
async def get_current_admin(current_user: Annotated[Customer, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ только для администраторов")
    return current_user

# --- Роутеры ---

@auth_router.post('/token')
def login_for_access_token(
    response: Response, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    # Поиск пользователя (используем db из зависимостей, а не создаем новую!)
    user = db.scalar(select(Customer).where(Customer.email == form_data.username))
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверный email или пароль"
        )

    token = create_jwt_token({"sub": user.email})
    
    # Установка Cookie (безопасный вариант)
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {token}", 
        httponly=True, # Защита от кражи токена через JS (XSS)
        max_age=1800
    )
    
    return {"access_token": token, "token_type": "bearer"}

@auth_router.get("/me")
def read_users_me(current_user: Annotated[Customer, Depends(get_current_user)]):
    return current_user