import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import StaticPool, create_engine, select
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.dependencies.dependency import get_db
from sqlalchemy import event

from app.models.models import Customer


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
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    event.listen(test_engine, "connect", set_sqlite_pragma)
    
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    db_session = TestSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    
@pytest.fixture
def auth_user(client, test_db):
    def register_and_login(email, password, name):
        payload = {
            'email': email,
            'password': password,
            'name': name
        }
        response = client.post(url='/customer/register/', json=payload)
        assert response.status_code == 200
        
        stmnt = select(Customer).where(Customer.email == email)
        customer = test_db.execute(stmnt).scalar_one_or_none()
        assert customer is not None
        customer_id = customer.id
        
        response = client.post(url='/auth/token', data={
                'username': email,
                'password': password
                
            })
        
        assert response.status_code == 200
        token = response.json()['access_token']
        assert token is not None
        headers = {'Authorization': f'Bearer {token}'}
        return customer_id, headers
    return register_and_login
    
    
