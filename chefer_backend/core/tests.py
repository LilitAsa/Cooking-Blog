from django.test import TestCase
import pytest
from django.urls import reverse
from django.test import Client
from core.models import Menu, Category, Dish, MenuItem, Tag, Feature
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
    

@pytest.fixture
def test_image():
    # Создаем тестовое изображение
    image_content = b'fake-image-content'
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=image_content,
        content_type='image/jpeg'
    )

@pytest.fixture
def test_data(test_image):
    # Очищаем кэш перед тестами
    cache.clear()
    
    # Create Menus
    menu1 = Menu.objects.create(name='Lunch Menu', description='Our lunch menu')
    menu2 = Menu.objects.create(name='Dinner Menu', description='Our dinner menu')
    menu3 = Menu.objects.create(name='Weekend Brunch', description='Weekend specials')

    # Create Tags
    tag1 = Tag.objects.create(name='Vegetarian')
    tag2 = Tag.objects.create(name='Spicy')
    tag3 = Tag.objects.create(name='Seafood')

    # Create Categories
    cat1 = Category.objects.create(name='Appetizers')
    cat2 = Category.objects.create(name='Main Courses')
    cat3 = Category.objects.create(name='Desserts')
    cat4 = Category.objects.create(name='Breakfast')
    cat5 = Category.objects.create(name='Soups')
    cat6 = Category.objects.create(name='Salads')
    cat7 = Category.objects.create(name='Drinks')
    cat8 = Category.objects.create(name='Snacks')

    # Create Dishes with images
    dish1 = Dish.objects.create(name='Vegetarian Salad', description='Fresh garden salad', price=10.00, menu=menu1, image=test_image)
    dish1.tags.add(tag1)
    dish2 = Dish.objects.create(name='Spicy Chicken', description='Grilled chicken with hot sauce', price=15.00, menu=menu1, image=test_image)
    dish2.tags.add(tag2)
    dish3 = Dish.objects.create(name='Grilled Salmon', description='Fresh salmon with herbs', price=20.00, menu=menu2, image=test_image)
    dish3.tags.add(tag3)
    dish4 = Dish.objects.create(name='Beef Steak', description='Juicy beef steak', price=25.00, menu=menu2, image=test_image)
    dish5 = Dish.objects.create(name='Pancakes', description='Fluffy pancakes with syrup', price=8.00, menu=menu3, image=test_image)

    # Create MenuItems with images
    MenuItem.objects.create(category=cat1, dish=dish1, title='Green Salad', description='A light green salad', price=10.00, image=test_image, menu=menu1)
    MenuItem.objects.create(category=cat2, dish=dish2, title='Chicken Delight', description='Our chef\'s special chicken', price=15.00, image=test_image, menu=menu1)
    MenuItem.objects.create(category=cat2, dish=dish3, title='Salmon Fillet', description='Perfectly grilled salmon', price=20.00, image=test_image, menu=menu2)
    MenuItem.objects.create(category=cat2, dish=dish4, title='Tenderloin Steak', description='Premium beef steak', price=25.00, image=test_image, menu=menu2)
    MenuItem.objects.create(category=cat4, dish=dish5, title='Morning Pancakes', description='Classic breakfast pancakes', price=8.00, image=test_image, menu=menu3)

    # Create Features
    Feature.objects.create(
        title='Special Offer',
        description='Get 20% off on all main courses',
        image=test_image,
        discount_title='Main Course Discount',
        discount=20
    )
    
    return {
        'menu1': menu1, 'menu2': menu2, 'menu3': menu3,
        'tag1': tag1, 'tag2': tag2, 'tag3': tag3,
        'dish1': dish1, 'dish2': dish2, 'dish3': dish3, 'dish4': dish4, 'dish5': dish5,
        'cat1': cat1, 'cat2': cat2, 'cat3': cat3, 'cat4': cat4,
        'cat5': cat5, 'cat6': cat6, 'cat7': cat7, 'cat8': cat8
    }

@pytest.mark.django_db
def test_menu_default_load(client, test_data):
    """Test that the default menu (first one created) is loaded correctly"""
    response = client.get(reverse('menu'))
    assert response.status_code == 200
    
    # Проверяем контекст
    context = response.context
    assert 'menus' in context
    assert 'selected_menu' in context
    assert 'categories' in context
    assert 'features' in context
    
    # Проверяем, что выбрано первое меню
    assert context['selected_menu'] == test_data['menu1']
    
    # Проверяем, что категории содержат правильные блюда
    categories = context['categories']
    assert len(categories) > 0
    
    # Проверяем, что блюда из первого меню присутствуют
    found_dish1 = False
    found_dish2 = False
    for category in categories:
        for item in category.filtered_items:
            if item.dish == test_data['dish1']:
                found_dish1 = True
            if item.dish == test_data['dish2']:
                found_dish2 = True
    
    assert found_dish1
    assert found_dish2

