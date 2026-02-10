from datetime import datetime, timedelta, timezone
from typing import Annotated
import uuid
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.settings import settings
import hashlib
from app.dependencies.dependency import get_db
from app.models.models import Customer, RefreshTokens
from app.schemas.schemas import CustomerReadSchema


auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# --- Утилиты ---

def hashing_pass(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def delete_cookies(response: Response):
    response.delete_cookie(
        key="refresh_token" 
    )
    
    response.delete_cookie(
        key="access_token" 
    )
    
    return {'message': 'Logout success'}
    

def create_jwt_token(data: dict):
    to_encode = data.copy()
    # Используем современный способ работы с UTC (актуально для 2026)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    payload = {
        'sub': str(user_id),
        'type': 'refresh',
        'jti': str(uuid.uuid4()),
        'exp': datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: Session = Depends(get_db)
) -> Customer:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
    refresh_token = create_refresh_token(user.id)
    new_refresh_token = RefreshTokens(
        user_id = user.id,
        token_hash = sha256_hash(refresh_token),
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked = False
    )
    db.add(new_refresh_token)
    db.commit()
    db.refresh(new_refresh_token)
    
    # Установка Cookie (безопасный вариант)
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {token}", 
        httponly=True,
        max_age=1800
    )
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )
    
    return {"access_token": token, "token_type": "bearer"}

@auth_router.get("/me", response_model=CustomerReadSchema)
def read_users_me(current_user: Annotated[Customer, Depends(get_current_user)]):
    return current_user

@auth_router.post('/refresh/')
def read_refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPException(401, 'Не авторизован')
    try: 
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(401, 'Не авторизован')
    if payload.get('type') != 'refresh':
        raise HTTPException(401, 'Не авторизован')
    incoming_hash = sha256_hash(refresh_token)
    stmnt = select(RefreshTokens).where(RefreshTokens.token_hash == incoming_hash, RefreshTokens.revoked.is_(False))
    refresh_token_base = db.execute(stmnt).scalar_one_or_none()
    
    if not refresh_token_base:
        raise HTTPException(401, 'Не авторизован')
    if refresh_token_base.expires_at < datetime.utcnow():
        refresh_token_base.revoked = True
        db.commit()
        raise HTTPException(401, 'Не авторизован')
    try:
        user_id = int(payload.get('sub'))
    except (TypeError, ValueError): 
        raise HTTPException(401, 'Неверный токен')
    if not user_id:
        raise HTTPException(401, 'Неверный токен')
    refresh_token_base.revoked = True
    db.commit()
    new_refresh_token = create_refresh_token(user_id)
    new_refresh_token_base = RefreshTokens(
        user_id = user_id,
        token_hash = sha256_hash(new_refresh_token),
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked = False
    )
    db.add(new_refresh_token_base)
    db.commit()
    db.refresh(new_refresh_token_base)
    user = db.get(Customer, user_id)
    if not user:
        raise HTTPException(401, 'Неверный токен')
    new_access_token = create_jwt_token({'sub': user.email})
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {new_access_token}", 
        httponly=True,
        max_age=1800
    )
    response.set_cookie(
        key="refresh_token", 
        value=new_refresh_token, 
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}

@auth_router.post('/logout/')
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get('refresh_token')
    
    if not refresh_token:
       return delete_cookies(response)
    
    try: 
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return delete_cookies(response)
    
    if payload.get('type') != 'refresh':
        return delete_cookies(response)
    
    incoming_hash = sha256_hash(refresh_token)
    stmnt = select(RefreshTokens).where(RefreshTokens.token_hash == incoming_hash, RefreshTokens.revoked.is_(False))
    refresh_token_base = db.execute(stmnt).scalar_one_or_none()
    
    if not refresh_token_base:
        return delete_cookies(response)

    refresh_token_base.revoked = True
    db.commit()
  
    return delete_cookies(response)
    
    