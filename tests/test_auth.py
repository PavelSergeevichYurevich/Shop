EMAIL = 'test_email@test.ru'
PASSWORD = 'test_password'
NAME = 'Test_name'

def test_login_success_200(client, test_db):
    payload = {
        'email': EMAIL,
        'password': PASSWORD,
        'name': 'Test_name',
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    response = client.post(url='/auth/token', data={
        'username': EMAIL,
        'password':PASSWORD
        
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert isinstance(data['access_token'], str)
    assert data['token_type'] == 'bearer'
    
def test_incorrect_password_401(client, test_db):
    payload = {
        'email': EMAIL,
        'password': PASSWORD,
        'name': 'Test_name',
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    response = client.post(url='/auth/token', data={
        'username': EMAIL,
        'password':'wrong_pass'
        
    })
    assert response.status_code == 401
    assert response.json()['error']['message'] == 'Неверный email или пароль'
    
def test_auth_without_token_401(client, test_db):
    response = client.get('/auth/me')
    assert response.status_code == 401
    
def test_auth_with_token_200(client, test_db):
    payload = {
        'email': EMAIL,
        'password': PASSWORD,
        'name': NAME,
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    response = client.post(url='/auth/token', data={
        'username': EMAIL,
        'password':PASSWORD
        
    })
    assert response.status_code == 200
    
    token = response.json()['access_token']
    response = client.get('/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json()['email'] == EMAIL
    assert response.json()['name'] == NAME
    
    
    
    