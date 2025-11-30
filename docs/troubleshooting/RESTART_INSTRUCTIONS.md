# 🔄 Instruções para Reiniciar

## ✅ Correção Aplicada

O auth-server.cjs foi atualizado para aceitar URLs com e sem barra final (`/`).

Agora funciona:
- ✅ `/auth/login` 
- ✅ `/auth/login/`
- ✅ `/auth/token/refresh`
- ✅ `/auth/token/refresh/`
- ✅ `/auth/me`
- ✅ `/auth/me/`
- ✅ `/auth/logout`
- ✅ `/auth/logout/`

## 🔄 Como Reiniciar

### Passo 1: Parar o Servidor
No terminal onde está rodando `npm run dev:mock`, pressione:
```
Ctrl+C
```

### Passo 2: Reiniciar
```bash
npm run dev:mock
```

### Passo 3: Aguardar Logs
Você deve ver:
```
[0] 🚀 Mock API Server is running!
[0] 📍 Endpoints:
[0]    - Auth: http://localhost:8000/auth/login
[0]    - API:  http://localhost:8000/api/initiatives
[0] 👤 Test Users:
[0]    - Username: admin     | Password: admin123
[1] VITE v5.x.x  ready in xxx ms
[1] ➜  Local:   http://localhost:5173/
```

### Passo 4: Limpar Cache do Navegador
1. Abrir DevTools (F12)
2. Ir para Application > Local Storage
3. Deletar todos os itens
4. Recarregar página (F5)

### Passo 5: Fazer Login
1. Ir para http://localhost:5173/login
2. Username: `admin`
3. Password: `admin123`
4. Clicar "Sign In"

## ✅ Deve Funcionar Agora!

O login deve:
1. ✅ Aceitar as credenciais
2. ✅ Retornar tokens
3. ✅ Armazenar no localStorage
4. ✅ Redirecionar para dashboard

## 🧪 Testar API Manualmente

```bash
# Testar login
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Deve retornar:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    ...
  }
}
```

## ❌ Ainda com Erro?

### Verificar Console do Navegador
1. Abrir DevTools (F12)
2. Ir para Console
3. Ver mensagens de erro
4. Copiar erro completo

### Verificar Network Tab
1. DevTools > Network
2. Fazer login
3. Ver requisição para `/auth/login/`
4. Ver resposta

### Verificar Logs do Servidor
No terminal, ver se há erros quando faz login.

## 📝 Erros Comuns

### "No response from server"
- Mock API não está rodando
- Porta 8000 não está acessível
- Firewall bloqueando

**Solução**: Reiniciar mock API

### "Invalid username or password"
- Credenciais erradas
- Banco de dados não carregou

**Solução**: Verificar `mock-api/db.json` tem usuários

### "Token invalid"
- Token malformado
- Secret key diferente

**Solução**: Limpar localStorage e fazer login novamente

### CORS Error
- Headers CORS não configurados

**Solução**: Verificar auth-server.cjs tem headers CORS

## 🎯 Checklist Final

Antes de testar:
- [ ] Mock API reiniciado
- [ ] Frontend reiniciado
- [ ] localStorage limpo
- [ ] Navegador recarregado
- [ ] Usando credenciais corretas
- [ ] Console sem erros
- [ ] Network tab mostra requisições

## 💡 Dica

Se ainda não funcionar, tente:

```bash
# Parar tudo
Ctrl+C

# Limpar completamente
cd frontend
rm -rf node_modules/.vite

# Reinstalar
npm install

# Reiniciar
npm run dev:mock

# Limpar localStorage no navegador
# DevTools > Application > Local Storage > Clear All

# Tentar login novamente
```

---

**Após reiniciar, o login deve funcionar!** 🎉
