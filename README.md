# CortejTech FastAPI Backend - Version 1.0# CortejTech FastAPI Backend - Version 1.0



A high-performance FastAPI backend service for CortejTech's admin dashboard and website, designed to provide fast, secure, and scalable API endpoints.A high-performance FastAPI backend service for CortejTech's admin dashboard and website, designed to provide fast, secure, and scalable API endpoints.



## 🚀 Quick Start## 🚀 Quick Start



### Prerequisites### Prerequisites

- Python 3.12 or higher- Python 3.12 or higher

- Virtual environment (recommended)- Virtual environment (recommended)

- Access to Supabase database- Access to Supabase database



### Installation### Installation



1. **Navigate to backend directory**1. **Navigate to backend directory**

   ```powershell   ```powershell

   cd backend   cd backend

   ```   ```



2. **Install dependencies**2. **Install dependencies**

   ```powershell   ```powershell

   pip install -r requirements.txt   pip install -r requirements.txt

   ```   ```



3. **Environment setup**3. **Environment setup**

   - Copy `.env.example` to `.env`   - Copy `.env.example` to `.env`

   - Configure your environment variables with actual values   - Configure your environment variables with actual values



4. **Start the development server**4. **Start the development server**

   ```powershell   ```powershell

   python run_backend.py   python run_backend.py

   ```   ```



### Access Points### Access Points

- **API Base URL**: http://localhost:8000- **API Base URL**: http://localhost:8000

- **API Documentation**: http://localhost:8000/docs- **API Documentation**: http://localhost:8000/docs

- **Health Check**: http://localhost:8000/health- **Health Check**: http://localhost:8000/health



## 📚 API Endpoints## 📚 API Endpoints



### Authentication### Authentication

- `POST /api/auth/login` - User login- `POST /api/auth/login` - User login

- `POST /api/auth/callback` - Handle authentication callback- `POST /api/auth/callback` - Handle authentication callback

- `POST /api/auth/logout` - User logout- `POST /api/auth/logout` - User logout

- `POST /api/auth/session-login` - Session-based login- `POST /api/auth/session-login` - Session-based login



### Admin Dashboard### Admin Dashboard

- `GET /api/admin/dashboard/stats` - Dashboard statistics- `GET /api/admin/dashboard/stats` - Dashboard statistics

- `GET /api/admin/audit-log` - Admin audit log- `GET /api/admin/audit-log` - Admin audit log

- `GET /api/admin/users` - Admin users management- `GET /api/admin/users` - Admin users management

- `POST /api/admin/users` - Create admin user- `POST /api/admin/users` - Create admin user

- `POST /api/contact/` - Submit contact form

### Contact Management- `PATCH /api/contact/messages/{id}/read` - Mark message as read

- `GET /api/contact/messages` - Get contact messages- `DELETE /api/contact/messages/{id}` - Delete message

- `POST /api/contact/` - Submit contact form### Running with VS Code Tasks

- `PATCH /api/contact/messages/{id}/read` - Mark message as readUse Terminal → Run Task…

- `DELETE /api/contact/messages/{id}` - Delete message- Start FastAPI Backend: launches the main API on http://localhost:8000

- Health Check Backend: verifies the backend `/health` endpoint

### Content Management- Start Admin API (8001): launches the admin-only API on http://localhost:8001

- `GET /api/content/about` - Get about page content- Health Check Admin API: verifies the admin API `/health` endpoint

- `PUT /api/content/about` - Update about content (admin)- `POST /api/blog/` - Create blog post (admin)

- `PUT /api/blog/{id}` - Update blog post (admin)

### Services Management- `DELETE /api/blog/{id}` - Delete blog post (admin)

- `GET /api/services/` - Get services

- `POST /api/services/` - Create service (admin)### Services Management

- `PUT /api/services/{id}` - Update service (admin)### Running Tests

- `DELETE /api/services/{id}` - Delete service (admin)```powershell

pytest

### Team Management```

- `GET /api/team/` - Get team members

- `POST /api/team/` - Create team member (admin)### Team Management

- `PUT /api/team/{id}` - Update team member (admin)- `GET /api/team/` - Get team members

- `DELETE /api/team/{id}` - Delete team member (admin)- `POST /api/team/` - Create team member (admin)

- `PUT /api/team/{id}` - Update team member (admin)

### Portfolio Management### Docker Deployment

- `GET /api/portfolio/` - Get portfolio projects```powershell

- `POST /api/portfolio/` - Create project (admin)docker-compose up -d

- `PUT /api/portfolio/{id}` - Update project (admin)```

- `DELETE /api/portfolio/{id}` - Delete project (admin)- `POST /api/portfolio/` - Create project (admin)

- `PUT /api/portfolio/{id}` - Update project (admin)

### FAQ Management- `DELETE /api/portfolio/{id}` - Delete project (admin)

- `GET /api/faq/` - Get FAQs

- `POST /api/faq/` - Create FAQ (admin)### FAQ Management

- `PUT /api/faq/{id}` - Update FAQ (admin)- `GET /api/faq/` - Get FAQs

