from pytest import MonkeyPatch
from sqlalchemy import select
from app.models.models import Customer, Item, Order, OrderItem


EMAIL = 'test_email@test.ru'
PASSWORD = 'test_password'
NAME = 'Test_name'

def test_create_order_success_201(client, test_db):
    customer = Customer(name=NAME, 
                        email=EMAIL, 
                        hashed_password=PASSWORD
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            
                'item_id': item.id,
                'quantity': 2
            }]
    })
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
    
    
def test_create_order_not_enough_quantity_400(client, test_db):
    customer = Customer(name=NAME, 
                        email=EMAIL, 
                        hashed_password=PASSWORD
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            
                'item_id': item.id,
                'quantity': 2
            }]
    })
    assert response.status_code == 400
    assert response.json()['error']['message'] == 'Недостаточно товара Iphone 17 PRO на складе. В наличии: 1'
    
def test_update_order_item_quantity_decrease_200(client, test_db):
    customer = Customer(name=NAME, 
                        email=EMAIL, 
                        hashed_password=PASSWORD
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            
                'item_id': item.id,
                'quantity': 3
            }]
    })
    assert response.status_code == 201
    order_id = response.json()['id']
    response = client.put('/order/update/', json={
        'order_id': order_id,
        'item_id': item.id,
        'new_quantity': 1
    })
    assert response.status_code == 200
    stmnt = select(Item).where((Item.id) == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 9
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 1
    
def test_update_order_item_400_not_enough_items(client, test_db):
    customer = Customer(
        name=NAME,
        hashed_password=PASSWORD,
        email=EMAIL
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            'item_id': item.id,
            'quantity': 3
        }]
    })
    assert response.status_code == 201
    order_id = response.json()['id']
    response = client.put('/order/update/', json={
        'order_id': order_id,
        'item_id': item.id,
        'new_quantity': 11
    })
    assert response.status_code == 400
    assert response.json()['error']['message'] == 'Недостаточно товара на складе. Можно добавить еще: 7'
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 7
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    order_item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert order_item_quantity == 3
    
def test_delete_order_returns_stock_and_removes_order_200(client, test_db):
    customer = Customer(
        name=NAME,
        hashed_password=PASSWORD,
        email=EMAIL
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            'item_id': item.id,
            'quantity': 3
        }]
    })
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    new_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert new_quantity == 7
    
    response = client.delete(f'/order/delete/{order_id}')
    assert response.status_code == 200
    assert response.json()['status'] == 'deleted'
    assert response.json()['id'] == order_id
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 10
    stmnt = select(Order).where(Order.id == order_id)
    order = test_db.execute(stmnt).scalar_one_or_none()
    assert order is None
    
def test_delete_order_is_not_exist_404(client, test_db):
    response = client.delete('/order/delete/99999')
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Заказ не найден'
    
def test_delete_item_with_return_200(client, test_db):
    customer = Customer(
        name=NAME,
        hashed_password=PASSWORD,
        email=EMAIL
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            'item_id': item.id,
            'quantity': 3
        }]
    })
    assert response.status_code == 201    
    order_id = response.json()['id']
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity_after_order = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity_after_order == 7
    
    response = client.request('DELETE', url='/order/deleteitem/', json={
        'order_id': order_id,
        'item_id': item.id
    })
    assert response.status_code == 200
    assert response.json()['status'] == 'success'
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    order_item = test_db.execute(stmnt).scalar_one_or_none()
    assert order_item is None
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 10
    
def test_delete_item_not_found_404(client, test_db):
    customer = Customer(
        name=NAME,
        hashed_password=PASSWORD,
        email=EMAIL
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
    
    response = client.request('DELETE', url='/order/deleteitem/', json={
        'order_id': 999999999,
        'item_id': 999999999
    })
    
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Строка в заказе не найдена'
    
def test_add_item_quantity_decrease_200(client, test_db):
    customer = Customer(
        name=NAME,
        hashed_password=PASSWORD,
        email=EMAIL
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': []
    })
    assert response.status_code == 201    
    order_id = response.json()['id']
    
    response = client.post('/order/additem/', json={
        'order_id': order_id,
        'item_id': item.id,
        'quantity': 2
    })
    
    assert response.status_code == 200
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    result = test_db.execute(stmnt).scalar_one_or_none()
    assert result is not None
    assert result.quantity == 2
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 8
    
def test_add_item_quantity_not_enough_400(client, test_db):
    customer = Customer(
        name=NAME,
        hashed_password=PASSWORD,
        email=EMAIL
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': []
    })
    assert response.status_code == 201    
    order_id = response.json()['id']
    
    response = client.post('/order/additem/', json={
        'order_id': order_id,
        'item_id': item.id,
        'quantity': 12
    })
    
    assert response.status_code == 400
    assert response.json()['error']['message'] == 'Товар недоступен или недостаточно на складе'
    stmnt = select(Item).where(Item.id == item.id)
    item_quantity = test_db.execute(stmnt).scalar_one_or_none().quantity
    assert item_quantity == 10
    stmnt = select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.item_id == item.id)
    result = test_db.execute(stmnt).scalar_one_or_none()
    assert result is None
    
def test_show_orders_with_no_orders_200(client, test_db):
    customer = Customer(
        name=NAME,
        hashed_password=PASSWORD,
        email=EMAIL
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
    response = client.get(f'/order/show/{customer.id}')
    assert response.status_code == 200
    assert response.json() == []
    
def test_show_orders_200(client, test_db):
    customer = Customer(name=NAME, 
                        email=EMAIL, 
                        hashed_password=PASSWORD
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            
                'item_id': item.id,
                'quantity': 2
            }]
    })
    assert response.status_code == 201
    order_id = response.json()['id']
    
    response = client.get(f'/order/show/{customer.id}')
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) > 0
    order_ids = {order['id'] for order in orders}
    assert order_id in order_ids
    
def test_add_order_with_item_not_exist_404(client, test_db):
    customer = Customer(name=NAME, 
                        email=EMAIL, 
                        hashed_password=PASSWORD
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
    response = client.post('/order/add/', json={
        'order_data': {
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            
                'item_id': 999999,
                'quantity': 2
            }]
    })
    
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Товар 999999 не найден'
    
def test_order_update_item_not_found_404(client, test_db):
    response = client.put('/order/update/', json={
        "order_id": 999999, 
        "item_id": 999999, 
        "new_quantity": 1
    })
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Позиция в заказе не найдена'
    
def test_create_order_wrong_500(client, test_db, monkeypatch):
    response = client.post('/order/add/', json={
        'order_data': {
            'customer_id': 99999,
            'status': 'pending'
        },
        'items_data': []
    })
    assert response.status_code == 500
    assert response.json()['error']['message'] == 'Ошибка при создании заказа'
    
def test_item_not_found_404(client, test_db, monkeypatch):
    customer = Customer(name=NAME, 
                        email=EMAIL, 
                        hashed_password=PASSWORD
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    
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
            'customer_id': customer.id,
            'status': 'pending'
        },
        'items_data': [{
            
                'item_id': item.id,
                'quantity': 2
            }]
    })
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
    })
    
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Товар не найден на складе'
    
    

    
    
    
    
    
    