# Como Iniciar os Servidores

## Problema Identificado

O mock API estava retornando um array diretamente `[...]`, mas o frontend espera o formato paginado do Django:

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [...]
}
```

## Solução Implementada

Foi adicionado um middleware no `mock-api/auth-server.cjs` que transforma automaticamente as respostas de lista para o formato paginado do Django.

## Como Iniciar

### Terminal 1: Mock API Server

```bash
cd frontend
node mock-api/auth-server.cjs
```

Você deve ver:
```
🚀 Mock API Server is running!

📍 Endpoints:
   - Home: http://localhost:8000
   - Auth: http://localhost:8000/auth/login
   - API:  http://localhost:8000/api/initiatives

👤 Test Users:
   - Username: admin       | Password: admin123 (Superuser)
   - Username: maria.silva | Password: senha123 (Staff)
   - Username: joao.santos | Password: senha123 (Regular)
```

### Terminal 2: Frontend Dev Server

```bash
cd frontend
npm run dev
```

Você deve ver:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

## Testar a API

### 1. Testar formato paginado

```bash
curl http://localhost:8000/api/initiatives | jq '.'
```

Deve retornar:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Programa de Extensão Rural",
      ...
    }
  ]
}
```

### 2. Testar paginação

```bash
# Primeira página (2 itens)
curl "http://localhost:8000/api/initiatives?page=1&page_size=2" | jq '.count, .results | length'

# Segunda página
curl "http://localhost:8000/api/initiatives?page=2&page_size=2" | jq '.results | length'
```

### 3. Testar autenticação

```bash
# Login
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq '.'

# Deve retornar access e refresh tokens
```

## Acessar o Frontend

1. Abra http://localhost:5173/login
2. Login:
   - Username: `admin`
   - Password: `admin123`
3. Navegue para "Initiatives"
4. Você deve ver as 5 iniciativas listadas

## Troubleshooting

### Problema: "Failed to connect"
**Solução**: Certifique-se de que o mock API está rodando na porta 8000

### Problema: "Initiatives list is empty"
**Solução**: 
1. Verifique se o mock API está retornando dados:
   ```bash
   curl http://localhost:8000/api/initiatives
   ```
2. Verifique o console do navegador (F12) para erros
3. Verifique se está autenticado (token no localStorage)

### Problema: "401 Unauthorized"
**Solução**: 
1. Faça logout e login novamente
2. Limpe o localStorage do navegador
3. Verifique se o token está sendo enviado (Network tab no DevTools)

### Problema: Porta 8000 já em uso
**Solução**:
```bash
# Encontrar processo
lsof -i :8000

# Matar processo
kill -9 <PID>
```

## Verificar se está funcionando

### Checklist:
- [ ] Mock API rodando na porta 8000
- [ ] Frontend rodando na porta 5173
- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Initiatives lista as 5 iniciativas
- [ ] Busca funciona
- [ ] Filtros funcionam
- [ ] Paginação funciona
- [ ] Detalhes da iniciativa carregam

## Comandos Úteis

```bash
# Parar todos os processos node
pkill -f node

# Ver processos rodando
ps aux | grep node

# Ver portas em uso
lsof -i :8000
lsof -i :5173

# Testar endpoint específico
curl http://localhost:8000/api/initiatives/1/

# Ver logs do mock API
# (os logs aparecem no terminal onde você iniciou o servidor)
```

## Estrutura de Dados Esperada

### Lista de Iniciativas (GET /api/initiatives)
```json
{
  "count": 5,
  "next": "http://localhost:8000/api/initiatives?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Programa de Extensão Rural",
      "description": "...",
      "type": "PROGRAM",
      "start_date": "2024-01-15",
      "end_date": "2025-12-31",
      "coordinator": {
        "id": 1,
        "first_name": "Maria",
        "last_name": "Silva",
        "email": "maria.silva@example.com",
        "full_name": "Maria Silva"
      },
      "parent": null,
      "parent_id": null,
      "team_members": [...],
      "students": [...],
      "organizational_groups": [...],
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

### Iniciativa Individual (GET /api/initiatives/1/)
```json
{
  "id": 1,
  "name": "Programa de Extensão Rural",
  ...
}
```

## Próximos Passos

Após verificar que tudo está funcionando:
1. Teste todas as funcionalidades (ver `documentation/TESTING_PHASE2.md`)
2. Reporte qualquer problema encontrado
3. Prossiga para Phase 3: Scholarships Module
