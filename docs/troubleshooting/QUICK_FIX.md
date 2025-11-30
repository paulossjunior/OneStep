# ⚡ Quick Fix - "No response from server"

## 🔧 Solução Rápida

### Passo 1: Parar tudo
Pressione `Ctrl+C` no terminal onde está rodando `npm run dev:mock`

### Passo 2: Verificar configuração
Arquivo: `frontend/.env.development`

Deve ter:
```env
VITE_API_URL=http://localhost:8000/api
```

### Passo 3: Reinstalar dependências
```bash
cd frontend
npm install
```

### Passo 4: Reiniciar
```bash
npm run dev:mock
```

### Passo 5: Aguardar logs
Você deve ver:
```
[0] 🚀 Mock API Server is running!
[0] 📍 Endpoints:
[0]    - Auth: http://localhost:8000/auth/login
[0]    - API:  http://localhost:8000/api/initiatives
[1] VITE v5.x.x  ready in xxx ms
[1] ➜  Local:   http://localhost:5173/
```

### Passo 6: Testar API
Em outro terminal:
```bash
cd frontend
./test-api.sh
```

Todos os testes devem passar ✅

### Passo 7: Abrir navegador
http://localhost:5173/login

### Passo 8: Login
- Username: `admin`
- Password: `admin123`

## 🎯 Se ainda não funcionar

### Opção 1: Limpar tudo e recomeçar
```bash
# Parar tudo (Ctrl+C)
cd frontend

# Matar processos
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null

# Limpar cache
rm -rf node_modules/.vite

# Reinstalar
npm install

# Reiniciar
npm run dev:mock
```

### Opção 2: Verificar manualmente

```bash
# Terminal 1: Apenas Mock API
cd frontend
node mock-api/auth-server.cjs

# Terminal 2: Apenas Frontend
cd frontend
npm run dev

# Terminal 3: Testar
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## 📋 Checklist

- [ ] Node.js instalado
- [ ] `npm install` executado
- [ ] Porta 8000 livre
- [ ] Porta 5173 livre
- [ ] `.env.development` correto
- [ ] `jsonwebtoken` instalado
- [ ] Mock API iniciado
- [ ] Frontend iniciado
- [ ] Logs aparecem no terminal

## 🆘 Ainda com erro?

Ver documentação completa: **TROUBLESHOOTING.md**

---

**Dica**: 90% dos problemas são resolvidos reiniciando o mock API!
