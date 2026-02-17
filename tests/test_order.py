from sqlalchemy import select
from app.models.models import Customer, Item, Order, OrderItem


EMAIL = 'test_email@test.ru'
PASSWORD = 'test_password'
NAME = 'Test_name'
    
def test_create_order_success_201(client, test_db, auth_user):
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 2
            }]
        }, 
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    stmnt = select(OrderItem).where(OrderItem.order_id == data['id'], OrderItem.item_id == item.id)
    order_item = test_db.execute(stmnt).scalar_one_or_none()
    assert order_item is not None
    price_at_purchase = order_item.price_at_purchase
    stmnt = select(Item).where((Item.id) == item.id)
    item = test_db.execute(stmnt).scalar_one_or_none()
    new_quantity = item.quantity
    new_price = item.price
    assert new_quantity == 8
    assert price_at_purchase == new_price
    
def test_create_order_for_another_user_403(client, test_db, auth_user):
    _, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )  
    payload = {
        'email': 'test_email@email.com',
        'password': 'test_password',
        'name': 'test_name'
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
        
    stmnt = select(Customer).where(Customer.email == 'test_email@email.com')
    customer_not_owner = test_db.execute(stmnt).scalar_one_or_none()
    assert customer_not_owner is not None
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_not_owner.id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 2
            }]
        }, 
        headers=headers
    )
    assert response.status_code == 403
    expected_message = (
        'Пользователь может создавать заказы только для себя. '
        'Администратор может создавать заказы для любых пользователей.'
    )
    assert response.json()['error']['message'] == expected_message

def test_create_order_not_enough_quantity_400(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=1,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 2
            }]
        },
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()['error']['message'] == 'Недостаточно товара Iphone 17 PRO на складе. В наличии: 1'
    
def test_update_order_item_quantity_decrease_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 3
            }]
        },
        headers=headers
        )
    assert response.status_code == 201
    order_id = response.json()['id']
    response = client.put('/order/update/', json={
        'order_id': order_id,
        'item_id': item.id,
        'new_quantity': 1
        },
        headers=headers
    )
    assert response.status_code == 200
    stmnt = select(Item).where((Item.id) == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 9
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 1
    
def test_update_order_item_400_not_enough_items(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                'item_id': item.id,
                'quantity': 3
            }]
        }, 
        headers=headers
    )
    assert response.status_code == 201
    order_id = response.json()['id']
    response = client.put('/order/update/', json={
        'order_id': order_id,
        'item_id': item.id,
        'new_quantity': 11
        },
        headers=headers
    )
    assert response.status_code == 400
    assert response.json()['error']['message'] == 'Недостаточно товара на складе. Можно добавить еще: 7'
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 7
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    order_item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert order_item_quantity == 3
    
def test_delete_order_returns_stock_and_removes_order_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    response = client.delete(f'/order/delete/{order_id}', headers=headers)
    assert response.status_code == 200
    assert response.json()['status'] == 'deleted'
    assert response.json()['id'] == order_id
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 10
    stmnt = select(Order).where(Order.id == order_id)
    order = test_db.execute(stmnt).scalar_one_or_none()
    assert order is None
    
def test_delete_order_not_owner_403(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    payload = {
            'email': 'test_email@email.com',
            'password': 'test_password',
            'name': 'test_name'
        }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
          
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
        
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    headers = {'Authorization': f'Bearer {token}'}

    response = client.delete(f'/order/delete/{order_id}', headers=headers)
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Пользователь может удалять только свои заказы. Администратор может удалять любые.'
    assert test_db.get(Order, order_id) is not None
    
        
        
def test_delete_order_is_not_exist_404(client, test_db, auth_user):
    _, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    response = client.delete('/order/delete/99999', headers=headers)
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Заказ не найден'
    
def test_delete_item_with_return_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                'item_id': item.id,
                'quantity': 3
            }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity_after_order = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity_after_order == 7
    
    response = client.request('DELETE', url='/order/deleteitem/', json={
        'order_id': order_id,
        'item_id': item.id
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    order_item = test_db.execute(stmnt).scalar_one_or_none()
    assert order_item is None
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 10
    
def test_delete_item_not_found_404(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    order_id = response.json()['id']
    
    response = client.request('DELETE', url='/order/deleteitem/', json={
        'order_id': order_id,
        'item_id': 999999999
        },
        headers=headers
    )
    
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Строка в заказе не найдена'
    
def test_add_item_quantity_decrease_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    seed_item = Item(
        name='Seed Item',
        description='Seed Item',
        price=1,
        quantity=1,
        category='Cell phones'
    )
    test_db.add(seed_item)
    test_db.commit()
    test_db.refresh(seed_item)

    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                'item_id': seed_item.id,
                'quantity': 1
            }]
        },
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    
    response = client.post('/order/additem/', json={
        'order_id': order_id,
        'item_id': item.id,
        'quantity': 2
        },
        headers=headers
    )
    
    assert response.status_code == 200
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    result = test_db.execute(stmnt).scalar_one_or_none()
    assert result is not None
    assert result.quantity == 2
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 8
    
