from pathlib import Path
from sqlalchemy import select
from app.models.models import Customer, Item
from app.routes.auth import get_current_user
from app.main import app


def test_show_items_200(client, test_db):
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
    
    item = Item(
        name='Iphone 17 PRO MAX',
        description='Iphone 17 PRO MAX',
        price=100,
        quantity=10,
        category='Cell phones'
        
    )
    test_db.add(item)
    test_db.commit()
    test_db.refresh(item)
    
    response = client.get('/item/show/')
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 2
    names = {item['name'] for item in items}
    categories = {item['category'] for item in items}
    assert 'Iphone 17 PRO' in names
    assert 'Iphone 17 PRO MAX' in names
    assert 'Cell phones' in categories
    
def test_add_item_200__user_admin(client, test_db):
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='admin'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        response = client.post('/item/add/', params={
            'name': 'Iphone 17 PRO',
            'description': 'Iphone 17 PRO',
            'price': 100,
            'quantity': 10,
            'category': 'Cell phones'
            },
            files={'file': ('test.jpg', b'fake-bytes', 'image/jpeg')}             
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'Iphone 17 PRO'
        assert data['category'] == 'Cell phones'
        assert float(data['price']) == 100.0
        assert data['quantity'] == 10
        stmnt = select(Item).where(Item.name == 'Iphone 17 PRO')
        result = test_db.execute(stmnt).scalar_one_or_none()
        assert result is not None
        assert result.image != ''
        assert 'static/images' in result.image
    finally: 
        app.dependency_overrides.pop(get_current_user, None)
        
def test_add_item_403__user_not_admin(client, test_db):
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='user'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        response = client.post('/item/add/', params={
            'name': 'Iphone 17 PRO',
            'description': 'Iphone 17 PRO',
            'price': 100,
            'quantity': 10,
            'category': 'Cell phones'
            },
            files={'file': ('test.jpg', b'fake-bytes', 'image/jpeg')}             
        )
        
        assert response.status_code == 403
        assert response.json()['error']['message'] == 'Доступ только для администраторов'
    finally: 
        app.dependency_overrides.pop(get_current_user, None)
    
    
def test_delete_item_200_user_admin(client, test_db, tmp_path):
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='admin'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        path = tmp_path / 'test.jpg'
        path.write_bytes(b'fake-image-content')
        item = Item(
            name='Iphone 17 PRO MAX',
            description='Iphone 17 PRO MAX',
            image=str(path),
            price=100,
            quantity=10,
            category='Cell phones'
            
        )
        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)
        assert path.exists()
        response = client.delete(f'/item/delete/{item.id}')
        assert response.status_code == 200
        assert response.json()['message'] == f'Товар {item.id} успешно удален'
        stmnt = select(Item).where(Item.id == item.id)
        result = test_db.execute(stmnt).scalar_one_or_none()
        assert result is None
        assert not path.exists()
    finally: 
        app.dependency_overrides.pop(get_current_user, None)
        
def test_delete_item_403_user_not_admin(client, test_db, tmp_path):
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='user'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        path = tmp_path / 'test.jpg'
        path.write_bytes(b'fake-image-content')
        item = Item(
            name='Iphone 17 PRO MAX',
            description='Iphone 17 PRO MAX',
            image=str(path),
            price=100,
            quantity=10,
            category='Cell phones'
            
        )
        test_db.add(item)
        test_db.commit()
        test_db.refresh(item)
        assert path.exists()
        response = client.delete(f'/item/delete/{item.id}')
        assert response.status_code == 403
        assert response.json()['error']['message'] == 'Доступ только для администраторов'
        stmnt = select(Item).where(Item.name == 'Iphone 17 PRO MAX')
        result = test_db.execute(stmnt).scalar_one_or_none()
        assert result is not None
        assert path.exists()
    finally: 
        app.dependency_overrides.pop(get_current_user, None)
    
    
def test_delete_item_not_exists_404(client, test_db):
    async def override_current_user(): return Customer(
        name='Test_name', 
        email='test_email@test.ru', 
        hashed_password='test_hashed_password',
        role='admin'
    )
    app.dependency_overrides[get_current_user] = override_current_user
    try:
        response = client.delete('/item/delete/999999')
        assert response.status_code == 404
        assert response.json()['error']['message'] == 'Товар не найден'
    finally: 
        app.dependency_overrides.pop(get_current_user, None)
    
    