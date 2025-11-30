# 🔧 Troubleshooting - OneStep Frontend

## ❌ Erro: "No response from server. Please check your connection."

### Causa
O frontend não consegue se conectar ao mock API.

### Soluções

#### 1. Verificar se o Mock API está rodando

```bash
# Verificar se a porta 8000 está em uso
lsof -i :8000

# Ou testar diretamente
curl http://localhost:8000/initiatives
```

Se não retornar nada, o mock API não está rodando.

#### 2. Reiniciar o Mock API

```bash
# Parar o processo atual (Ctrl+C)
# Depois reiniciar
cd frontend
npm run dev:mock
```

#### 3. Verificar a URL da API

Arquivo: `frontend/.env.development`

Deve conter:
```env
VITE_API_URL=http://localhost:8000/api
```

#### 4. Limpar cache e reiniciar

```bash
# Parar tudo (Ctrl+C)
cd frontend

# Limpar cache do Vite
rm -rf node_modules/.vite

# Reiniciar
npm run dev:mock
```

#### 5. Verificar logs do terminal

Quando executar `npm run dev:mock`, você deve ver:

```
[0] 🚀 Mock API Server is running!
[0] 
[0] 📍 Endpoints:
[0]    - Auth: http://localhost:8000/auth/login
[0]    - API:  http://localhost:8000/api/initiatives
[0] 
[1] VITE v5.x.x  ready in xxx ms
[1] ➜  Local:   http://localhost:5173/
```

Se não ver isso, há um problema na inicialização.

## ❌ Erro: "Invalid username or password"

### Causa
Credenciais incorretas ou mock API não está usando o auth-server.

### Soluções

#### 1. Verificar credenciais

Usuários disponíveis:
- Username: `admin` | Password: `admin123`
- Username: `maria.silva` | Password: `senha123`
- Username: `joao.santos` | Password: `senha123`

#### 2. Testar login via curl

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Deve retornar tokens JWT.

#### 3. Verificar se auth-server está sendo usado

No `package.json`, o script deve ser:
```json
"mock-api": "node mock-api/auth-server.js"
```

Não deve ser:
```json
"mock-api": "json-server --watch mock-api/db.json ..."
```

## ❌ Erro: "Cannot find module 'jsonwebtoken'"

### Causa
Dependência não instalada.

### Solução

```bash
cd frontend
npm install jsonwebtoken --save-dev
```

## ❌ Porta 8000 já em uso

### Causa
Outro processo está usando a porta 8000.

### Soluções

#### 1. Encontrar e matar o processo

```bash
# Encontrar processo
lsof -i :8000

# Matar processo
kill -9 <PID>
```

#### 2. Usar outra porta

Editar `frontend/mock-api/auth-server.js`:
```javascript
const PORT = 8001; // Mudar de 8000 para 8001
```

E atualizar `.env.development`:
```env
VITE_API_URL=http://localhost:8001/api
```

## ❌ Frontend não carrega

### Causa
Vite não está rodando ou porta 5173 em uso.

### Soluções

#### 1. Verificar porta 5173

```bash
lsof -i :5173
```

#### 2. Limpar cache

```bash
cd frontend
rm -rf node_modules/.vite
npm run dev:mock
```

#### 3. Reinstalar dependências

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev:mock
```

## ❌ Erro CORS

### Causa
CORS não configurado corretamente.

### Solução

O auth-server.js já tem CORS configurado. Verificar se estas linhas estão presentes:

```javascript
server.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  // ...
});
```

## ❌ Token não funciona

### Causa
Token inválido ou expirado.

### Soluções

#### 1. Limpar localStorage

Abrir DevTools (F12) > Application > Local Storage > Deletar tudo

#### 2. Fazer login novamente

#### 3. Verificar se token está sendo enviado

DevTools > Network > Selecionar requisição > Headers

Deve ter:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## ❌ Iniciativas não aparecem

### Causa
API não está retornando dados ou erro de CORS.

### Soluções

#### 1. Testar API diretamente

```bash
curl http://localhost:8000/initiatives
```

Deve retornar JSON com iniciativas.

#### 2. Verificar console do navegador

Abrir DevTools (F12) > Console

Procurar por erros em vermelho.

#### 3. Verificar Network tab

DevTools > Network > Filtrar por "initiatives"

Ver se requisição foi feita e qual foi a resposta.

## 🔄 Passos para Reiniciar Tudo

Se nada funcionar, siga estes passos:

```bash
# 1. Parar tudo
# Pressionar Ctrl+C no terminal

# 2. Matar processos nas portas
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# 3. Limpar cache
cd frontend
rm -rf node_modules/.vite

# 4. Verificar dependências
npm install

# 5. Reiniciar
npm run dev:mock

# 6. Aguardar logs aparecerem

# 7. Abrir navegador
# http://localhost:5173/login

# 8. Login
# Username: admin
# Password: admin123
```

## 📝 Checklist de Verificação

Antes de reportar um problema, verificar:

- [ ] Node.js instalado (`node --version`)
- [ ] npm instalado (`npm --version`)
- [ ] Dependências instaladas (`npm install`)
- [ ] Mock API rodando (ver logs no terminal)
- [ ] Frontend rodando (ver logs no terminal)
- [ ] Porta 8000 livre
- [ ] Porta 5173 livre
- [ ] `.env.development` correto
- [ ] Console do navegador sem erros
- [ ] Network tab mostra requisições

## 🆘 Ainda com Problemas?

### 1. Verificar logs completos

Copiar todos os logs do terminal e verificar mensagens de erro.

### 2. Verificar console do navegador

DevTools (F12) > Console > Copiar erros

### 3. Verificar Network tab

DevTools > Network > Ver requisições falhadas

### 4. Testar API manualmente

```bash
# Testar auth
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Testar initiatives
curl http://localhost:8000/initiatives
```

### 5. Verificar arquivos

- `frontend/.env.development` - URL correta?
- `frontend/mock-api/auth-server.js` - Existe?
- `frontend/mock-api/db.json` - Tem usuários?
- `frontend/package.json` - Script correto?

## 📚 Documentação Útil

- **LOGIN_CREDENTIALS.md** - Credenciais de acesso
- **mock-api/AUTH_GUIDE.md** - Guia de autenticação
- **START_DEV_MOCK.md** - Como iniciar
- **TEST_INSTRUCTIONS.md** - Instruções de teste

---

**Dica**: Na maioria dos casos, reiniciar o mock API resolve o problema!
