from sqlalchemy import select
from app.models.models import Customer
from app.main import app
from app.routes.auth import get_current_user

EMAIL = 'test_email@test.ru'
PASSWORD = 'test_password'
NAME = 'Test_name'

def test_show_customers_admin_200(client, test_db):
    payload = {
        'email': EMAIL,
        'password': PASSWORD,
        'name': NAME
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='admin'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    
    try:
        
        response = client.get('/customer/show/')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        names = {u['name'] for u in data}
        assert 'Test_name' in names
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        
    
def test_show_customers_not_admin_403(client, test_db, auth_user):
    _, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )

    response = client.get('/customer/show/', headers=headers)
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Доступ только для администраторов'
    
def test_show_no_customers(client, test_db):
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='admin'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    
    try:
        response = client.get('/customer/show/')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        
    
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
    
def test_delete_customer_not_admin_403(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    response = client.delete(f'/customer/delete/', params={'id': customer_id}, headers=headers)
    
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Доступ только для администраторов'
    
def test_delete_customer_admin_200(client, test_db):
    payload = {
        'email': EMAIL,
        'password': PASSWORD,
        'name': NAME
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='admin'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    
    try:
        stmnt = select(Customer).where(Customer.email == EMAIL)
        result = test_db.execute(stmnt).scalar_one_or_none()
        assert result is not None
        customer_id = result.id
        
        response = client.delete('/customer/delete/', params={'id': customer_id})
        assert response.status_code == 200
        assert response.json()['status'] == 'deleted'
        assert test_db.get(Customer, customer_id) is None
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        

    
    
    
    
    
    
    
    