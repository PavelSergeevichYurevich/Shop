from sqlalchemy import select
from app.models.models import Customer, Item, OrderItem


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
    
    response = client.post('/order/add', json={
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
    
    