# Mock API - OneStep Frontend

Mock backend usando json-server para desenvolvimento e testes do frontend sem depender do backend Django.

## 🚀 Como Usar

### Iniciar Mock API + Frontend

```bash
cd frontend
npm install
npm run dev:mock
```

Isso iniciará:
- **Mock API**: http://localhost:8000 (com autenticação)
- **Frontend**: http://localhost:5173

### Apenas Mock API

```bash
npm run mock-api
```

## 🔐 Autenticação

O Mock API agora inclui autenticação JWT!

### Usuários Disponíveis

| Username | Password | Tipo | Permissões |
|----------|----------|------|------------|
| `admin` | `admin123` | Superusuário | Todas |
| `maria.silva` | `senha123` | Staff | Ver, Adicionar, Editar |
| `joao.santos` | `senha123` | Regular | Ver apenas |

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Ver guia completo**: [AUTH_GUIDE.md](./AUTH_GUIDE.md)

## 📚 Endpoints Disponíveis

### Initiatives

```bash
# Listar todas as iniciativas
GET http://localhost:8000/initiatives

# Listar com paginação
GET http://localhost:8000/initiatives?_page=1&_limit=10

# Buscar por nome
GET http://localhost:8000/initiatives?name_like=Programa

# Filtrar por tipo
GET http://localhost:8000/initiatives?type=PROGRAM

# Obter uma iniciativa
GET http://localhost:8000/initiatives/1

# Criar iniciativa
POST http://localhost:8000/initiatives
Content-Type: application/json

{
  "name": "Nova Iniciativa",
  "description": "Descrição",
  "type": "PROJECT",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "coordinator": {...},
  "parent_id": null
}

# Atualizar iniciativa
PATCH http://localhost:8000/initiatives/1
Content-Type: application/json

{
  "name": "Nome Atualizado"
}

# Deletar iniciativa
DELETE http://localhost:8000/initiatives/1
```

### People

```bash
# Listar pessoas
GET http://localhost:8000/people

# Buscar por nome
GET http://localhost:8000/people?first_name_like=Maria

# Obter uma pessoa
GET http://localhost:8000/people/1
```

### Organizational Groups

```bash
# Listar grupos
GET http://localhost:8000/organizational_groups

# Filtrar por tipo
GET http://localhost:8000/organizational_groups?type=RESEARCH
```

### Failed Imports

```bash
# Listar importações falhadas
GET http://localhost:8000/failed_imports

# Obter uma importação falhada
GET http://localhost:8000/failed_imports/1

# Deletar importação falhada
DELETE http://localhost:8000/failed_imports/1
```

### Coordinator Changes

```bash
# Listar mudanças de coordenador
GET http://localhost:8000/coordinator_changes

# Filtrar por iniciativa
GET http://localhost:8000/coordinator_changes?initiative.id=2
```

## 🔧 Funcionalidades

### Paginação

json-server suporta paginação automática:

```bash
GET http://localhost:8000/initiatives?_page=1&_limit=10
```

Headers de resposta:
- `X-Total-Count`: Total de registros
- `Link`: Links para próxima/anterior página

### Ordenação

```bash
# Ordenar por nome (ascendente)
GET http://localhost:8000/initiatives?_sort=name&_order=asc

# Ordenar por data (descendente)
GET http://localhost:8000/initiatives?_sort=created_at&_order=desc
```

### Busca

```bash
# Busca parcial (like)
GET http://localhost:8000/initiatives?name_like=Programa

# Busca exata
GET http://localhost:8000/initiatives?type=PROJECT
```

### Filtros

```bash
# Múltiplos filtros
GET http://localhost:8000/initiatives?type=PROGRAM&_sort=name
```

### Relacionamentos

```bash
# Expandir relacionamentos
GET http://localhost:8000/initiatives?_embed=team_members

# Incluir parent
GET http://localhost:8000/initiatives?_expand=parent
```

## 📝 Estrutura de Dados

### Initiative

```json
{
  "id": 1,
  "name": "Nome da Iniciativa",
  "description": "Descrição detalhada",
  "type": "PROGRAM | PROJECT | EVENT",
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
```

