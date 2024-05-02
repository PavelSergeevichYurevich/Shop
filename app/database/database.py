from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

engine = create_engine("sqlite:///./shop.db", echo=True)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
session = SessionLocal()

class Base(DeclarativeBase):       
    pass