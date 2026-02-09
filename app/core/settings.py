from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
class Settings(BaseSettings):
    # Пути
    
    DATABASE_URL:str = f"sqlite:///{BASE_DIR}/app/shop.db" 

    # API Keys
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    
    APP_HOST: str = '127.0.0.1'
    APP_PORT: int = 8000
    APP_ENV: str = 'dev'
    DEBUG: bool = False
    
    # Автоматическое чтение из .env файла
    model_config = SettingsConfigDict(env_file=BASE_DIR / '.env', extra='ignore')

settings = Settings()
