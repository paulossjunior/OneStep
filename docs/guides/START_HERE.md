# 🚀 START HERE - OneStep Frontend

## ⚡ Início Rápido (3 passos)

### 1️⃣ Instalar Dependências

```bash
cd frontend
npm install
```

### 2️⃣ Iniciar Aplicação

```bash
npm run dev:mock
```

Aguarde ver os logs:
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

### 3️⃣ Abrir e Fazer Login

**URL**: http://localhost:5173/login

**Credenciais**:
- Username: `admin`
- Password: `admin123`

## ✅ Pronto!

Você está dentro do sistema. Agora pode:
- Ver lista de iniciativas
- Buscar e filtrar
- Exportar para CSV
- Mudar tema (light/dark)
- Mudar idioma (en/pt-BR)

## 🧪 Testar API (Opcional)

```bash
cd frontend
./test-api.sh
```

Todos os testes devem passar ✅

## ❌ Problemas?

### Erro: "No response from server"

**Solução rápida**:
```bash
# Parar tudo (Ctrl+C)
cd frontend
npm install
npm run dev:mock
```

Ver mais: **QUICK_FIX.md**

### Erro: "require is not defined"

Já corrigido! O arquivo agora é `auth-server.cjs`

### Porta em uso

```bash
# Matar processos
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Reiniciar
npm run dev:mock
```

## 📚 Documentação

### Essencial
- **LOGIN_CREDENTIALS.md** - Todas as credenciais
- **QUICK_FIX.md** - Solução rápida de problemas
- **TROUBLESHOOTING.md** - Guia completo

### Técnica
- **mock-api/AUTH_GUIDE.md** - Guia de autenticação
- **SERVICES_AND_MOCK_API.md** - Arquitetura
- **IMPLEMENTATION_STATUS.md** - Status do projeto

### Testes
- **TEST_INSTRUCTIONS.md** - Como testar
- **test-api.sh** - Script de teste

## 🎯 O Que Testar

### Lista de Iniciativas
1. Clicar em "Initiatives" no menu
2. Ver 5 iniciativas de exemplo
3. Buscar por "Programa"
4. Filtrar por tipo "Program"
5. Ordenar por nome
6. Exportar para CSV

### Navegação
1. Menu lateral responsivo
2. Tema light/dark (ícone sol/lua)
3. Idioma en/pt-BR (ícone tradução)

### Autenticação
1. Logout (avatar > Logout)
2. Login novamente
3. Token renovado automaticamente

## 👥 Outros Usuários

### Maria Silva (Staff)
```
Username: maria.silva
Password: senha123
```
Pode ver, criar e editar (não deletar)

### João Santos (Regular)
```
Username: joao.santos
Password: senha123
```
Pode apenas visualizar

## 🔧 Comandos Úteis

```bash
# Apenas Mock API
npm run mock-api

# Apenas Frontend
npm run dev

# Ambos juntos
npm run dev:mock

# Testar API
./test-api.sh

# Limpar cache
rm -rf node_modules/.vite
```

## 📊 Status do Projeto

- **Phase 1**: ✅ 95% Completo (Foundation)
- **Phase 2**: 🚧 50% Completo (Initiatives)
- **Overall**: ~22% Completo

### Implementado
- ✅ Autenticação JWT
- ✅ Lista de iniciativas
- ✅ Busca e filtros
- ✅ Export CSV
- ✅ Tema e idioma
- ✅ Mock API completo

### Em Desenvolvimento
- 🚧 Criar iniciativa
- 🚧 Editar iniciativa
- 🚧 Detalhes da iniciativa
- 🚧 Gerenciar equipe
- 🚧 Hierarquia
- 🚧 Import CSV/ZIP

## 🎓 Arquitetura

```
View (InitiativeListView)
  ↓
Handler (useDeleteInitiativeHandler)
  ↓
Service (initiativeService)
  ↓
API Client (initiativesApi)
  ↓
Mock Backend (auth-server.cjs)
```

## 💡 Dicas

1. **Use admin/admin123** para acesso completo
2. **Mantenha o terminal aberto** para ver logs
3. **Use DevTools (F12)** para debug
4. **Teste a API** com curl ou test-api.sh
5. **Leia TROUBLESHOOTING.md** se tiver problemas

## 🎉 Próximos Passos

Após testar:
1. Explorar o código em `frontend/src/`
2. Ver documentação em `documentation/`
3. Completar Phase 2 (views e componentes)
4. Implementar Phase 3 (Scholarships)

---

**Tudo pronto para começar!** 🚀

Se tiver dúvidas, consulte a documentação ou os arquivos de troubleshooting.
