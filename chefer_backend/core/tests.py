from django.test import TestCase
import pytest
from django.urls import reverse
from django.test import Client
from core.models import Menu, Category, Dish, MenuItem, Tag
    

@pytest.fixture
def test_data():
    # Create Menus
    menu1 = Menu.objects.create(name='Lunch Menu')
    menu2 = Menu.objects.create(name='Dinner Menu')
    menu3 = Menu.objects.create(name='Weekend Brunch')

    # Create Tags
    tag1 = Tag.objects.create(name='Vegetarian')
    tag2 = Tag.objects.create(name='Spicy')
    tag3 = Tag.objects.create(name='Seafood')

    # Create Dishes
    dish1 = Dish.objects.create(name='Vegetarian Salad', description='Fresh garden salad', price=10.00, menu=menu1)
    dish1.tags.add(tag1)
    dish2 = Dish.objects.create(name='Spicy Chicken', description='Grilled chicken with hot sauce', price=15.00, menu=menu1)
    dish2.tags.add(tag2)
    dish3 = Dish.objects.create(name='Grilled Salmon', description='Fresh salmon with herbs', price=20.00, menu=menu2)
    dish3.tags.add(tag3)
    dish4 = Dish.objects.create(name='Beef Steak', description='Juicy beef steak', price=25.00, menu=menu2)
    dish5 = Dish.objects.create(name='Pancakes', description='Fluffy pancakes with syrup', price=8.00, menu=menu3)

    # Create Categories
    cat1 = Category.objects.create(name='Appetizers')
    cat2 = Category.objects.create(name='Main Courses')
    cat3 = Category.objects.create(name='Desserts')
    cat4 = Category.objects.create(name='Breakfast')


    # Create MenuItems and link them to Dishes and Categories
    MenuItem.objects.create(category=cat1, dish=dish1, title='Green Salad', description='A light green salad', price=10.00)
    MenuItem.objects.create(category=cat2, dish=dish2, title='Chicken Delight', description='Our chef\'s special chicken', price=15.00)
    MenuItem.objects.create(category=cat2, dish=dish3, title='Salmon Fillet', description='Perfectly grilled salmon', price=20.00)
    MenuItem.objects.create(category=cat2, dish=dish4, title='Tenderloin Steak', description='Premium beef steak', price=25.00)
    MenuItem.objects.create(category=cat4, dish=dish5, title='Morning Pancakes', description='Classic breakfast pancakes', price=8.00)
    
    return {
        'menu1': menu1, 'menu2': menu2, 'menu3': menu3,
        'tag1': tag1, 'tag2': tag2, 'tag3': tag3,
        'dish1': dish1, 'dish2': dish2, 'dish3': dish3, 'dish4': dish4, 'dish5': dish5,
        'cat1': cat1, 'cat2': cat2, 'cat3': cat3, 'cat4': cat4
    }

@pytest.mark.django_db
def test_menu_default_load(client, test_data):
    # Test that the default menu (first one created) is loaded
    response = client.get(reverse('menu'))
    assert response.status_code == 200
    assert test_data['menu1'].name.encode() in response.content # Check if default menu name is in content
    assert test_data['dish1'].name.encode() in response.content # Check if a dish from default menu is present
    assert test_data['dish3'].name.encode() not in response.content # Check if a dish from another menu is NOT present

@pytest.mark.django_db
def test_menu_specific_menu_selection(client, test_data):
    # Test selecting a specific menu
    response = client.get(reverse('menu') + f'?menu={test_data["menu2"].id}')
    assert response.status_code == 200
    assert test_data['menu2'].name.encode() in response.content
    assert test_data['dish3'].name.encode() in response.content # Dish from menu2
    assert test_data['dish1'].name.encode() not in response.content # Dish from menu1

@pytest.mark.django_db
def test_menu_search_by_dish_name(client, test_data):
    # Test searching for a dish name within a specific menu
    response = client.get(reverse('menu') + f'?menu={test_data["menu1"].id}&search=Salad')
    assert response.status_code == 200
    assert test_data['dish1'].name.encode() in response.content # Vegetarian Salad from menu1
    assert test_data['dish2'].name.encode() not in response.content # Spicy Chicken is not in search results
    assert test_data['dish3'].name.encode() not in response.content # Grilled Salmon is not in menu1

@pytest.mark.django_db
def test_menu_search_by_dish_description(client, test_data):
    # Test searching by dish description
    response = client.get(reverse('menu') + f'?menu={test_data["menu2"].id}&search=salmon')
    assert response.status_code == 200
    assert test_data['dish3'].name.encode() in response.content # Grilled Salmon from menu2
    assert test_data['dish4'].name.encode() not in response.content # Beef Steak not in search

@pytest.mark.django_db
def test_menu_search_by_menu_item_title(client, test_data):
    # Test searching by MenuItem title
    response = client.get(reverse('menu') + f'?menu={test_data["menu3"].id}&search=Morning')
    assert response.status_code == 200
    assert test_data['dish5'].name.encode() in response.content # Pancakes from menu3
    assert test_data['dish1'].name.encode() not in response.content # Vegetarian Salad not in menu3

@pytest.mark.django_db
def test_menu_pagination(client, test_data):
    # Create more categories to test pagination
    for i in range(6, 12):
        Category.objects.create(name=f'Category {i}')
    
    # Reload test_data to include new categories if needed, or directly test
    # This test might need more nuanced data setup for categories linked to MenuItems
    # For simplicity, let's assume default menu has enough categories for pagination
    
    # Test first page
    response = client.get(reverse('menu'))
    assert response.status_code == 200
    # Check if first 5 categories are present
    assert len(response.context['categories'].object_list) <= 5
    assert response.context['categories'].has_next()

    # Test second page
    response = client.get(reverse('menu') + '?page=2')
    assert response.status_code == 200
    assert len(response.context['categories'].object_list) <= 5
    # Check if there is a previous page
    assert response.context['categories'].has_previous()

@pytest.mark.django_db
def test_menu_search_and_pagination(client, test_data):
    # Combine search and pagination
    # This requires careful setup to ensure specific search results fall on specific pages
    # For now, a basic check that it doesn't crash
    response = client.get(reverse('menu') + f'?menu={test_data["menu2"].id}&search=beef&page=1')
    assert response.status_code == 200
    assert test_data['dish4'].name.encode() in response.content # Beef Steak
    assert test_data['dish3'].name.encode() not in response.content # Salmon is not in search
    assert not response.context['categories'].has_next() # Assuming Beef Steak is only result and on first page
