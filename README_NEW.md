# OneStep

Sistema completo de gestão de iniciativas de pesquisa, bolsas de estudo e grupos organizacionais.

## 📁 Estrutura do Projeto

```
onestep/
├── backend/          # Django REST API
├── frontend/         # Vue 3 + TypeScript SPA  
└── documentation/    # Documentação completa
```

## 🚀 Quick Start

### Opção 1: Full Stack com Docker

```bash
# Iniciar backend e frontend juntos
docker-compose up
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Admin: http://localhost:8000/admin

### Opção 2: Desenvolvimento Separado

**Backend:**
```bash
cd backend
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentação

Toda documentação está organizada em [documentation/](./documentation/)

- **[Especificações](./documentation/specs/)** - Specs técnicas detalhadas
- **[API](./documentation/api/)** - Documentação da API REST
- **[Guias](./documentation/guides/)** - Guias de desenvolvimento e uso
- **[Propostas](./documentation/proposals/)** - Propostas e RFCs

### Documentação Principal

- **[Backend README](./backend/README.md)** - Como desenvolver o backend
- **[Frontend README](./frontend/README.md)** - Como desenvolver o frontend
- **[Documentation README](./documentation/README.md)** - Índice da documentação

## 🎯 Sobre o OneStep

OneStep é uma plataforma para gerenciamento de:

### 🎓 Iniciativas de Pesquisa
- Programas, projetos e eventos
- Estrutura hierárquica (iniciativas pai/filho)
- Gerenciamento de equipe e estudantes
- Importação em massa via CSV/ZIP
- Rastreamento de mudanças de coordenador

### 💰 Bolsas de Estudo
- Gerenciamento de bolsas
- Cálculo de duração e valor total
- Estatísticas por campus e tipo
- Importação em massa via CSV/ZIP
- Rastreamento de erros de importação

### 👥 Pessoas
- Coordenadores, membros de equipe, estudantes
- Busca e filtros avançados
- Histórico de participação em iniciativas

### 🏛️ Grupos Organizacionais
- Unidades organizacionais (grupos de pesquisa/extensão)
- Campi universitários
- Áreas de conhecimento
- Gerenciamento de liderança com histórico

## 🛠️ Tecnologias

### Backend
- Python 3.11+
- Django 4.2+
- Django REST Framework
- PostgreSQL
- Docker

### Frontend
- Vue 3.4+
- TypeScript 5.0+
- Vite 5.0+
- Vuetify 3
- TailwindCSS
- Pinia + TanStack Query

## 🏗️ Arquitetura

### Domain-Driven Design

Cada domínio de negócio é um módulo independente:

```
Backend (Django)        Frontend (Vue 3)
─────────────────────────────────────────────
apps/core           →   src/core/
apps/initiatives    →   src/modules/initiatives/
apps/scholarships   →   src/modules/scholarships/
apps/people         →   src/modules/people/
apps/organizational_group → src/modules/organizational_group/
```

### Comunicação

```
Frontend (Vue 3) ←→ REST API ←→ Backend (Django) ←→ PostgreSQL
```

## 📦 Instalação

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Docker & Docker Compose (opcional)

### Instalação Completa

```bash
# 1. Clone o repositório
git clone <repository-url>
cd onestep

# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# 3. Frontend
cd ../frontend
npm install

# 4. Iniciar serviços
# Terminal 1 (Backend)
cd backend && python manage.py runserver

# Terminal 2 (Frontend)
cd frontend && npm run dev
```

## 🧪 Testes

### Backend
```bash
cd backend
python manage.py test
```

### Frontend
```bash
cd frontend
npm run test:unit
npm run test:e2e
```

## 🚢 Deploy

### Backend
```bash
cd backend
docker build -t onestep-backend .
docker-compose -f docker-compose.prod.yml up -d
```

### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ para servidor estático ou CDN
```

## 🤝 Contribuindo

1. Leia a [documentação](./documentation/)
2. Crie uma branch para sua feature
3. Faça suas alterações
4. Execute os testes
5. Abra um Pull Request

## 📄 Licença

Este projeto faz parte da plataforma OneStep.

## 🔗 Links Úteis

- **Backend**: [backend/README.md](./backend/README.md)
- **Frontend**: [frontend/README.md](./frontend/README.md)
- **Documentação**: [documentation/README.md](./documentation/README.md)
- **API Schema**: http://localhost:8000/api/schema/
- **Admin**: http://localhost:8000/admin/
- **Frontend**: http://localhost:3000/

## 📞 Suporte

Para questões ou problemas:
1. Verifique a documentação relevante
2. Consulte os guias em `documentation/guides/`
3. Entre em contato com o tech lead

---

**Versão**: 1.0  
**Última Atualização**: 2024-11-30