def test_add_item_quantity_not_enough_400(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    seed_item = Item(
        name='Seed Item',
        description='Seed Item',
        price=1,
        quantity=1,
        category='Cell phones'
    )
    test_db.add(seed_item)
    test_db.commit()
    test_db.refresh(seed_item)

    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                'item_id': seed_item.id,
                'quantity': 1
            }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    
    response = client.post('/order/additem/', json={
        'order_id': order_id,
        'item_id': item.id,
        'quantity': 12
        },
        headers=headers
    )
    
    assert response.status_code == 400
    assert response.json()['error']['message'] == 'Товар недоступен или недостаточно на складе'
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 10
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    result = test_db.execute(stmnt).scalar_one_or_none()
    assert result is None
    
def test_show_orders_with_no_orders_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    response = client.get(f'/order/show/{customer_id}', 
        headers=headers)
    
    assert response.status_code == 200
    assert response.json() == []
    
def test_show_orders_200_owner(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 2
            }]
        }, 
        headers=headers
    )
    assert response.status_code == 201
    order_id = response.json()['id']
    
    response = client.get(f'/order/show/{customer_id}', 
        headers=headers
    )
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) > 0
    order_ids = {order['id'] for order in orders}
    assert order_id in order_ids
    
def test_show_orders_403_not_owner(client, test_db, auth_user):
    owner_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    payload = {
        'email': 'test_email@email.com',
        'password': 'test_password',
        'name': 'test_name'
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    result = test_db.execute(select(Customer).where(Customer.email == 'test_email@email.com')).scalar_one_or_none()
    assert result is not None
    other_id = result.id
    assert other_id is not None
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': owner_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 2
            }]
        }, 
        headers=headers
    )
    assert response.status_code == 201
    
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
    
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    
    response = client.get(f'/order/show/{owner_id}', 
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Пользователь может просматривать только свои заказы. Администратор может просматривать любые.'

    
def test_add_order_with_item_not_exist_404(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': 999999,
                    'quantity': 2
            }]
        },
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Товар 999999 не найден'
    
def test_order_update_item_not_found_404(client, test_db, auth_user):
    _, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    response = client.put('/order/update/', json={
        "order_id": 999999, 
        "item_id": 999999, 
        "new_quantity": 1
        },
        headers=headers
    )
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Позиция в заказе не найдена'
    
    
def test_item_not_found_404(client, test_db, monkeypatch, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 2
            }]
        },
        headers=headers
    )
    assert response.status_code == 201
    order_id = response.json()['id']
    item_id = item.id
    db = test_db
    original_get = db.get
    def fake_get(model, ident, *args, **kwargs):
        if model is OrderItem:
            return original_get(model, ident, *args, **kwargs)  # реальный OrderItem
        if model is Item:
            return None  # имитируем "товар исчез"
        return original_get(model, ident, *args, **kwargs)
    monkeypatch.setattr(db, 'get', fake_get)

    response = client.put('/order/update/', json={
        'order_id': order_id,
        'item_id': item_id,
        'new_quantity': 2
        },
        headers=headers
    )
    
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Товар не найден на складе'
    
def test_create_order_empty_items_400(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': []
        },
        headers=headers
    )
    
    assert response.status_code == 400
    assert response.json()['error']['code'] == 'bad_request'
    assert response.json()['error']['message'] == 'Список товаров пуст'
    
def test_show_orders_without_token_401(client, test_db):    
    response = client.get(f'/order/show/1')
    assert response.status_code == 401
    