- `DELETE /api/faq/{id}` - Delete FAQ (admin)### Manual Deployment

```powershell

### Testimonials Management# Install dependencies

- `GET /api/testimonials/` - Get testimonialspip install -r requirements.txt

- `POST /api/testimonials/` - Create testimonial (admin)```

- `PUT /api/testimonials/{id}` - Update testimonial (admin)- `GET /api/testimonials/` - Get testimonials

- `DELETE /api/testimonials/{id}` - Delete testimonial (admin)- `POST /api/testimonials/` - Create testimonial (admin)



## 🏗️ Project Structure## 📁 Folder structure (summary)

```

```backend/

backend/├─ app/

├── app/│  ├─ core/          # config, hosts/CORS, security helpers

│   ├── core/              # Core configuration and security│  ├─ middleware/    # rate limit + security middleware

│   │   ├── config.py      # Application configuration│  ├─ models/        # Pydantic models

│   │   ├── database.py    # Database connection setup│  ├─ routers/       # auth, admin, contact, content, services, team, portfolio, faq, testimonials

│   │   └── security.py    # Security utilities│  └─ services/      # email, utils

│   ├── middleware/        # Custom middleware├─ main.py           # mounts /api/*

│   │   ├── rate_limit.py  # Rate limiting middleware├─ run_backend.py    # dev launcher

│   │   └── security.py    # Security middleware├─ run_admin_api.py  # optional admin API on 8001

│   ├── models/           # Pydantic models├─ requirements.txt

│   │   ├── auth.py       # Authentication models└─ Dockerfile / docker-compose.yml

│   │   └── content.py    # Content models```

│   ├── routers/          # API route handlers- `PUT /api/testimonials/{id}` - Update testimonial (admin)

│   │   ├── admin.py      # Admin routes- `DELETE /api/testimonials/{id}` - Delete testimonial (admin)

│   │   ├── auth.py       # Authentication routes

│   │   ├── contact.py    # Contact form routes### Logo Management

│   │   ├── content.py    # Content management routes- `GET /api/logo/` - Get logos

│   │   ├── faq.py        # FAQ routes- `POST /api/logo/` - Create logo (admin)

│   │   ├── portfolio.py  # Portfolio routes- `PUT /api/logo/{id}` - Update logo (admin)

│   │   ├── services.py   # Services routes- `DELETE /api/logo/{id}` - Delete logo (admin)

│   │   ├── team.py       # Team routes

│   │   └── testimonials.py # Testimonials routes### Content Management

│   └── services/         # Business logic services- `GET /api/content/about` - Get about page content

│       └── email.py      # Email service- `PUT /api/content/about` - Update about content (admin)

├── data/                 # Data storage

│   └── blog-posts.json   # Blog posts data## 🔒 Security Features

├── main.py              # Main application entry point

├── main_admin.py        # Admin-only API (optional)- **JWT Authentication**: Secure token-based authentication

├── run_backend.py       # Development server launcher- **Rate Limiting**: Protection against brute force attacks

├── run_admin_api.py     # Admin API launcher- **CORS Protection**: Configurable cross-origin resource sharing

├── health_check.py      # Health check script- **Security Headers**: Comprehensive security headers

├── requirements.txt     # Python dependencies- **Admin Authorization**: Role-based access control

└── Dockerfile          # Docker configuration- **Audit Logging**: Complete admin action logging

```- **Input Validation**: Pydantic model validation

- **SQL Injection Protection**: Supabase client protection

## 🔒 Security Features

## 🏗️ Architecture

- **JWT Authentication**: Secure token-based authentication

- **Rate Limiting**: Protection against brute force attacks### Core Components

- **CORS Protection**: Configurable cross-origin resource sharing- **FastAPI**: High-performance web framework

- **Security Headers**: Comprehensive security headers- **Pydantic**: Data validation and serialization

- **Input Validation**: Pydantic model validation- **Supabase**: Database and authentication

- **Admin Authorization**: Role-based access control- **JWT**: Token-based authentication

- **Audit Logging**: Complete admin action logging- **Uvicorn**: ASGI server



## 🛠️ Development Tools### Middleware Stack

- **Security Middleware**: Security headers and protection

### VS Code Tasks- **Rate Limit Middleware**: Request rate limiting

Use `Terminal → Run Task...` to access pre-configured tasks:- **CORS Middleware**: Cross-origin resource sharing

- **Start FastAPI Backend**: Launch main API on http://localhost:8000- **Trusted Host Middleware**: Host validation

- **Health Check Backend**: Verify backend health endpoint

- **Start Admin API (8001)**: Launch admin-only API on http://localhost:8001### Database Integration

- **Health Check Admin API**: Verify admin API health endpoint- **Supabase Client**: Direct database integration

- **File-based Blog**: Maintains compatibility with existing blog system

### Running Tests- **Audit Logging**: Complete admin action tracking

```powershell- **Error Handling**: Comprehensive error management

pytest

