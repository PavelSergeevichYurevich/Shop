import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.dependencies.dependency import get_db


@pytest.fixture
def client(test_db):
    def override_get_db(): yield test_db
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app=app)
    yield client
    app.dependency_overrides.clear()
        
@pytest.fixture
def test_db():
    test_engine = create_engine('sqlite:///:memory:', 
                        connect_args={'check_same_thread': False},
                        poolclass=StaticPool
    )
    
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    db_session = TestSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    
    