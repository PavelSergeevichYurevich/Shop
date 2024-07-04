import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from dependencies.dependency import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from models.models import Customer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "60dad50dcf49cdb04ff89b51a6c5b3abcb6eeba1a628b96b1f57c06a838d3383"
ALGORITHM = "HS256"
EXPIRATION_TIME = timedelta(minutes=30)

def get_user(email: str, db: Session = Depends(get_db)):
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

def authenticate_user(username: str, password: str):
    user = get_user(username) # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    is_password_correct = pwd_context.verify(password, user.hashed_password)

    if not is_password_correct:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    jwt_token = create_jwt_token({"sub": user.username})
    return {"access_token": jwt_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_user(decoded_data["sub"])  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user

def get_user_me(current_user: Customer = Depends(get_current_user)):
    return current_user
    




