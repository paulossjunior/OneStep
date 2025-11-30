# 🔐 Credenciais de Login - OneStep Frontend

## 👤 Usuários para Teste

### 1. Administrador (Recomendado)
```
Username: admin
Password: admin123
```
**Acesso**: Completo (superusuário)  
**Permissões**: Todas as operações

### 2. Maria Silva (Staff)
```
Username: maria.silva
Password: senha123
```
**Acesso**: Staff  
**Permissões**: Ver, Criar e Editar iniciativas

### 3. João Santos (Regular)
```
Username: joao.santos
Password: senha123
```
**Acesso**: Usuário regular  
**Permissões**: Apenas visualizar

## 🚀 Como Fazer Login

### 1. Iniciar Aplicação

```bash
cd frontend
npm run dev:mock
```

### 2. Acessar Login

Abrir navegador em: http://localhost:5173/login

### 3. Inserir Credenciais

- **Username**: `admin`
- **Password**: `admin123`

### 4. Clicar em "Sign In"

Você será redirecionado para o dashboard.

## 🎯 O Que Testar Após Login

### Com Admin (admin/admin123)
- ✅ Ver todas as iniciativas
- ✅ Criar nova iniciativa
- ✅ Editar iniciativas
- ✅ Deletar iniciativas
- ✅ Gerenciar membros
- ✅ Importar CSV/ZIP
- ✅ Todas as funcionalidades

### Com Maria Silva (maria.silva/senha123)
- ✅ Ver todas as iniciativas
- ✅ Criar nova iniciativa
- ✅ Editar iniciativas
- ❌ Deletar iniciativas (sem permissão)

### Com João Santos (joao.santos/senha123)
- ✅ Ver todas as iniciativas
- ❌ Criar iniciativas (sem permissão)
- ❌ Editar iniciativas (sem permissão)
- ❌ Deletar iniciativas (sem permissão)

## 🔧 Funcionalidades de Autenticação

### Implementado ✅
- Login com username/password
- JWT tokens (access + refresh)
- Token armazenado no localStorage
- Token enviado automaticamente em requisições
- Refresh automático quando token expira
- Logout
- Proteção de rotas
- Redirecionamento para login se não autenticado

### Fluxo de Autenticação
```
1. Usuário acessa /login
2. Insere username e password
3. Frontend envia para /auth/login
4. Backend valida e retorna tokens
5. Frontend armazena tokens
6. Frontend redireciona para dashboard
7. Todas as requisições incluem token
8. Se token expira, renova automaticamente
```

## 🧪 Testar Autenticação

### Teste 1: Login Bem-Sucedido
1. Ir para http://localhost:5173/login
2. Usar `admin` / `admin123`
3. Clicar "Sign In"
4. ✅ Deve redirecionar para dashboard

### Teste 2: Login com Credenciais Inválidas
1. Ir para http://localhost:5173/login
2. Usar `admin` / `senhaerrada`
3. Clicar "Sign In"
4. ❌ Deve mostrar erro "Invalid username or password"

### Teste 3: Acesso Sem Login
1. Limpar localStorage (DevTools > Application > Local Storage)
2. Tentar acessar http://localhost:5173/initiatives
3. ✅ Deve redirecionar para /login

### Teste 4: Logout
1. Fazer login
2. Clicar no avatar do usuário (canto superior direito)
3. Clicar em "Logout"
4. ✅ Deve redirecionar para /login

### Teste 5: Token Refresh
1. Fazer login
2. Esperar 24 horas (ou modificar expiração para 10s)
3. Fazer uma requisição
4. ✅ Token deve ser renovado automaticamente

## 🔐 Segurança

### Tokens JWT
- **Access Token**: Expira em 24 horas
- **Refresh Token**: Expira em 24 horas
- **Secret Key**: `onestep-secret-key-2024` (apenas para desenvolvimento!)

### Armazenamento
- Tokens armazenados no `localStorage`
- Senha **não** é armazenada
- Token é enviado no header `Authorization: Bearer TOKEN`

### Proteção
- Rotas protegidas requerem autenticação
- Token inválido = redirecionamento para login
- Token expirado = refresh automático
- Refresh falha = redirecionamento para login

## 📝 Adicionar Novos Usuários

Edite `frontend/mock-api/db.json` na seção `users`:

```json
{
  "id": 4,
  "username": "seu.usuario",
  "password": "sua.senha",
  "email": "email@example.com",
  "first_name": "Seu",
  "last_name": "Nome",
  "is_staff": false,
  "is_superuser": false,
  "permissions": [
    "initiatives.view_initiative"
  ]
}
```

Reinicie o mock API: `Ctrl+C` e `npm run dev:mock`

## 🚨 Troubleshooting

### "Invalid username or password"
- Verificar se username e password estão corretos
- Verificar se mock API está rodando
- Verificar console do navegador para erros

### Redirecionado para login constantemente
- Verificar se token está no localStorage
- Verificar se mock API está rodando
- Verificar console para erros de rede

### Token não funciona
- Verificar formato do token no localStorage
- Verificar se está sendo enviado no header
- Verificar Network tab no DevTools

### Mock API não inicia
- Verificar se porta 8000 está livre
- Verificar se jsonwebtoken está instalado: `npm install`
- Verificar logs no terminal

## 📚 Documentação Adicional

- **Guia Completo de Autenticação**: `frontend/mock-api/AUTH_GUIDE.md`
- **README Mock API**: `frontend/mock-api/README.md`
- **Instruções de Teste**: `frontend/TEST_INSTRUCTIONS.md`

## 🎉 Pronto para Usar!

Use as credenciais acima para fazer login e testar todas as funcionalidades do sistema.

**Recomendação**: Use `admin` / `admin123` para ter acesso completo durante o desenvolvimento.

---

**Nota**: Estas credenciais são apenas para desenvolvimento/teste. Em produção, use autenticação real com senhas seguras!
