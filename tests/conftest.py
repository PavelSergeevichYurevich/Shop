import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base


@pytest.fixture
def client():
    client = TestClient(app=app)
    yield client
    
@pytest.fixture
def test_db():
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    db_session = TestSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=test_engine)
    
    