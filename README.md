# CortejTech FastAPI Backend

A high-performance FastAPI backend serving both the main website and admin dashboard for CortejTech. This backend provides comprehensive APIs for content management, user authentication, and administrative functionalities.

## 🏗️ Architecture Overview

This FastAPI application serves all endpoints under `/api/*` and provides:
- **Public APIs**: For the main website (portfolio, services, contact, etc.)
- **Admin APIs**: For the admin dashboard with authentication
- **Authentication**: JWT-based auth with Supabase integration
- **Database**: PostgreSQL via Supabase
- **Middleware**: Security, rate limiting, CORS, and trusted hosts

## 📁 Project Structure

```
backend/
├── app/                          # Main application package
│   ├── core/                     # Core configuration and utilities
│   │   ├── auth0_security.py     # Auth0 security utilities
│   │   ├── config.py             # Application settings and configuration
│   │   ├── database.py           # Database connection and initialization
│   │   ├── monkeypatches.py      # Early patches and fixes
│   │   └── security.py           # Security utilities and JWT handling
│   ├── middleware/               # Custom middleware
│   │   ├── rate_limit.py         # Rate limiting middleware
│   │   └── security.py           # Security headers middleware
│   ├── models/                   # Pydantic models and schemas
│   │   ├── auth.py               # Authentication models
│   │   ├── content.py            # Content management models
│   │   └── __init__.py
│   ├── routers/                  # API route handlers
│   │   ├── admin.py              # Admin dashboard APIs
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── contact.py            # Contact form handling
│   │   ├── content.py            # Content management
│   │   ├── faq.py                # FAQ management
│   │   ├── portfolio.py          # Portfolio management
│   │   ├── services.py           # Services management
│   │   ├── team.py               # Team member management
│   │   ├── testimonials.py       # Testimonials management
│   │   └── __init__.py
│   ├── services/                 # Business logic services
│   │   ├── email.py              # Email sending service
│   │   └── __pycache__/
│   ├── vendor/                   # Third-party integrations
│   └── __init__.py
├── data/                         # Static data files
│   └── blog-posts.json          # Blog posts data
├── __pycache__/                  # Python cache files
├── .env                          # Environment variables
├── .git/                         # Git repository
├── .gitignore                    # Git ignore rules
├── cleanup_team_table.py         # Database cleanup utility
├── deploy.sh                     # Deployment script
├── docker-compose.prod.yml       # Production Docker compose
├── docker-compose.yml            # Development Docker compose
├── Dockerfile                    # Docker container definition
├── health_check.py               # Health check for main API
├── health_check_admin.py         # Health check for admin API
├── main.py                       # Main FastAPI application (port 8000)
├── main_admin.py                 # Admin-only API (port 8001)
├── nginx.conf                    # Nginx configuration
├── Procfile                      # Heroku deployment config
├── requirements.txt              # Python dependencies
├── run_admin_api.py              # Admin API launcher
├── run_backend.py                # Main API launcher
├── run_production.py             # Production launcher
├── start.py                      # Generic starter script
└── __init__.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (via Supabase)
- Virtual environment (recommended)

### Setup

1. **Create and activate virtual environment:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

3. **Configure environment variables:**
Create a `.env` file in the backend directory:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
SUPABASE_JWT_SECRET=your_jwt_secret

# API Configuration
API_SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Email Configuration (optional)
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

4. **Run the development server:**
```powershell
python run_backend.py
```

The API will be available at `http://localhost:8000`

### Alternative: Admin-Only API
For admin-specific endpoints on a separate port:
```powershell
python run_admin_api.py
```
Available at `http://localhost:8001`

## 📡 API Endpoints

### Public Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /api/contact` - Contact form submission

### Content Management
- `GET /api/services` - List all services
- `GET /api/portfolio` - Portfolio items
- `GET /api/team` - Team members
- `GET /api/testimonials` - Client testimonials
- `GET /api/faq` - Frequently asked questions

### Authentication
- `POST /api/auth/session-login` - Admin session login
- `POST /api/auth/verify-token` - Token verification

