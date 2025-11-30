# OneStep

Sistema de gerenciamento de iniciativas organizacionais incluindo programas, projetos e eventos.

## Estrutura do Projeto

```
onestep/
├── backend/           # Django REST API
├── frontend/          # Vue 3 + TypeScript + Vuetify
├── documentation/     # Documentação completa
└── docker-compose.yml # Orquestração full stack
```

## Início Rápido

### Full Stack (Recomendado)

```bash
# Iniciar todos os serviços
docker-compose up

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# Admin: http://localhost:8000/admin
```

### Backend Apenas

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Apenas

```bash
cd frontend
npm install
npm run dev
```

## Tecnologias

### Backend
- Python 3.x
- Django + Django REST Framework
- PostgreSQL
- Docker

### Frontend
- Vue 3
- TypeScript
- Vuetify 3
- Vite
- Pinia

## Documentação

Toda documentação está em `/documentation`:

- **specs/** - Especificações técnicas
- **api/** - Documentação da API
- **guides/** - Guias de uso
- **proposals/** - Propostas de features
- **architecture/** - Diagramas e arquitetura

## Desenvolvimento

### Backend
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py test
```

### Frontend
```bash
cd frontend
npm run dev      # Desenvolvimento
npm run build    # Build produção
npm run test     # Testes
npm run lint     # Linting
```

## Deploy

### Backend
```bash
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ para servidor estático
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.

## Contato

Para mais informações, consulte a documentação em `/documentation`.
