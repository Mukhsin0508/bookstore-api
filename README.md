# BookStore API

A professional e-commerce book store API built with FastAPI, featuring JWT authentication, role-based access control, and payment simulation.

## Features

- **Two User Roles**: Admin and User
- **JWT Authentication** using passport-jwt pattern
- **Book Management**: CRUD operations for books with image, title, price, and description
- **Order Management**: Create orders, process payments
- **Payment Simulation**: Even card numbers succeed, odd numbers fail
- **Admin Dashboard**: View statistics and ban/unban users
- **OpenAPI/Swagger**: Full API documentation
- **Async/Await**: Fully asynchronous Python implementation
- **Type Safety**: Complete type annotations throughout

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy 2.0**: Async ORM with type annotations
- **PostgreSQL**: Database with asyncpg driver
- **Pydantic**: Data validation and settings management
- **JWT**: JSON Web Tokens for authentication
- **Alembic**: Database migrations
- **Docker**: Containerization

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/Mukhsin0508/bookstore-api.git
cd bookstore-api
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Run with Docker Compose:
```bash
docker-compose up -d
```

The API will be available at http://localhost:8000/docs/

4. To access protected endpoints, you'll need to:
```text
To access protected endpoints, you'll need to:

Use the /api/v1/auth/login endpoint to log in with the admin credentials:

Username: mukhsin_mukhtariy
Password: admin123


This will return an access token.
```


### Manual Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database and update `.env` file

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Admin Credentials

- Email: admin@bookstore.com
- Password: admin123

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID

### Books
- `GET /api/v1/books` - List all books
- `GET /api/v1/books/{book_id}` - Get book details
- `POST /api/v1/books` - Create book (admin only)
- `PUT /api/v1/books/{book_id}` - Update book (admin only)
- `DELETE /api/v1/books/{book_id}` - Delete book (admin only)

### Orders
- `GET /api/v1/orders` - List user's orders
- `GET /api/v1/orders/{order_id}` - Get order details
- `POST /api/v1/orders` - Create new order
- `POST /api/v1/orders/{order_id}/pay` - Process payment
- `POST /api/v1/orders/{order_id}/cancel` - Cancel order

### Admin
- `GET /api/v1/admin/statistics` - Get statistics
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users/{user_id}/ban` - Ban user
- `POST /api/v1/admin/users/{user_id}/unban` - Unban user
- `GET /api/v1/admin/orders` - List all orders

## Payment Simulation

The payment system simulates card processing:
- **Even card numbers** (e.g., 1234567890123456) - Payment succeeds
- **Odd card numbers** (e.g., 1234567890123457) - Payment fails

Example payment request:
```json
{
  "order_id": 1,
  "card_number": "1234567890123456",
  "card_holder": "John Doe",
  "expiry_month": 12,
  "expiry_year": 2025,
  "cvv": "123"
}
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy app
```

## VSCode Configuration

The project includes VSCode settings for optimal development experience:
- Python linting with flake8
- Formatting with black
- Import sorting with isort
- Type checking enabled

## License

This project is licensed under the MIT License.