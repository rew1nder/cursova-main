# Привіт! 👋 I'm Taras Sen (rew1nder)<img src="https://i.pinimg.com/originals/b9/98/12/b998122f2c7ef8462a078fb6792ec411.gif" alt="#" width="25" height="20"/>

<img src="https://i.pinimg.com/originals/fa/64/3b/fa643ba588a521b8617840c3cbec0a5c.gif" alt="My Photo" width="1000" height="400"/>

# Зв'язок
- Email: divoliytaras@gmail.com
- LinkedIn: https://www.linkedin.com/in/taras-sen/

# Nike Shoes Store

This repository contains a Django-based Nike Shoes Store application.

## Features

- Django web application for an e-commerce sneaker store
- Product image carousel for showcasing multiple product images
- Shopping cart functionality with quantity selector
- Docker and Docker Compose setup for easy deployment
- Nginx for serving static and media files

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

# Directory Tree
```
nike_shoes_store/
├── __init__.py        # Package initialization
├── asgi.py            # ASGI configuration
├── settings.py        # Project settings
├── settings_prod.py   # Production settings for Docker
├── urls.py            # URL routing
├── wsgi.py            # WSGI configuration
store/
├── __init__.py        # Package initialization
├── admin.py           # Admin panel configuration with Order and OrderItem models
├── apps.py            # App configuration
├── migrations/        # Database migrations
│   ├── 0001_initial.py
│   └── __init__.py
├── forms.py           # Django forms including user registration form
├── models.py          # Database models
├── tests.py           # Test cases
├── urls.py            # URL routing for store app
├── views_auth.py      # View functions for user authentication (login, register, logout)
└── views.py           # View functions
templates/
├── base.html          # Base template
└── store/
    ├── cart.html                # Shopping cart page
    ├── checkout.html            # Checkout page for placing orders
    ├── index.html               # Homepage template
    ├── login.html               # User login page
    ├── order_confirmation.html  # Order confirmation after successful purchase
    ├── payment.html             # Payment processing page
    ├── product_detail.html      # Product detail page with image carousel and wishlist button
    ├── product_list.html        # Product listing page with fixed template syntax
    ├── profile.html             # User profile page with account info
    └── register.html            # User registration page
static/
├── css/
│   └── style.css      # Stylesheet with updated carousel control colors
├── images/
│   └──  ...           # Folder containing product and UI images
├── js/
│   └── main.js        # JavaScript file with wishlist functionality
└── nike.ico           # Favicon for the website (Nike logo)
nginx/
└── django.conf        # Nginx configuration for serving the application

Dockerfile             # Dockerfile for containerization
docker-compose.yml     # Docker Compose configuration
.entrypoint.sh         # Entrypoint script for Docker
manage.py              # Command-line utility for administrative tasks
requirements.txt       # Project dependencies
db.sqlite3             # SQLite database file
.dockerignore          # Docker ignore file
README.md              # Documentation for Docker usage
```

# Project Module Description
- **Frontend**: Utilizes Django templates for a responsive and user-friendly interface, now with a wishlist feature.
- **Backend**: Employs Django's ORM for database interactions, includes an admin panel for product management, and custom views for handling requests. Order and OrderItem models have been added for enhanced order management.
- **Database**: Uses SQLite for data storage.
- **Static Files**: Contains CSS for styling and JavaScript for dynamic functionalities.
- **Image Management**: Introduces a ProductImage model and carousel functionality for displaying multiple product images.
- **Docker Support**: Includes Dockerfile and docker-compose for containerization and deployment.

# Technology Stack
- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Server**: WSGI/ASGI
- **Containerization**: Docker, Nginx

# Usage
1. **Install Dependencies**: 
   ```
   pip install Django Pillow
   ```
2. **Set Up Project**:
   ```
   django-admin startproject nike_shoes_store .
   python manage.py startapp store
   ```
3. **Migrate Database**:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create Superuser**:
   ```
   echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell
   ```
5. **Run Server**:
   ```
   python manage.py runserver
   ```
6. **Using Docker**:
   ```
   docker-compose up --build
   ```

## Quick Start
1. To run in development mode without Docker:
   ```
   # Navigate to the project directory
   cd workspace

   # Install the required dependencies
   pip install -r requirements.txt

   # Run database migrations:
   python manage.py makemigrations
   python manage.py migrate

   # Create a superuser 
   python manage.py createsuperuser

   # Start the development server
   python manage.py runserver

   ```

2. To run in development mode with Docker:
   ```
   # Start the application
   docker-compose up
   
   # Start in detached mode
   docker-compose up -d

   # Stop the application
   docker-compose down

   # View logs
   docker-compose logs

   # Rebuild containers
   docker-compose up --build
   ```

3. Access the application:

   - Web application: http://localhost
   - Admin interface: http://localhost/admin

## Configuration

Environment variables can be set in the `docker-compose.yml` file:

- `DEBUG`: Set to 1 for development, 0 for production
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Project Structure

- `nike_shoes_store/`: Django project settings
- `store/`: Main application directory
- `templates/`: HTML templates
- `static/`: Static assets (CSS, JS, images)
- `media/`: Uploaded media files
- `nginx/`: Nginx configuration
- `Dockerfile`: Docker image configuration
- `docker-compose.yml`: Docker Compose services definition

## Production Deployment

For production deployment, update the following in `docker-compose.yml`:

```yaml
environment:
  - DEBUG=0
  - DJANGO_SETTINGS_MODULE=nike_shoes_store.settings_prod
  - SECRET_KEY=your-secure-production-secret-key
  - ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

## Adding Products

1. Access the Django admin interface at http://localhost/admin
2. Log in with your superuser credentials
3. Navigate to Products and add new products with images
4. Multiple images can be added to each product for the carousel feature