### Admin APIs (Authentication Required)
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `POST /api/admin/services` - Create/update services
- `POST /api/admin/portfolio` - Manage portfolio items
- `POST /api/admin/team` - Team management
- `POST /api/admin/testimonials` - Testimonials management
- `GET /api/admin/contact/messages` - Contact messages

## 🔧 Configuration

### Settings (app/core/config.py)
The application uses Pydantic settings for configuration management:

```python
class Settings(BaseSettings):
    # Database
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_JWT_SECRET: str
    
    # Security
    API_SECRET_KEY: str
    CORS_ORIGINS: List[str]
    ALLOWED_HOSTS: List[str]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
```

### Middleware Stack
1. **SecurityMiddleware** - Security headers
2. **RateLimitMiddleware** - Request rate limiting
3. **CORSMiddleware** - Cross-origin resource sharing
4. **TrustedHostMiddleware** - Host validation

## 🗄️ Database

### Connection
- **Type**: PostgreSQL via Supabase
- **ORM**: Direct HTTP client via Supabase SDK
- **Connection**: Configured in `app/core/database.py`

### Tables
- `services` - Service offerings
- `portfolio` - Portfolio projects
- `team` - Team members
- `testimonials` - Client testimonials
- `faq` - Frequently asked questions
- `contact_messages` - Contact form submissions

## 🔐 Authentication & Security

### JWT Authentication
- Uses Supabase JWT tokens for user authentication
- Admin endpoints require valid JWT tokens
- Token verification in `app/core/security.py`

### Security Features
- **Rate Limiting**: Configurable request limits
- **CORS**: Properly configured for frontend origins
- **Security Headers**: Via SecurityMiddleware
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: Parameterized queries

## 📧 Email Service

### Configuration
Email notifications are handled via SMTP:
- Contact form submissions
- Admin notifications
- Error alerts (optional)

### Telegram Integration
Optional Telegram bot integration for notifications:
- Contact form alerts
- System notifications

## 🐳 Docker Deployment

### Development
```powershell
docker-compose up -d
```

### Production
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Docker
Set in `docker-compose.yml` or as environment variables:
- All `.env` variables
- `PORT` (default: 8000)
- `HOST` (default: 0.0.0.0)

## 🧪 Testing & Health Checks

### Health Checks
- **Main API**: `GET /health`
- **Admin API**: `GET /health` (port 8001)
- **Automated**: `python health_check.py`

### Manual Testing
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔄 Development Workflow

### Adding New Endpoints
1. Create router in `app/routers/`
2. Define Pydantic models in `app/models/`
3. Add business logic in `app/services/`
4. Register router in `main.py`

### Database Operations
1. Define models in `app/models/`
2. Use Supabase client in `app/core/database.py`
3. Handle operations in router functions

## 📊 Monitoring & Logging

### Logging
- Configured via Python logging module
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Output: Console (development), File (production)

### Performance
- Request timing via middleware
- Database query optimization
- Async/await throughout

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```powershell
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Environment Variables Not Loading**
   - Ensure `.env` file exists in backend directory
   - Check file permissions
   - Verify environment variable names

3. **Database Connection Issues**
   - Verify Supabase credentials
   - Check network connectivity
   - Validate environment variables

4. **CORS Errors**
   - Update `CORS_ORIGINS` in settings
   - Check frontend origin URLs
   - Verify OPTIONS handling

### Debug Mode
Run with debug logging:
```powershell
$env:LOG_LEVEL="DEBUG"
python run_backend.py
```

## 📈 Performance Optimization

### Recommendations
- Use async/await for I/O operations
- Implement caching for frequently accessed data
- Optimize database queries
- Use connection pooling
- Monitor memory usage

### Scaling
- Horizontal scaling with multiple instances
- Load balancing with nginx
- Database read replicas
- Redis for session storage

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write docstrings for modules and functions
4. Test all new endpoints
5. Update this README for significant changes

## 📄 License

This project is proprietary software for CortejTech.

---

For more information, see the main project README or contact the development team.