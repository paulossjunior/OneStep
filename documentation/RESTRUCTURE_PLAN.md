# Plano de Reestruturação do Projeto OneStep

## Estrutura Atual
```
onestep/
├── apps/                    # Django apps (backend)
├── onestep/                 # Django project settings
├── frontend/                # Vue 3 frontend
├── docs/                    # Documentação antiga
├── documentations/          # Documentação adicional
├── .kiro/                   # Specs e configurações
├── docker/                  # Docker configs
├── scripts/                 # Scripts utilitários
├── manage.py               # Django management
├── requirements.txt        # Python dependencies
└── [arquivos raiz]         # Configs, README, etc.
```

## Nova Estrutura Proposta
```
onestep/
├── backend/                 # Todo código Django
│   ├── apps/               # Django apps
│   ├── onestep/            # Django settings
│   ├── docker/             # Docker configs backend
│   ├── scripts/            # Scripts backend
│   ├── logs/               # Logs
│   ├── media/              # Media files
│   ├── staticfiles/        # Static files
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.superset.yml
│   ├── Makefile
│   ├── .env.example
│   └── README.md
│
├── frontend/                # Todo código Vue 3
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
│
├── documentation/           # Toda documentação
│   ├── specs/              # Especificações (.kiro/specs)
│   ├── api/                # API docs
│   ├── architecture/       # Diagramas e arquitetura
│   ├── guides/             # Guias de uso
│   ├── proposals/          # Propostas (FRONTEND_PROPOSAL.md, etc)
│   └── README.md
│
├── .github/                 # GitHub workflows
├── .vscode/                 # VSCode settings
├── README.md                # README principal
└── docker-compose.yml       # Docker compose raiz (full stack)
```

## Ações de Reestruturação

### 1. Criar Estrutura de Diretórios ✅
- [x] Criar `backend/`
- [x] Criar `documentation/`
- [x] `frontend/` já existe

### 2. Mover Backend ✅
- [x] Mover `apps/` → `backend/apps/`
- [x] Mover `onestep/` → `backend/onestep/`
- [x] Mover `manage.py` → `backend/manage.py`
- [x] Mover `requirements.txt` → `backend/requirements.txt`
- [x] Mover `Dockerfile` → `backend/Dockerfile`
- [x] Mover `docker-compose*.yml` → `backend/`
- [x] Mover `Makefile` → `backend/Makefile`
- [x] Mover `scripts/` → `backend/scripts/`
- [x] Mover `docker/` → `backend/docker/`
- [x] Mover `logs/` → `backend/logs/`
- [x] Mover `media/` → `backend/media/`
- [x] Mover `staticfiles/` → `backend/staticfiles/`
- [x] Mover `.env.dev`, `.env.prod.example`, `.env.superset` → `backend/`
- [x] Mover arquivos Python e CSV → `backend/`
- [x] Mover `example/`, `examples/` → `backend/`
- [x] `backend/README.md` já existia

### 3. Organizar Documentation ✅
- [x] Copiar `.kiro/specs/` → `documentation/specs/`
- [x] Mover `docs/` → `documentation/api/`
- [x] Mover `documentations/` → `documentation/guides/`
- [x] Mover `FRONTEND_PROPOSAL.md` → `documentation/proposals/`
- [x] Mover `FRONTEND_SPEC_SUMMARY.md` → `documentation/proposals/`
- [x] Mover `RESTRUCTURE_PLAN.md` → `documentation/`
- [x] `documentation/README.md` já existia

### 4. Atualizar Configurações ✅
- [x] Verificar paths no `backend/Dockerfile` (OK)
- [x] Verificar paths no `backend/docker-compose.yml` (OK)
- [x] Verificar paths no `backend/Makefile` (OK)
- [x] Verificar imports no Django settings (OK - BASE_DIR correto)
- [x] Criar `docker-compose.yml` raiz para full stack
- [x] Atualizar `README.md` principal

### 5. Manter na Raiz ✅
- `.git/`
- `.github/`
- `.kiro/`
- `.vscode/`
- `.gitignore`
- `README.md` (atualizado)
- `docker-compose.yml` (full stack)
- `.dockerignore`

### 6. Limpeza ✅
- [x] Remover diretórios vazios da raiz
- [x] Verificar estrutura final

## Benefícios da Nova Estrutura

1. **Separação Clara**: Backend, Frontend e Documentação isolados
2. **Desenvolvimento Independente**: Cada parte pode ser desenvolvida separadamente
3. **Deploy Facilitado**: Cada parte tem seu próprio Dockerfile
4. **Documentação Centralizada**: Toda documentação em um só lugar
5. **Manutenção Simplificada**: Mais fácil encontrar e atualizar código
6. **Onboarding Melhor**: Novos desenvolvedores entendem a estrutura rapidamente

## Comandos Após Reestruturação

### Backend
```bash
cd backend
python manage.py runserver
# ou
docker-compose up
```

### Frontend
```bash
cd frontend
npm run dev
# ou
docker-compose up
```

### Full Stack
```bash
# Na raiz
docker-compose up
```

## Notas Importantes

- Manter compatibilidade com Git history
- Usar `git mv` para preservar histórico
- Atualizar todos os paths em configs
- Testar após cada movimentação
- Atualizar documentação


---

## ✅ Status: CONCLUÍDO

**Data de Conclusão**: 30 de Novembro de 2024

Todas as tarefas do plano de reestruturação foram implementadas com sucesso!

### Verificação

Execute o script de verificação para confirmar a estrutura:

```bash
./verify_structure.sh
```

### Próximos Passos

1. **Testar Backend**
   ```bash
   cd backend
   docker-compose up
   ```

2. **Testar Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Testar Full Stack**
   ```bash
   docker-compose up
   ```

4. **Commit das Mudanças**
   ```bash
   git add .
   git commit -m "refactor: restructure project into backend, frontend, and documentation folders"
   ```

Para mais detalhes, consulte [RESTRUCTURE_COMPLETE.md](../RESTRUCTURE_COMPLETE.md).