def test_show_orders_admin_can_view_other_users_200(client, test_db, auth_user):
    owner_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    payload = {
        'email': 'test_email@email.com',
        'password': 'test_password',
        'name': 'test_name'
    }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    result = test_db.execute(select(Customer).where(Customer.email == 'test_email@email.com')).scalar_one_or_none()
    assert result is not None
    admin_id = result.id
    assert admin_id is not None
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': owner_id,
                'status': 'pending'
            },
            'items_data': [{
                
                    'item_id': item.id,
                    'quantity': 2
            }]
        },
        headers=headers
    )
    assert response.status_code == 201
    order_id = response.json()['id']
    
    admin = test_db.get(Customer, admin_id)
    assert admin is not None
    admin.role = 'admin'
    test_db.commit()
    test_db.refresh(admin)
    
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
    
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    
    response = client.get(f'/order/show/{owner_id}', 
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    orders = response.json()
    assert order_id in [o['id'] for o in orders]
    
def test_show_orders_with_no_customer_token_exists_404(client, test_db, auth_user):
    _, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
        
    response = client.get(f'/order/show/99999999999', 
        headers=headers)
    
    assert response.status_code == 404  
    assert response.json()['error']['message'] == 'Пользователь не найден'    

def test_update_not_owner_403(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    payload = {
            'email': 'test_email@email.com',
            'password': 'test_password',
            'name': 'test_name'
        }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
          
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
        
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    headers = {'Authorization': f'Bearer {token}'}
    response = client.put('/order/update/', json={
        'order_id': order_id,
        'item_id': item.id,
        'new_quantity': 1
        },
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Пользователь может править только свои заказы. Администратор может править любые.'
    
def test_update_not_owner_admin_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    payload = {
            'email': 'test_email@email.com',
            'password': 'test_password',
            'name': 'test_name'
        }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    admin_id = response.json()['id']
    admin = test_db.get(Customer, admin_id)
    admin.role = 'admin'
    test_db.commit()
    test_db.refresh(admin)
          
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
        
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    headers = {'Authorization': f'Bearer {token}'}
    response = client.put('/order/update/', json={
        'order_id': order_id,
        'item_id': item.id,
        'new_quantity': 1
        },
        headers=headers
    )
    assert response.status_code == 200
    
def test_delete_item_not_owner_403(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    payload = {
            'email': 'test_email@email.com',
            'password': 'test_password',
            'name': 'test_name'
        }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
          
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
        
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    headers = {'Authorization': f'Bearer {token}'}
    response = client.request('DELETE', url='/order/deleteitem/', json={
        'order_id': order_id,
        'item_id': item.id
        },
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Пользователь может удалять строки только в своих заказах. Администратор может удалять в любых.'
    order = test_db.get(Order, order_id)
    assert item.id in [o.item_id for o in order.items]
    item = test_db.get(Item, item.id)
    assert item.quantity == 7
    
def test_delete_item_not_owner_admin_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    payload = {
            'email': 'test_email@email.com',
            'password': 'test_password',
            'name': 'test_name'
        }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    admin_id = response.json()['id']
    admin = test_db.get(Customer, admin_id)
    admin.role = 'admin'
    test_db.commit()
    test_db.refresh(admin)
          
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
        
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    headers = {'Authorization': f'Bearer {token}'}
    response = client.request('DELETE', url='/order/deleteitem/', json={
        'order_id': order_id,
        'item_id': item.id
        },
        headers=headers
    )
    assert response.status_code == 200
    
    
def test_add_item_not_owner_403(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.post('/order/add/', json={
                'order_data': {
                    'customer_id': customer_id,
                    'status': 'pending'
                },
                'items_data': [{
                    'item_id': item.id,
                    'quantity': 3
                }]
        }, 
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    payload = {
            'email': 'test_email@email.com',
            'password': 'test_password',
            'name': 'test_name'
        }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
          
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
        
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/order/additem/', json={
        'order_id': order_id,
        'item_id': item.id,
        'quantity': 2
        },
        headers=headers
    )
    assert response.status_code == 403
    assert response.json()['error']['message'] == 'Пользователь может добавлять строки только в своих заказах. Администратор может добавлять в любых.'
    order = test_db.get(Order, order_id)
    assert item.id in [o.item_id for o in order.items]
    item = test_db.get(Item, item.id)
    assert item.quantity == 7
    
def test_add_item_not_owner_admin_200(client, test_db, auth_user):
    customer_id, headers = auth_user(
        email=EMAIL,
        password=PASSWORD, 
        name=NAME
    )
    
    seed_item = Item(
        name='Seed Item',
        description='Seed Item',
        price=1,
        quantity=1,
        category='Cell phones'
    )
    test_db.add(seed_item)
    test_db.commit()
    test_db.refresh(seed_item)

    item = Item(
        name='Iphone 17 PRO',
        description='Iphone 17 PRO',
        price=100,
        quantity=10,
        category='Cell phones'
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    payload = {
            'email': 'test_email@email.com',
            'password': 'test_password',
            'name': 'test_name'
        }
    response = client.post(url='/customer/register/', json=payload)
    assert response.status_code == 200
    admin_id = response.json()['id']
    admin = test_db.get(Customer, admin_id)
    admin.role = 'admin'
    test_db.commit()
    test_db.refresh(admin)
          
    response = client.post(url='/auth/token', data={
            'username': 'test_email@email.com',
            'password': 'test_password'
            
        })
        
    assert response.status_code == 200
    token = response.json()['access_token']
    assert token is not None
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.post('/order/add/', json={
            'order_data': {
                'customer_id': customer_id,
                'status': 'pending'
            },
            'items_data': [{
                'item_id': seed_item.id,
                'quantity': 1
            }]
        },
        headers=headers
    )
    assert response.status_code == 201    
    order_id = response.json()['id']
    
    response = client.post('/order/additem/', json={
        'order_id': order_id,
        'item_id': item.id,
        'quantity': 2
        },
        headers=headers
    )
    
    assert response.status_code == 200
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    result = test_db.execute(stmnt).scalar_one_or_none()
    assert result is not None
    assert result.quantity == 2
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 8

    
    
    
    
    
    
