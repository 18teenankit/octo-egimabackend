# FastAPI Backend - CORS & Host Configuration Guide

## Quick Fix Summary

Your backend has been updated to handle:
✅ Dynamic port configuration (uses Render's `$PORT` or falls back to 8000)
✅ Proper CORS setup for both local and production environments  
✅ Host header validation that works with Render domains
✅ Environment-based configuration

## Local Development Setup

1. **Copy the local environment file:**
   ```bash
   cp .env.local .env
   ```

2. **Update your Supabase credentials in `.env`:**
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

3. **Start the development server:**
   ```bash
   python start.py
   ```
   or
   ```bash
   python main.py
   ```

## Render Production Setup

### Environment Variables to Set in Render Dashboard:

**Required:**
```
ENVIRONMENT=production
DEBUG=false
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET_KEY=your-strong-32-char-secret-key
ADMIN_SESSION_SECRET=your-strong-32-char-admin-secret
```

**CORS Configuration:**
```
ALLOWED_ORIGINS=https://your-frontend-domain.com,https://your-admin-dashboard.com,http://localhost:3000,http://localhost:3001
ALLOWED_HOSTS=cortejtech-backend.onrender.com,your-frontend-domain.com,localhost,127.0.0.1
```

**Optional:**
```
RESEND_API_KEY=your-resend-api-key
ALLOWED_ADMIN_EMAILS=giriankit595@outlook.com,info@cortejtech.com
ADMIN_BASE_URL=https://your-admin-dashboard.com
```

### Build & Deploy Settings in Render:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** Already configured in `Procfile` → `python run_production.py`
- **Environment:** Python 3.12+

## Testing the Fix

### 1. Local Testing:
```bash
# Start the server
python start.py

# Test from browser/frontend
curl http://localhost:8000/health
```

### 2. Production Testing:
```bash
# Test your Render deployment
curl https://cortejtech-backend.onrender.com/health

# Test CORS (replace with your frontend domain)
curl -H "Origin: https://your-frontend-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://cortejtech-backend.onrender.com/api/content
```

## Frontend Configuration

Update your frontend to use the correct API endpoints:

**Local Development:**
```javascript
const API_BASE_URL = 'http://localhost:8000'
```

**Production:**
```javascript
const API_BASE_URL = 'https://cortejtech-backend.onrender.com'
```

## Common Issues & Solutions

### 1. "Invalid Host Header" Error
- **Cause:** TrustedHostMiddleware blocking requests
- **Solution:** Already fixed by adding your Render domain to `ALLOWED_HOSTS`

### 2. CORS Preflight Failures
- **Cause:** Missing or incorrect CORS origins
- **Solution:** Add your frontend domains to `ALLOWED_ORIGINS`

### 3. Port Binding Issues on Render
- **Cause:** Not using Render's `$PORT` environment variable
- **Solution:** Already fixed - server auto-detects port

### 4. Frontend Can't Connect
- **Cause:** Incorrect API base URL
- **Solution:** Use `https://cortejtech-backend.onrender.com` in production

## Security Notes

🔒 **Important for Production:**
- Use strong, random secrets for `JWT_SECRET_KEY` and `ADMIN_SESSION_SECRET` (32+ characters)
- Set `DEBUG=false` in production
- Only include your actual frontend domains in `ALLOWED_ORIGINS`
- Never commit your `.env` file to version control

## Files Modified

- ✅ `main.py` - Updated CORS and host middleware
- ✅ `app/core/config.py` - Added Render domains to defaults
- ✅ `start.py` - Improved environment validation
- ✅ `run_production.py` - Added port configuration logging
- ✅ Created `.env.example` and `.env.local` for reference

Your FastAPI backend is now ready for both local development and Render deployment! 🚀