```## 🔄 Migration from Next.js



### Docker Deployment### Frontend Changes Required

```powershell

docker-compose up -d1. **Update API Base URL**:

``````typescript

// Before (Next.js)

## 🌐 Environment Variablesconst API_BASE = '/api'



Create a `.env` file with the following variables:// After (FastAPI)

const API_BASE = 'http://localhost:8000/api'

```env```

# Required

NEXT_PUBLIC_SUPABASE_URL=your_supabase_url2. **Update Authentication Headers**:

NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key```typescript

JWT_SECRET_KEY=your_jwt_secret// Add Authorization header to all admin requests

const headers = {

# Optional  'Authorization': `Bearer ${token}`,

SUPABASE_SERVICE_ROLE_KEY=your_service_key  'Content-Type': 'application/json'

RECAPTCHA_SECRET_KEY=your_recaptcha_secret}

ALLOWED_ADMIN_EMAIL=admin@example.com```

REDIS_URL=redis://localhost:6379

ENVIRONMENT=development3. **Update Error Handling**:

DEBUG=True```typescript

```// FastAPI returns consistent error format

{

## 📈 Performance Features  "detail": "Error message"

}

- **High Performance**: Built on FastAPI for maximum speed```

- **Concurrent Processing**: Handles multiple requests efficiently

- **Optimized Memory Usage**: Lower memory footprint### Compatibility Features

- **Auto Documentation**: Built-in OpenAPI/Swagger documentation- **Same API Structure**: Maintains existing endpoint patterns

- **Health Monitoring**: Built-in health checks and metrics- **Same Response Format**: Compatible response structures

- **Same Authentication Flow**: Magic link + JWT tokens

## 🚀 Deployment- **Same Database Schema**: Uses existing Supabase tables

- **File-based Blog**: Maintains existing blog post storage

### Production Deployment

```bash## 🚀 Deployment

# Set environment variables

export ENVIRONMENT=production### Docker Deployment

export DEBUG=False```bash

docker-compose up -d

# Start with Gunicorn```

gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

```### Manual Deployment

```bash

### Docker Deployment# Install dependencies

```bashpip install -r requirements.txt

docker-compose up -d

```# Set environment variables

export ENVIRONMENT=production

## 🆘 Troubleshootingexport DEBUG=False



### Common Issues# Start with Gunicorn

gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

1. **Port Already in Use**```

   ```powershell

   # Windows: Find and kill process using port 8000### Environment Variables

   netstat -ano | findstr :8000```env

   taskkill /PID <PID> /F# Required

   ```NEXT_PUBLIC_SUPABASE_URL=your_supabase_url

NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

2. **Environment Variables Missing**JWT_SECRET_KEY=your_jwt_secret

   ```powershell

   # Check if .env file exists and contains required variables# Optional

   Get-Content .envSUPABASE_SERVICE_ROLE_KEY=your_service_key

   ```RECAPTCHA_SECRET_KEY=your_recaptcha_secret

ALLOWED_ADMIN_EMAIL=admin@example.com

3. **Database Connection Issues**REDIS_URL=redis://localhost:6379

   - Verify Supabase URL and keys in `.env````

   - Check network connectivity to Supabase

## 📈 Performance Monitoring

4. **Dependencies Issues**

   ```powershell- **Built-in Metrics**: Request timing and performance headers

   # Reinstall requirements- **Health Checks**: `/health` endpoint for monitoring

   pip install -r requirements.txt --force-reinstall- **Structured Logging**: Comprehensive application logging

   ```- **Error Tracking**: Detailed error logging and reporting



## 📞 Support## 🔧 Development



For issues, bugs, or feature requests, please contact the development team or check the application logs for detailed error information.### Running in Development

```bash

---python start.py

```

**CortejTech FastAPI Backend v1.0** - Built with ❤️ for high performance and reliability.
### Running with VS Code Tasks
If you're using this repository in VS Code, you can use the pre-configured tasks to run the servers with the workspace virtual environment:

- Start FastAPI Backend: launches the main API on http://localhost:8000
- Health Check Backend: verifies the backend `/health` endpoint
- Start Admin API (8001): launches the admin-only API on http://localhost:8001
- Health Check Admin API: verifies the admin API `/health` endpoint

You can find these under Terminal → Run Task…

### Running Tests
```bash
pytest
```

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

## 🆘 Troubleshooting

### Common Issues

1. **Port Already in Use**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

2. **Environment Variables**:
```bash
# Check if .env file exists and has correct values
cat .env
```

3. **Database Connection**:
```bash
# Test Supabase connection
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

4. **Dependencies**:
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

---

## 🎯 Next Steps

1. **Update Frontend**: Change API calls to use FastAPI backend
2. **Test All Endpoints**: Verify all functionality works correctly
3. **Performance Testing**: Compare response times with Next.js
4. **Deploy to Production**: Use Docker or manual deployment
5. **Monitor Performance**: Track improvements and optimize further

**FastAPI Backend** - High-performance replacement for Next.js API routes
For support or issues, check the logs or contact the development team.