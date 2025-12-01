# OAuth Setup Complete ✅

## 📋 OAuth Application Details

### Backend Configuration

**Application Name**: OneStep Frontend  
**Client ID**: `onestep-frontend-client`  
**Client Secret**: `onestep-frontend-secret-dev`  
**Grant Type**: Resource Owner Password Credentials (ROPC)  
**Redirect URIs**: 
- `http://localhost:5173/auth/callback`
- `http://localhost:5173`

### Token Endpoint

```
POST http://localhost:8000/api/o/token/
```

## 🔧 Frontend Environment Variables

### Development (`.env.development` and `.env.local`)

```env
VITE_API_URL=http://localhost:8000
VITE_OAUTH_CLIENT_ID=onestep-frontend-client
VITE_OAUTH_CLIENT_SECRET=onestep-frontend-secret-dev
```

### Production (`.env.production`)

```env
VITE_API_URL=https://api.onestep.com
VITE_OAUTH_CLIENT_ID=onestep-frontend-client-prod
VITE_OAUTH_CLIENT_SECRET=CHANGE_THIS_IN_PRODUCTION
```

## 🚀 How to Use

### 1. Start Docker Services

```bash
docker-compose -f docker-compose.dev.yml up -d
```

The OAuth application is created automatically on backend startup.

### 2. Verify OAuth Application

```bash
# Check backend logs
docker-compose -f docker-compose.dev.yml logs backend | grep "OAuth"
```

You should see:
```
🔐 Creating OAuth Application...
✅ OAuth Application "OneStep Frontend" created successfully!
📋 OAuth Application Details:
   Name: OneStep Frontend
   Client ID: onestep-frontend-client
   Client Secret: onestep-frontend-secret-dev
```

### 3. Test OAuth Login

```bash
curl -X POST http://localhost:8000/api/o/token/ \
  -F "grant_type=password" \
  -F "client_id=onestep-frontend-client" \
  -F "username=admin" \
  -F "password=admin123"
```

Expected response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 36000,
  "scope": "read write"
}
```

### 4. Use Token in API Requests

```bash
TOKEN="your_access_token_here"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/initiatives/
```

## 🔐 Frontend Login Flow

### 1. User enters credentials

```typescript
// LoginView.vue
const credentials = {
  username: 'admin',
  password: 'admin123'
}
```

### 2. Frontend sends OAuth request

```typescript
// auth.store.ts
const formData = new FormData();
formData.append('grant_type', 'password');
formData.append('client_id', import.meta.env.VITE_OAUTH_CLIENT_ID);
formData.append('username', credentials.username);
formData.append('password', credentials.password);

const response = await apiClient.post('/o/token/', formData);
```

### 3. Backend validates and returns tokens

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 36000
}
```

### 4. Frontend stores tokens

```typescript
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

### 5. Frontend adds token to all requests

```typescript
// client.ts interceptor
config.headers.Authorization = `Bearer ${access_token}`;
```

## 📁 Files Updated

### Backend
- ✅ `backend/create_oauth_application.py` - Script to create OAuth app
- ✅ `docker-compose.dev.yml` - OAuth environment variables

### Frontend
- ✅ `frontend/.env.development` - Development OAuth config
- ✅ `frontend/.env.local` - Local development OAuth config
- ✅ `frontend/.env.production` - Production OAuth config (template)
- ✅ `frontend/src/core/stores/auth.store.ts` - Already using OAuth

### Documentation
- ✅ `OAUTH_CONFIGURATION.md` - Complete OAuth guide
- ✅ `OAUTH_SETUP_COMPLETE.md` - This file

## ✅ Verification Checklist

- [x] OAuth application created in Django
- [x] Client ID configured: `onestep-frontend-client`
- [x] Client Secret configured: `onestep-frontend-secret-dev`
- [x] Frontend `.env.development` updated
- [x] Frontend `.env.local` created
- [x] Frontend `.env.production` template created
- [x] Docker Compose configured with OAuth variables
- [x] Backend creates OAuth app automatically on startup
- [x] Frontend auth.store.ts already using OAuth

## 🧪 Test Credentials

### Admin User
- **Username**: `admin`
- **Password**: `admin123`

### OAuth Client
- **Client ID**: `onestep-frontend-client`
- **Client Secret**: `onestep-frontend-secret-dev`

## 🔒 Security Notes

### Development
- Using simple secrets for development
- Secrets are in version control (OK for dev)
- HTTP is acceptable for localhost

### Production
⚠️ **IMPORTANT**: Before deploying to production:

1. **Generate secure secrets**:
   ```bash
   openssl rand -base64 32
   ```

2. **Update production secrets**:
   - Backend: `OAUTH_CLIENT_SECRET` in production .env
   - Frontend: `VITE_OAUTH_CLIENT_SECRET` in production .env

3. **Use HTTPS**:
   - All OAuth traffic must be over HTTPS
   - Configure SSL/TLS certificates

4. **Secure storage**:
   - Use environment variables
   - Never commit production secrets
   - Use secret management tools (AWS Secrets Manager, etc.)

5. **Configure CORS**:
   - Restrict to production domains only
   - Remove localhost from ALLOWED_HOSTS

## 📚 Additional Resources

- [OAuth Configuration Guide](./OAUTH_CONFIGURATION.md) - Detailed OAuth setup
- [Django OAuth Toolkit Docs](https://django-oauth-toolkit.readthedocs.io/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)

## 🆘 Troubleshooting

### "Invalid client_id"
- Verify OAuth application exists in Django admin
- Check client_id matches in frontend and backend

### "Invalid credentials"
- Verify username/password are correct
- Check superuser exists: `docker-compose exec backend python manage.py createsuperuser`

### Token not working
- Verify token is being sent in Authorization header
- Check token hasn't expired (default: 10 hours)
- Try refreshing token

### CORS errors
- Verify CORS_ALLOWED_ORIGINS includes frontend URL
- Check browser console for specific CORS error

---

**Status**: ✅ OAuth fully configured and ready to use!

**Last Updated**: November 30, 2024
