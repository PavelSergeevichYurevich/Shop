from sqlalchemy import select
from app.models.models import Customer
from app.main import app
from app.routes.auth import get_current_user


def test_show_customers(client, test_db):
    customer = Customer(name='Test_name', 
                        email='test_email@test.ru', 
                        hashed_password='test_hashed_password'
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
    response = client.get('/customer/show/')
    
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['name'] == 'Test_name'
    
def test_show_no_customers(client, test_db):
    response = client.get('/customer/show/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
    
def test_register_customer_success(client, test_db):
    payload:dict = {
        'email':'test_email@test.ru',
        'password':'test_password',
        'name': 'Test_name',
    }
    response = client.post(url='/customer/register/', json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data['email'] == payload['email']
    assert data['name'] == payload['name']
    assert 'password' not in data
    assert 'hashed_password' not in data
    
    stmnt = select(Customer).where(Customer.email == payload['email'])
    customer = test_db.execute(stmnt).scalar_one_or_none()
    assert customer is not None
    assert customer.hashed_password != payload['password']
    
def test_register_customer_duplicate_email(client, test_db):
    payload:dict = {
        'email':'test_email@test.ru',
        'password':'test_password',
        'name': 'Test_name',
    }
    
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 400
    data = response.json()
    assert isinstance(data, dict)
    assert data['error']['message'] == 'Email уже зарегистрирован'
    
def test_update_customer_returns_404_if_customer_missing(client, test_db):
    customer1 = Customer(name='Test_name', 
                        email='test_email@test.ru', 
                        hashed_password='test_hashed_password'
    )
    test_db.add(customer1)
    test_db.commit()
    test_db.refresh(customer1)
    
    async def override_current_user(): return customer1
    app.dependency_overrides[get_current_user] = override_current_user
    response = client.put(url='/customer/update/999999', json={'name': 'new_name'})
    assert response.status_code == 404
    data = response.json()
    assert data['error']['message'] == 'Пользователь не найден'
    del app.dependency_overrides[get_current_user]
    
def test_update_customer_returns_403_if_updating_other_user(client, test_db):
    customer1 = Customer(name='Test_name', 
                        email='test_email@test.ru', 
                        hashed_password='test_hashed_password'
    )
    test_db.add(customer1)
    test_db.commit()
    test_db.refresh(customer1)
    
    customer2 = Customer(name='Test_name_1', 
                        email='test_email_1@test.ru', 
                        hashed_password='test_hashed_password_1'
    )
    test_db.add(customer2)
    test_db.commit()
    test_db.refresh(customer2)
    
    async def override_current_user(): return customer1
    app.dependency_overrides[get_current_user] = override_current_user
    
    customer2_id = customer2.id
    
    response = client.put(url=f'/customer/update/{customer2_id}', json={'name': 'new_name'})
    assert response.status_code == 403
    data = response.json()
    assert data['error']['message'] == 'Недостаточно прав'
    
    del app.dependency_overrides[get_current_user]
    
def test_update_customer_returns_200_if_updating_same_user(client, test_db):
    customer1 = Customer(name='Test_name', 
                        email='test_email@test.ru', 
                        hashed_password='test_hashed_password'
    )
    test_db.add(customer1)
    test_db.commit()
    test_db.refresh(customer1)
    
    async def override_current_user(): return customer1
    app.dependency_overrides[get_current_user] = override_current_user
    
    response = client.put(url=f'/customer/update/{customer1.id}', json={'name': 'new_name'})
    assert response.status_code == 200
    assert response.json()['name'] == 'new_name'
    
    del app.dependency_overrides[get_current_user]
    
def test_update_403_when_non_admin_tries_to_change_role(client, test_db):
    customer1 = Customer(name='Test_name', 
                        email='test_email@test.ru', 
                        hashed_password='test_hashed_password'
    )
    test_db.add(customer1)
    test_db.commit()
    test_db.refresh(customer1)
    
    async def override_current_user(): return customer1
    app.dependency_overrides[get_current_user] = override_current_user
    
    response = client.put(url=f'/customer/update/{customer1.id}', json={'role': 'admin'})
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Только админ может менять роли'
    
    del app.dependency_overrides[get_current_user]
    
def test_register_customer_wrong_format_email_422(client, test_db):
    payload:dict = {
        'email':'test_email_test.ru',
        'password':'test_password',
        'name': 'Test_name',
    }
    
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'validation_error'
    details = response.json()['error']['details']
    assert any('email' in err['loc'] for err in details)
    
    
    
    
    
    
    
    
    
    