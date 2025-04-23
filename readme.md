# Iqraa - Book Management System Backend

## Project Overview
Iqraa is a comprehensive book management system built with Django REST Framework and PostgreSQL. The system provides features for managing books, user accounts, orders (borrowing/purchasing), reviews, and personalized book recommendations.

## Technology Stack
- **Framework**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Additional Features**: 
  - Sentiment Analysis for book reviews
  - Machine Learning-based book recommendations
  - CORS support for frontend integration
  - Docker containerization

## Project Structure
```
iqraa/
├── books/             # Book management
├── users/             # User authentication and profiles
├── orders/            # Book borrowing and purchasing
├── reviews/           # Book reviews and ratings
├── recommendations/   # ML-based book recommendations
└── iqraa/            # Project settings
```

## Features
1. **User Management**
   - User registration and authentication
   - Profile management
   - JWT-based authentication

2. **Book Management**
   - Book catalog with detailed information
   - Search and filter capabilities
   - Genre-based categorization

3. **Order System**
   - Book borrowing
   - Book purchasing
   - Order history tracking

4. **Review System**
   - Book ratings and reviews
   - Sentiment analysis of reviews
   - Recent and top-rated reviews

5. **Recommendation System**
   - Personalized book recommendations
   - Machine learning-based suggestions
   - Top-rated books recommendations

## API Endpoints

### Users API
- `GET/POST /api/users/` - List/Create users
- `GET/PUT/DELETE /api/users/{id}/` - Manage specific user
- `GET /api/users/me/` - Current user profile
- `POST /api/users/{id}/change_password/` - Change password

### Books API
- `GET/POST /api/books/` - List/Create books
- `GET/PUT/DELETE /api/books/{id}/` - Manage specific book
- `GET /api/books/genres/` - List book genres

### Orders API
- `GET/POST /api/orders/` - List/Create orders
- `GET/PUT/DELETE /api/orders/{id}/` - Manage specific order
- `POST /api/orders/{id}/borrow/` - Borrow book
- `POST /api/orders/{id}/purchase/` - Purchase book
- `POST /api/orders/{id}/return_book/` - Return book
- `GET /api/orders/borrowed/` - List borrowed books
- `GET /api/orders/purchased/` - List purchased books

### Reviews API
- `GET/POST /api/reviews/` - List/Create reviews
- `GET/PUT/DELETE /api/reviews/{id}/` - Manage specific review
- `GET /api/reviews/my_reviews/` - User's reviews
- `GET /api/reviews/recent/` - Recent reviews
- `GET /api/reviews/top_rated/` - Top-rated reviews
- `GET /api/reviews/{id}/sentiment/` - Review sentiment
- `GET /api/reviews/book_sentiments/` - Book review sentiments

### Recommendations API
- `GET /api/recommendations/` - List recommendations
- `POST /api/recommendations/generate/` - Generate recommendations
- `GET /api/recommendations/top_rated_books/` - Top-rated books

## Setup Instructions

1. **Using Docker (Recommended)**
   ```bash
   # Build and start the containers
   docker-compose up --build

   # The application will be available at http://localhost:8000
   ```

2. **Manual Setup (Alternative)**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   The following environment variables are configured in docker-compose.yml:
   ```
   DATABASE_URL=postgresql://postgres:postgres@db:5432/iqraa_db
   DJANGO_SETTINGS_MODULE=iqraa.settings
   ```

4. **Database Setup**
   - When using Docker, PostgreSQL is automatically configured
   - For manual setup, configure PostgreSQL according to the settings in docker-compose.yml

5. **Run Development Server (for manual setup)**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Dependencies
See `requirements.txt` for complete list:
- Django
- Django REST Framework
- psycopg2-binary
- django-cors-headers
- scikit-learn (for ML features)
- nltk (for sentiment analysis)
- And more...

## Security Features
- JWT Authentication
- Secure password handling
- CORS configuration
- SSL/TLS support in production
- XSS and CSRF protection

## API Documentation
For detailed API documentation, you can use Django REST Framework's built-in documentation interface at:
`http://localhost:8000/api/`

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
This project is licensed under the MIT License.

# this is final gradution project backend #
all the steps to make this up will be in the this file
