# Chefer - Ресторанный веб-сайт-блог

## Project Overview
Chefer is a comprehensive restaurant management system built with Django. It provides functionality for menu management, dish categorization, and customer interactions.

## Model Relationships

### Menu Structure
```
Menu
 └── Category
     └── MenuItem
         └── Dish
             └── Tags
```

### Key Models and Their Relationships

1. **Menu**
   - Represents different menus (e.g., Lunch Menu, Dinner Menu)
   - Contains multiple categories

2. **Category**
   - Belongs to a Menu
   - Contains multiple MenuItems
   - Example: "Appetizers", "Main Courses", "Desserts"

3. **MenuItem**
   - Belongs to a Category
   - Can be linked to a Dish
   - Contains:
     - Title
     - Description
     - Price
     - Image
     - Availability status

4. **Dish**
   - Can be linked to MenuItems
   - Has multiple Tags
   - Contains:
     - Name
     - Description
     - Preparation time
     - Tags for filtering

5. **Tag**
   - Many-to-many relationship with Dishes
   - Used for filtering and categorization
   - Example: "Spicy", "Vegetarian", "Gluten-Free"

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Admin Interface

Access the admin interface at `/admin` to:
1. Create and manage menus
2. Add categories to menus
3. Create menu items and link them to dishes
4. Manage dishes and their tags
5. Update prices and availability

## Key Features

- Menu management with categories
- Dish tagging system
- Image upload for menu items
- Price management
- Availability tracking
- Responsive design
- Search and filter functionality

## Development Guidelines

1. **Adding New Menu Items**:
   - Create a Dish first
   - Add appropriate tags to the Dish
   - Create a MenuItem and link it to the Dish
   - Assign the MenuItem to a Category

2. **Managing Categories**:
   - Categories must be associated with a Menu
   - MenuItems must be assigned to a Category
   - Categories can be reordered within a Menu

3. **Tag Management**:
   - Tags should be descriptive and consistent
   - Use existing tags when possible
   - Tags help customers filter dishes by preferences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 