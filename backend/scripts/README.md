# Backend Scripts

Esta pasta contém scripts utilitários para o backend do OneStep.

## 📁 Scripts Disponíveis

### 1. `create_oauth_app.py`
Cria uma aplicação OAuth2 para autenticação do frontend.

**Uso:**
```bash
cd backend
python scripts/create_oauth_app.py
```

**O que faz:**
- Cria ou atualiza uma aplicação OAuth2 no Django
- Configura como CLIENT_PUBLIC
- Define grant type como PASSWORD
- Gera Client ID e Client Secret

**Saída:**
```
OAuth2 Credentials:
Client ID: <client-id>
Client Secret: <client-secret>
```

### 2. `create_sample_initiatives.py`
Cria dados de exemplo (iniciativas, pessoas, grupos) para desenvolvimento e testes.

**Uso:**
```bash
cd backend
python scripts/create_sample_initiatives.py
```

**O que faz:**
- Cria pessoas de exemplo
- Cria grupos organizacionais
- Cria iniciativas (programas, projetos, eventos)
- Estabelece relacionamentos entre entidades

**Dados criados:**
- ~10 pessoas
- ~5 grupos organizacionais
- ~15 iniciativas com hierarquia

### 3. `backup_superset.sh`
Script de backup para o Apache Superset (se estiver usando).

**Uso:**
```bash
cd backend
bash scripts/backup_superset.sh
```

**O que faz:**
- Faz backup do banco de dados do Superset
- Faz backup dos dashboards
- Compacta em arquivo .tar.gz
- Salva com timestamp

## 🚀 Como Executar

### Dentro do Docker

```bash
# OAuth App
docker-compose -f docker-compose.dev.yml exec backend python scripts/create_oauth_app.py

# Sample Data
docker-compose -f docker-compose.dev.yml exec backend python scripts/create_sample_initiatives.py

# Backup Superset
docker-compose -f docker-compose.dev.yml exec backend bash scripts/backup_superset.sh
```

### Localmente

```bash
cd backend

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Executar scripts
python scripts/create_oauth_app.py
python scripts/create_sample_initiatives.py
bash scripts/backup_superset.sh
```

## 📝 Notas

- Todos os scripts Python usam `django.setup()` para configurar o Django
- Os scripts são idempotentes (podem ser executados múltiplas vezes)
- Verifique os logs para confirmar a execução
- Em produção, use variáveis de ambiente apropriadas

## 🔧 Desenvolvimento

Para criar novos scripts:

1. Crie o arquivo na pasta `backend/scripts/`
2. Adicione o shebang apropriado:
   - Python: `#!/usr/bin/env python`
   - Bash: `#!/bin/bash`
3. Configure o Django (para scripts Python):
   ```python
   import os
   import django
   
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onestep.settings')
   django.setup()
   ```
4. Torne executável (se necessário):
   ```bash
   chmod +x scripts/seu_script.sh
   ```
5. Documente neste README

## 🆘 Troubleshooting

### Erro: "No module named 'django'"
```bash
# Certifique-se de estar no ambiente virtual
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "DJANGO_SETTINGS_MODULE is not set"
```bash
# Defina a variável de ambiente
export DJANGO_SETTINGS_MODULE=onestep.settings
```

### Erro: "Database connection failed"
```bash
# Verifique se o database está rodando
docker-compose -f docker-compose.dev.yml ps db

# Ou inicie o database
docker-compose -f docker-compose.dev.yml up db
```

---

**Última atualização**: 30 de Novembro de 2024
