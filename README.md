# Simple Django REST API with PostgreSQL

A simple Django REST API with User and Product models using PostgreSQL.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
1. Install PostgreSQL
2. Create database: `djangoalemenoassignment`
3. Update credentials in `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'djangoalemenoassignment',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

### 3. Run Setup Commands
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## API Endpoints

### Users
- `GET /api/users/` - Get all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get specific user
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Products
- `GET /api/products/` - Get all products
- `POST /api/products/` - Create new product
- `GET /api/products/{id}/` - Get specific product
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

## Usage Examples

### Users
```bash
# Get all users
curl http://localhost:8000/api/users/

# Create user
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "phone_number": "1234567890"}'

# Get specific user
curl http://localhost:8000/api/users/1/

# Update user
curl -X PUT http://localhost:8000/api/users/1/ \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane", "last_name": "Smith", "phone_number": "0987654321"}'

# Delete user
curl -X DELETE http://localhost:8000/api/users/1/
```

### Products
```bash
# Get all products
curl http://localhost:8000/api/products/

# Create product (replace 1 with actual user ID)
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "Gaming laptop", "price": "999.99", "created_by": 1}'

# Get specific product
curl http://localhost:8000/api/products/1/

# Update product
curl -X PUT http://localhost:8000/api/products/1/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Gaming Laptop", "description": "High-end gaming laptop", "price": "1299.99", "created_by": 1}'

# Delete product
curl -X DELETE http://localhost:8000/api/products/1/
```

## Model Fields

### User
- first_name
- last_name  
- phone_number
- created_at (auto-generated)

### Product
- name
- description
- price
- created_by (foreign key to User)
- created_at (auto-generated)
