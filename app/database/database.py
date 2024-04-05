from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./shop.db", echo=True)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
session = SessionLocal()

class Base(DeclarativeBase):       
    pass