from typing import Annotated
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, Cookie, FastAPI, Depends, HTTPException, Response
from sqlalchemy import create_engine, select
from dependencies.dependency import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from models.models import Customer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker


app_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "60dad50dcf49cdb04ff89b51a6c5b3abcb6eeba1a628b96b1f57c06a838d3383"
ALGORITHM = "HS256"
EXPIRATION_TIME = timedelta(minutes=30)

def get_user(email: str):
    engine = create_engine("sqlite:///./shop.db", echo=True)
    SessionLocal = sessionmaker(autoflush=False, bind=engine)
    db = SessionLocal()
    stmnt = select(Customer).where(Customer.email == email)
    user = db.scalars(stmnt).one()
    return user
    
def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + EXPIRATION_TIME
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None
    
def hashing_pass(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = decoded_data.get('sub')  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user

@app_router.get("/users/me")
def get_user_me(current_user: Annotated[Customer, Depends(get_current_user)]):
    return current_user

@app_router.post('/token')
def authenticate_user(response: Response,  form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username) # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(form_data.password, user.hashed_password)

    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    jwt_token = create_jwt_token({"sub": user.email})
    response.set_cookie(key = user.email, value = jwt_token)
    return {"access_token": jwt_token, "token_type": "bearer"}

@app_router.post('/admin')
def get_user_role(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = get_user(form_data.username) # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    is_password_correct = pwd_context.verify(form_data.password, user.hashed_password)
    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    is_role_admin = user.role
    if is_role_admin == 'admin':
        return {user.email: is_role_admin}
    else:
        raise HTTPException(status_code=401, detail="User is not admin")

    
    




