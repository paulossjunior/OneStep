# OneStep Backend

Django REST API para gerenciamento de iniciativas de pesquisa, bolsas e grupos organizacionais.

## 🚀 Quick Start

### Desenvolvimento Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### Docker

```bash
# Iniciar todos os serviços
docker-compose up

# Ou com Superset
docker-compose -f docker-compose.superset.yml up
```

### Makefile

```bash
# Ver todos os comandos disponíveis
make help

# Comandos úteis
make migrate              # Executar migrações
make makemigrations       # Criar migrações
make test                 # Executar testes
make shell                # Abrir Django shell
make docker-up            # Iniciar containers
```

## 📁 Estrutura

```
backend/
├── apps/                    # Django apps (domínios)
│   ├── initiatives/        # Iniciativas
│   ├── scholarships/       # Bolsas
│   ├── people/             # Pessoas
│   ├── organizational_group/ # Grupos organizacionais
│   └── core/               # Funcionalidades compartilhadas
├── onestep/                # Configurações Django
├── docker/                 # Configurações Docker
├── scripts/                # Scripts utilitários
├── logs/                   # Logs da aplicação
├── media/                  # Arquivos de mídia
├── staticfiles/            # Arquivos estáticos
├── example/                # Dados de exemplo
├── manage.py               # Django management
├── requirements.txt        # Dependências Python
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker compose
└── Makefile                # Comandos make
```

## 🔧 Tecnologias

- **Python 3.11+**
- **Django 4.2+**
- **Django REST Framework**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Apache Superset** (opcional)

## 📚 Documentação

- [API Documentation](../documentation/api/)
- [Especificações](../documentation/specs/)
- [Guias](../documentation/guides/)

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Executar testes de um app específico
python manage.py test apps.initiatives

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

## 🔐 Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/onestep
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 📦 Apps Django

### Core
Funcionalidades compartilhadas, modelos base, utilitários.

### Initiatives
Gerenciamento de iniciativas (programas, projetos, eventos).
- CRUD de iniciativas
- Estrutura hierárquica
- Gerenciamento de equipe
- Importação CSV/ZIP
- Rastreamento de mudanças de coordenador

### Scholarships
Gerenciamento de bolsas de estudo.
- CRUD de bolsas
- Estatísticas
- Importação CSV/ZIP
- Cálculo de duração e valor

### People
Gerenciamento de pessoas (coordenadores, membros, estudantes).
- CRUD de pessoas
- Busca e filtros
- Relacionamentos com iniciativas

### Organizational Group
Gerenciamento de grupos organizacionais, campi e áreas de conhecimento.
- Unidades organizacionais
- Gerenciamento de liderança
- Campi
- Áreas de conhecimento

## 🚢 Deploy

### Produção

```bash
# Build da imagem
docker build -t onestep-backend .

# Executar
docker-compose -f docker-compose.prod.yml up -d
```

### Variáveis de Ambiente (Produção)

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@db:5432/onestep
ALLOWED_HOSTS=api.onestep.com
CORS_ALLOWED_ORIGINS=https://onestep.com
```

## 🤝 Contribuindo

1. Crie uma branch para sua feature
2. Faça suas alterações
3. Execute os testes
4. Faça commit das mudanças
5. Abra um Pull Request

## 📄 Licença

Este projeto faz parte da plataforma OneStep.