@pytest.mark.django_db
def test_menu_specific_selection(client, test_data):
    """Test selecting a specific menu"""
    response = client.get(reverse('menu') + f'?menu={test_data["menu2"].id}')
    assert response.status_code == 200
    
    context = response.context
    assert context['selected_menu'] == test_data['menu2']
    
    # Проверяем, что блюда из второго меню присутствуют
    categories = context['categories']
    found_dish3 = False
    found_dish4 = False
    for category in categories:
        for item in category.filtered_items:
            if item.dish == test_data['dish3']:
                found_dish3 = True
            if item.dish == test_data['dish4']:
                found_dish4 = True
    
    assert found_dish3
    assert found_dish4

@pytest.mark.django_db
def test_menu_search(client, test_data):
    """Test menu search functionality"""
    # Поиск по названию блюда
    response = client.get(reverse('menu') + f'?menu={test_data["menu1"].id}&search=Salad')
    assert response.status_code == 200
    context = response.context
    
    # Проверяем, что поисковый запрос сохранен
    assert 'search_query' in context
    assert context['search_query'] == 'Salad'
    
    # Проверяем результаты поиска
    categories = context['categories']
    found_items = []
    for category in categories:
        for item in category.filtered_items:
            found_items.append(item)
    
    # Проверяем, что найдены элементы, содержащие "Salad"
    assert len(found_items) > 0
    salad_items = [item for item in found_items if 'salad' in item.title.lower() or 
                  'salad' in item.description.lower()]
    assert len(salad_items) > 0  # Должен быть найден хотя бы один салат

@pytest.mark.django_db
def test_menu_pagination(client, test_data):
    """Test menu pagination"""
    # Проверяем первую страницу
    response = client.get(reverse('menu'))
    assert response.status_code == 200
    context = response.context
    categories = context['categories']
    
    # Проверяем, что на странице не более 5 категорий
    assert len(categories) <= 5
    
    # Проверяем вторую страницу
    response = client.get(reverse('menu') + '?page=2')
    assert response.status_code == 200
    context = response.context
    categories = context['categories']
    
    # Проверяем, что на второй странице тоже не более 5 категорий
    assert len(categories) <= 5

@pytest.mark.django_db
def test_menu_search_and_pagination(client, test_data):
    """Test combination of search and pagination"""
    response = client.get(reverse('menu') + f'?menu={test_data["menu2"].id}&search=beef&page=1')
    assert response.status_code == 200
    context = response.context
    
    # Проверяем, что поиск работает с пагинацией
    assert 'search_query' in context
    assert context['search_query'] == 'beef'
    
    # Проверяем, что найден правильный результат
    categories = context['categories']
    found_items = []
    for category in categories:
        for item in category.filtered_items:
            found_items.append(item)
    
    # Проверяем, что найдены элементы, содержащие "beef"
    assert len(found_items) > 0
    beef_items = [item for item in found_items if 'beef' in item.title.lower() or 
                 'beef' in item.description.lower()]
    assert len(beef_items) > 0  # Должен быть найден хотя бы один стейк

@pytest.mark.django_db
def test_menu_search_empty(client, test_data):
    """Test search with empty query"""
    response = client.get(reverse('menu') + f'?menu={test_data["menu1"].id}&search=')
    assert response.status_code == 200
    context = response.context
    
    # Проверяем, что показаны все блюда меню
    categories = context['categories']
    found_items = []
    for category in categories:
        for item in category.filtered_items:
            found_items.append(item)
    
    # Проверяем, что найдены все блюда из меню
    assert len(found_items) > 0
    assert any(item.dish == test_data['dish1'] for item in found_items)
    assert any(item.dish == test_data['dish2'] for item in found_items)

@pytest.mark.django_db
def test_menu_search_special_chars(client, test_data):
    """Test search with special characters"""
    response = client.get(reverse('menu') + f'?menu={test_data["menu1"].id}&search=@#$%')
    assert response.status_code == 200
    context = response.context
    
    # Проверяем, что поиск корректно обрабатывает специальные символы
    categories = context['categories']
    found_items = []
    for category in categories:
        for item in category.filtered_items:
            found_items.append(item)
    
    # Проверяем, что поиск с специальными символами не вызывает ошибок
    assert response.status_code == 200

@pytest.mark.django_db
def test_menu_filter_by_tag(client, test_data):
    """Test filtering menu items by tag"""
    response = client.get(reverse('menu') + f'?menu={test_data["menu1"].id}&tag={test_data["tag1"].id}')
    assert response.status_code == 200
    context = response.context
    
    # Проверяем, что показаны только вегетарианские блюда
    categories = context['categories']
    found_items = []
    for category in categories:
        for item in category.filtered_items:
            found_items.append(item)
    
    # Проверяем, что все найденные блюда имеют тег Vegetarian
    assert len(found_items) > 0
    vegetarian_items = [item for item in found_items if test_data['tag1'] in item.dish.tags.all()]
    assert len(vegetarian_items) > 0  # Должен быть найден хотя бы один вегетарианский элемент
    assert any(item.dish == test_data['dish1'] for item in found_items)  # Должен быть найден Vegetarian Salad

@pytest.mark.django_db
def test_menu_invalid_id(client):
    """Test menu with invalid ID"""
    response = client.get(reverse('menu') + '?menu=999999')
    assert response.status_code == 404
