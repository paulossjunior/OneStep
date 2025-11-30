# 🔐 Guia de Autenticação - Mock API

## 👤 Usuários Disponíveis

### 1. Admin (Superusuário)
```
Username: admin
Password: admin123
```
**Permissões**: Todas (superusuário)

### 2. Maria Silva (Staff)
```
Username: maria.silva
Password: senha123
```
**Permissões**: 
- Ver iniciativas
- Adicionar iniciativas
- Editar iniciativas

### 3. João Santos (Usuário Regular)
```
Username: joao.santos
Password: senha123
```
**Permissões**: 
- Ver iniciativas

## 🚀 Como Usar

### 1. Iniciar Mock API com Autenticação

```bash
cd frontend
npm run dev:mock
```

O servidor iniciará em http://localhost:8000 com autenticação habilitada.

### 2. Login via API

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Resposta**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@onestep.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_staff": true,
    "is_superuser": true,
    "permissions": [...]
  }
}
```

### 3. Usar Token nas Requisições

```bash
# Listar iniciativas (GET não requer auth)
curl http://localhost:8000/initiatives

# Criar iniciativa (POST requer auth)
curl -X POST http://localhost:8000/initiatives \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "name": "Nova Iniciativa",
    "type": "PROJECT",
    ...
  }'
```

### 4. Refresh Token

```bash
curl -X POST http://localhost:8000/auth/token/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "SEU_REFRESH_TOKEN_AQUI"
  }'
```

**Resposta**:
```json
{
  "access": "NOVO_ACCESS_TOKEN"
}
```

### 5. Obter Usuário Atual

```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### 6. Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "SEU_REFRESH_TOKEN_AQUI"
  }'
```

## 🔑 Endpoints de Autenticação

### POST /auth/login
Login do usuário.

**Request**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200)**:
```json
{
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@onestep.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_staff": true,
    "is_superuser": true,
    "permissions": [...]
  }
}
```

**Response (401)**:
```json
{
  "detail": "Invalid username or password"
}
```

### POST /auth/token/refresh
Renovar access token.

**Request**:
```json
{
  "refresh": "JWT_REFRESH_TOKEN"
}
```

**Response (200)**:
```json
{
  "access": "NEW_JWT_ACCESS_TOKEN"
}
```

### GET /auth/me
Obter usuário atual.

**Headers**:
```
Authorization: Bearer JWT_ACCESS_TOKEN
```

**Response (200)**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@onestep.com",
  "first_name": "Admin",
  "last_name": "User",
  "is_staff": true,
  "is_superuser": true,
  "permissions": [...]
}
```

### POST /auth/logout
Logout (token é stateless, então apenas retorna sucesso).

**Response (200)**:
```json
{
  "detail": "Successfully logged out"
}
```

## 🛡️ Proteção de Rotas

### Rotas Públicas (sem autenticação)
- `GET /initiatives` - Listar iniciativas
- `GET /initiatives/:id` - Ver iniciativa
- `GET /people` - Listar pessoas
- `GET /organizational_groups` - Listar grupos
- Todas as rotas GET são públicas

### Rotas Protegidas (requerem autenticação)
- `POST /initiatives` - Criar iniciativa
- `PATCH /initiatives/:id` - Atualizar iniciativa
- `PUT /initiatives/:id` - Atualizar iniciativa
- `DELETE /initiatives/:id` - Deletar iniciativa
- Todas as rotas POST, PUT, PATCH, DELETE requerem token

## 🔧 Configuração do Frontend

O frontend já está configurado para usar autenticação. O `apiClient` em `src/core/api/client.ts` automaticamente:

1. Adiciona o token no header `Authorization`
2. Intercepta erros 401 (não autorizado)
3. Tenta renovar o token automaticamente
4. Redireciona para login se falhar

## 🧪 Testar Autenticação

### 1. Login no Frontend

1. Iniciar aplicação: `npm run dev:mock`
2. Abrir http://localhost:5173/login
3. Usar credenciais:
   - Username: `admin`
   - Password: `admin123`
4. Clicar em "Sign In"
5. Será redirecionado para dashboard

### 2. Testar Token Expirado

Os tokens expiram em 24 horas. Para testar expiração:

1. Fazer login
2. Esperar ou modificar `expiresIn` em `auth-server.js` para `'10s'`
3. Aguardar expiração
4. Fazer uma requisição
5. Token será renovado automaticamente

### 3. Testar Sem Autenticação

1. Abrir DevTools (F12)
2. Ir para Application > Local Storage
3. Deletar `access_token` e `refresh_token`
4. Tentar acessar página protegida
5. Será redirecionado para login

## 📝 Estrutura do Token JWT

### Access Token
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@onestep.com",
  "iat": 1701360000,
  "exp": 1701446400
}
```

### Refresh Token
```json
{
  "id": 1,
  "username": "admin",
  "type": "refresh",
  "iat": 1701360000,
  "exp": 1701446400
}
```

## 🔐 Secret Key

A chave secreta usada para assinar os tokens é:
```
onestep-secret-key-2024
```

**Nota**: Em produção, use uma chave forte e armazene em variável de ambiente!

## 🎯 Fluxo de Autenticação

```
1. Usuário faz login
   ↓
2. Backend valida credenciais
   ↓
3. Backend gera access_token e refresh_token
   ↓
4. Frontend armazena tokens no localStorage
   ↓
5. Frontend adiciona token em todas as requisições
   ↓
6. Backend valida token
   ↓
7. Se token expirado, frontend usa refresh_token
   ↓
8. Backend gera novo access_token
   ↓
9. Frontend atualiza token e refaz requisição
```

## 🚨 Troubleshooting

### Token inválido
- Verificar se token está sendo enviado no header
- Verificar formato: `Authorization: Bearer TOKEN`
- Verificar se token não expirou

### Login falha
- Verificar username e password
- Verificar se mock API está rodando
- Verificar console para erros

### Requisições sem autenticação
- Verificar se token está no localStorage
- Verificar se apiClient está adicionando header
- Verificar Network tab no DevTools

## 📚 Adicionar Novos Usuários

Edite `mock-api/db.json` e adicione na seção `users`:

```json
{
  "id": 4,
  "username": "novo.usuario",
  "password": "senha123",
  "email": "novo@example.com",
  "first_name": "Novo",
  "last_name": "Usuário",
  "is_staff": false,
  "is_superuser": false,
  "permissions": [
    "initiatives.view_initiative"
  ]
}
```

Reinicie o mock API para aplicar mudanças.

## 🎓 Permissões Disponíveis

```
initiatives.view_initiative
initiatives.add_initiative
initiatives.change_initiative
initiatives.delete_initiative

scholarships.view_scholarship
scholarships.add_scholarship
scholarships.change_scholarship
scholarships.delete_scholarship

people.view_person
people.add_person
people.change_person
people.delete_person
```

---

**Pronto para testar!** 🚀

Use `admin` / `admin123` para acesso completo.
