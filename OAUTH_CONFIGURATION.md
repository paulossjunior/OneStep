# OAuth Configuration Guide - OneStep

## 🔐 OAuth2 com Django OAuth Toolkit

O OneStep usa Django OAuth Toolkit para autenticação OAuth2 com grant type **Resource Owner Password Credentials** (ROPC).

## 📋 Configuração Automática

### Backend

O backend cria automaticamente uma aplicação OAuth quando o container inicia:

```bash
docker-compose -f docker-compose.dev.yml up
```

Você verá nos logs:
```
🔐 Creating OAuth Application...
✅ OAuth Application "OneStep Frontend" created successfully!

📋 OAuth Application Details:
   Name: OneStep Frontend
   Client ID: onestep-frontend-client
   Client Secret: onestep-frontend-secret-dev
   Grant Type: Resource owner password-based
```

### Frontend

O frontend já está configurado para usar OAuth. As variáveis são passadas automaticamente via docker-compose.

## 🔧 Variáveis de Ambiente

### Backend (`docker-compose.dev.yml`)

```yaml
environment:
  - OAUTH_CLIENT_ID=onestep-frontend-client
  - OAUTH_CLIENT_SECRET=onestep-frontend-secret-dev
  - OAUTH_REDIRECT_URIS=http://localhost:5173/auth/callback http://localhost:5173
```

### Frontend (`docker-compose.dev.yml`)

```yaml
environment:
  - VITE_OAUTH_CLIENT_ID=onestep-frontend-client
  - VITE_OAUTH_CLIENT_SECRET=onestep-frontend-secret-dev
```

### Frontend Local (`.env.development`)

```env
VITE_OAUTH_CLIENT_ID=onestep-frontend-client
VITE_OAUTH_CLIENT_SECRET=onestep-frontend-secret-dev
```

## 🔄 Fluxo de Autenticação

### 1. Login

```typescript
// Frontend envia
POST /api/o/token/
Content-Type: multipart/form-data

grant_type=password
client_id=onestep-frontend-client
username=admin
password=admin123
```

### 2. Resposta

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 36000,
  "scope": "read write"
}
```

### 3. Uso do Token

```typescript
// Frontend adiciona em todas as requisições
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 4. Refresh Token

```typescript
// Quando access_token expira
POST /api/o/token/
Content-Type: multipart/form-data

grant_type=refresh_token
client_id=onestep-frontend-client
refresh_token=eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 📝 Código Frontend

### Auth Store (`auth.store.ts`)

```typescript
async function login(credentials: LoginCredentials): Promise<void> {
  const formData = new FormData();
  formData.append('grant_type', 'password');
  formData.append('client_id', import.meta.env.VITE_OAUTH_CLIENT_ID);
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await apiClient.post('/o/token/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  const { access_token, refresh_token } = response.data;
  
  // Store tokens
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
}
```

### API Client (`client.ts`)

```typescript
// Request interceptor - Add token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - Refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      
      const formData = new FormData();
      formData.append('grant_type', 'refresh_token');
      formData.append('client_id', import.meta.env.VITE_OAUTH_CLIENT_ID);
      formData.append('refresh_token', refreshToken);
      
      const response = await axios.post('/api/o/token/', formData);
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      
      // Retry original request
      error.config.headers.Authorization = `Bearer ${access_token}`;
      return apiClient(error.config);
    }
    return Promise.reject(error);
  }
);
```

## 🧪 Testar OAuth

### 1. Verificar Aplicação OAuth

```bash
# Entrar no container
docker-compose -f docker-compose.dev.yml exec backend bash

# Django shell
python manage.py shell

# Verificar aplicação
from oauth2_provider.models import Application
app = Application.objects.get(client_id='onestep-frontend-client')
print(f"Name: {app.name}")
print(f"Client ID: {app.client_id}")
print(f"Client Secret: {app.client_secret}")
print(f"Grant Type: {app.authorization_grant_type}")
```

### 2. Testar Login via cURL

```bash
curl -X POST http://localhost:8000/api/o/token/ \
  -F "grant_type=password" \
  -F "client_id=onestep-frontend-client" \
  -F "username=admin" \
  -F "password=admin123"
```

Deve retornar:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 36000,
  "scope": "read write"
}
```

### 3. Testar API com Token

```bash
# Salvar token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Fazer requisição
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/initiatives/
```

### 4. Testar Refresh Token

```bash
curl -X POST http://localhost:8000/api/o/token/ \
  -F "grant_type=refresh_token" \
  -F "client_id=onestep-frontend-client" \
  -F "refresh_token=REFRESH_TOKEN_AQUI"
```

## 🔐 Segurança

### Desenvolvimento

```env
OAUTH_CLIENT_SECRET=onestep-frontend-secret-dev
```

### Produção

```env
# Gerar secret forte
OAUTH_CLIENT_SECRET=$(openssl rand -base64 32)
```

**IMPORTANTE**: 
- ⚠️ Nunca commitar secrets de produção
- ⚠️ Usar HTTPS em produção
- ⚠️ Configurar CORS corretamente
- ⚠️ Definir scopes apropriados

## 📊 Endpoints OAuth

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/o/token/` | POST | Obter token (login/refresh) |
| `/api/o/revoke_token/` | POST | Revogar token |
| `/api/o/introspect/` | POST | Verificar token |
| `/api/o/authorize/` | GET | Autorização (não usado em ROPC) |

## 🔧 Configuração Avançada

### Alterar Grant Type

Se quiser usar Authorization Code ao invés de Password:

```python
# backend/create_oauth_application.py
authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE
```

### Adicionar Scopes

```python
# backend/onestep/settings.py
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'initiatives': 'Access initiatives',
        'scholarships': 'Access scholarships',
    }
}
```

### Token Expiration

```python
# backend/onestep/settings.py
OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,  # 10 horas
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400,  # 24 horas
}
```

## 🆘 Troubleshooting

### Erro: "Invalid client_id"

```bash
# Verificar se aplicação existe
docker-compose -f docker-compose.dev.yml exec backend \
  python manage.py shell -c "from oauth2_provider.models import Application; print(Application.objects.all())"
```

### Erro: "Invalid credentials"

- Verificar username/password
- Verificar se superuser existe
- Verificar logs do backend

### Token não funciona

```bash
# Verificar token
curl -X POST http://localhost:8000/api/o/introspect/ \
  -F "token=SEU_TOKEN_AQUI" \
  -F "client_id=onestep-frontend-client"
```

## 📚 Referências

- [Django OAuth Toolkit Docs](https://django-oauth-toolkit.readthedocs.io/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [Resource Owner Password Credentials](https://tools.ietf.org/html/rfc6749#section-4.3)

---

**Última atualização**: 30 de Novembro de 2024
