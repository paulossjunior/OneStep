# OneStep - Quick Start Guide

Guia rápido para começar a trabalhar com o projeto OneStep após a reestruturação.

## 📁 Nova Estrutura

```
onestep/
├── backend/           # Django REST API
├── frontend/          # Vue 3 + TypeScript
├── documentation/     # Toda documentação
└── docker-compose.yml # Full stack
```

## 🚀 Início Rápido

### Opção 1: Full Stack (Recomendado)

```bash
# Iniciar todos os serviços
docker-compose up

# Acessar:
# - Backend API: http://localhost:8000
# - Admin: http://localhost:8000/admin
# - Frontend: http://localhost:5173
```

### Opção 2: Backend Apenas

```bash
cd backend

# Com Docker
docker-compose up

# Ou local
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Opção 3: Frontend Apenas

```bash
cd frontend

# Com Docker
docker-compose up

# Ou local
npm install
npm run dev
```

## 📚 Documentação

Toda documentação está em `/documentation`:

```bash
documentation/
├── specs/              # Especificações técnicas
├── api/                # Documentação da API
├── guides/             # Guias de desenvolvimento
├── proposals/          # Propostas de features
└── README.md           # Índice completo
```

## 🔧 Comandos Úteis

### Backend

```bash
cd backend

# Migrações
python manage.py makemigrations
python manage.py migrate

# Testes
python manage.py test

# Shell
python manage.py shell

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Ver comandos make
make help
```

### Frontend

```bash
cd frontend

# Desenvolvimento
npm run dev

# Build
npm run build

# Testes
npm run test

# Lint
npm run lint

# Type check
npm run type-check
```

## 🐳 Docker

### Full Stack

```bash
# Iniciar
docker-compose up

# Parar
docker-compose down

# Rebuild
docker-compose up --build

# Ver logs
docker-compose logs -f
```

### Backend

```bash
cd backend

# Iniciar
docker-compose up

# Com Superset
docker-compose -f docker-compose.superset.yml up

# Produção
docker-compose -f docker-compose.prod.yml up
```

### Frontend

```bash
cd frontend

# Iniciar
docker-compose up

# Build
docker-compose -f docker-compose.prod.yml up
```

## 📖 Leitura Recomendada

1. **Para Desenvolvedores**
   - [Backend README](backend/README.md)
   - [Frontend README](frontend/README.md)
   - [Documentação Completa](documentation/README.md)

2. **Para Product Managers**
   - [Requirements](documentation/specs/frontend-vue3-typescript/requirements.md)
   - [User Stories](documentation/specs/frontend-vue3-typescript/requirements.md)

3. **Para Designers**
   - [Design Document](documentation/specs/frontend-vue3-typescript/design.md)
   - [Component List](documentation/specs/frontend-vue3-typescript/design.md)

## 🔍 Verificar Estrutura

```bash
# Executar script de verificação
./verify_structure.sh
```

## 🆘 Problemas Comuns

### Backend não inicia

```bash
cd backend
# Verificar se o banco está rodando
docker-compose ps

# Verificar logs
docker-compose logs db

# Recriar banco
docker-compose down -v
docker-compose up
```

### Frontend não inicia

```bash
cd frontend
# Limpar node_modules
rm -rf node_modules package-lock.json
npm install

# Verificar porta
lsof -i :5173
```

### Permissões no Docker

```bash
# Dar permissões aos diretórios
sudo chown -R $USER:$USER backend/media backend/staticfiles backend/logs
```

## 📞 Suporte

- **Documentação**: [documentation/README.md](documentation/README.md)
- **Issues**: Abra uma issue no GitHub
- **Specs**: [documentation/specs/](documentation/specs/)

---

**Última Atualização**: 30 de Novembro de 2024