### Person

```json
{
  "id": 1,
  "first_name": "Maria",
  "last_name": "Silva",
  "email": "maria.silva@example.com",
  "phone": "+55 11 98765-4321",
  "full_name": "Maria Silva"
}
```

## 🎯 Dados de Exemplo

O arquivo `db.json` contém:
- **5 iniciativas** (2 programas, 2 projetos, 1 evento)
- **14 pessoas** (coordenadores, membros, estudantes)
- **3 grupos organizacionais**
- **2 importações falhadas**
- **1 mudança de coordenador**

## 🔄 Middleware Customizado

O arquivo `middleware.js` adiciona:
- **Delay de 300ms** para simular latência de rede
- **Headers CORS** para permitir requisições do frontend
- **Headers de paginação** (X-Total-Count, X-Page, X-Page-Size)

## 🛠️ Modificar Dados

### Editar db.json

Você pode editar `db.json` diretamente. O json-server recarrega automaticamente.

### Resetar Dados

```bash
# Fazer backup
cp mock-api/db.json mock-api/db.backup.json

# Restaurar backup
cp mock-api/db.backup.json mock-api/db.json
```

### Adicionar Mais Dados

Edite `db.json` e adicione novos registros seguindo a estrutura existente.

## 📊 Rotas Customizadas

O arquivo `routes.json` define rotas customizadas:

```json
{
  "/api/*": "/$1",
  "/api/initiatives/:id/hierarchy": "/initiatives?parent_id=:id",
  "/api/initiatives/:id/children": "/initiatives?parent_id=:id"
}
```

Isso permite que o frontend use URLs como `/api/initiatives` que são mapeadas para `/initiatives`.

## 🧪 Testar com Postman/Insomnia

Importe a coleção de exemplo:

```bash
# Listar iniciativas
GET http://localhost:8000/initiatives

# Criar iniciativa
POST http://localhost:8000/initiatives
Content-Type: application/json

{
  "name": "Teste",
  "description": "Descrição teste",
  "type": "PROJECT",
  "start_date": "2024-01-01",
  "coordinator": {
    "id": 1,
    "first_name": "Maria",
    "last_name": "Silva",
    "email": "maria.silva@example.com",
    "full_name": "Maria Silva"
  }
}
```

## 🐛 Troubleshooting

### Porta 8000 já em uso

```bash
# Mudar porta no package.json
"mock-api": "json-server --watch mock-api/db.json --port 8001 ..."

# Atualizar VITE_API_URL no .env.development
VITE_API_URL=http://localhost:8001
```

### Dados não aparecem

1. Verifique se o json-server está rodando
2. Verifique o console do navegador para erros CORS
3. Verifique se a URL da API está correta no .env

### Mudanças não são salvas

json-server salva mudanças em `db.json` automaticamente. Se não estiver salvando:
1. Verifique permissões do arquivo
2. Verifique se o arquivo não está aberto em outro editor
3. Reinicie o json-server

## 📚 Documentação json-server

Para mais informações: https://github.com/typicode/json-server

## 🎓 Exemplos de Uso no Frontend

### Listar Iniciativas

```typescript
import { initiativesApi } from '@/modules/initiatives/api/initiatives.api';

const response = await initiativesApi.list({
  page: 1,
  page_size: 10,
  type: 'PROGRAM'
});

console.log(response.data.results);
```

### Criar Iniciativa

```typescript
import { initiativeService } from '@/modules/initiatives/services/initiative.service';

const initiative = await initiativeService.createInitiative({
  name: 'Nova Iniciativa',
  description: 'Descrição',
  type: 'PROJECT',
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  coordinator_id: 1,
  parent_id: null
});
```

### Usar Composable

```vue
<script setup>
import { useInitiatives } from '@/modules/initiatives/composables/useInitiatives';

const { items, isLoading, refetch } = useInitiatives();
</script>
```

---

**Nota**: Este é um mock backend apenas para desenvolvimento. Em produção, use o backend Django real.
