from pathlib import Path
from sqlalchemy import select
from app.models.models import Item

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
    
def test_add_item_200(client, test_db):
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
    assert data['price'] == 100
    assert data['quantity'] == 10
    stmnt = select(Item).where(Item.name == 'Iphone 17 PRO')
    result = test_db.execute(stmnt).scalar_one_or_none()
    assert result is not None
    assert result.image != ''
    assert 'static/images' in result.image
    
def test_delete_item_200(client, test_db, tmp_path):
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
    
    
def test_delete_item_not_exists_404(client, test_db):
    response = client.delete('/item/delete/999999')
    assert response.status_code == 404
    assert response.json()['error']['message'] == 'Товар не найден'
    
    
    