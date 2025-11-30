#!/bin/bash

# Script de Reestruturação do Projeto OneStep
# Organiza o projeto em: backend/, frontend/, documentation/

set -e

echo "🔄 Iniciando reestruturação do projeto OneStep..."
echo "=================================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para criar diretórios
create_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo -e "${GREEN}✓${NC} Criado: $1"
    else
        echo -e "${YELLOW}⚠${NC} Já existe: $1"
    fi
}

# Função para mover com git
move_with_git() {
    if [ -e "$1" ]; then
        git mv "$1" "$2" 2>/dev/null || mv "$1" "$2"
        echo -e "${GREEN}✓${NC} Movido: $1 → $2"
    else
        echo -e "${YELLOW}⚠${NC} Não encontrado: $1"
    fi
}

echo -e "${BLUE}Passo 1: Criando estrutura de diretórios${NC}"
echo "-------------------------------------------"
create_dir "backend"
create_dir "documentation"
create_dir "documentation/specs"
create_dir "documentation/api"
create_dir "documentation/guides"
create_dir "documentation/proposals"
create_dir "documentation/architecture"
echo ""

echo -e "${BLUE}Passo 2: Movendo Backend${NC}"
echo "------------------------"
move_with_git "apps" "backend/apps"
move_with_git "onestep" "backend/onestep"
move_with_git "manage.py" "backend/manage.py"
move_with_git "requirements.txt" "backend/requirements.txt"
move_with_git "Dockerfile" "backend/Dockerfile"
move_with_git "docker-compose.yml" "backend/docker-compose.yml"
move_with_git "docker-compose.superset.yml" "backend/docker-compose.superset.yml"
move_with_git "docker-compose.prod.yml" "backend/docker-compose.prod.yml"
move_with_git "Makefile" "backend/Makefile"
move_with_git "entrypoint.sh" "backend/entrypoint.sh"
move_with_git "scripts" "backend/scripts"
move_with_git "docker" "backend/docker"
move_with_git "logs" "backend/logs"
move_with_git "media" "backend/media"
move_with_git "staticfiles" "backend/staticfiles"
move_with_git ".env.example" "backend/.env.example"
move_with_git ".env.dev" "backend/.env.dev"
move_with_git ".env.prod.example" "backend/.env.prod.example"
move_with_git ".env.superset" "backend/.env.superset"
move_with_git "migrate_data.py" "backend/migrate_data.py"
move_with_git "test_campus_migration.py" "backend/test_campus_migration.py"
move_with_git "test_campus_migration_edge_cases.py" "backend/test_campus_migration_edge_cases.py"
echo ""

echo -e "${BLUE}Passo 3: Movendo Documentação${NC}"
echo "------------------------------"
move_with_git ".kiro/specs" "documentation/specs"
move_with_git "docs" "documentation/api"
move_with_git "documentations" "documentation/guides"
move_with_git "FRONTEND_PROPOSAL.md" "documentation/proposals/FRONTEND_PROPOSAL.md"
move_with_git "FRONTEND_SPEC_SUMMARY.md" "documentation/proposals/FRONTEND_SPEC_SUMMARY.md"
move_with_git "RESTRUCTURE_PLAN.md" "documentation/RESTRUCTURE_PLAN.md"
echo ""

echo -e "${BLUE}Passo 4: Movendo Exemplos${NC}"
echo "-------------------------"
move_with_git "example" "backend/example"
move_with_git "examples" "backend/examples"
move_with_git "sample_research_groups.csv" "backend/sample_research_groups.csv"
echo ""

echo -e "${BLUE}Passo 5: Limpando diretórios vazios${NC}"
echo "------------------------------------"
# Remover .kiro se estiver vazio
if [ -d ".kiro" ] && [ -z "$(ls -A .kiro)" ]; then
    rmdir .kiro
    echo -e "${GREEN}✓${NC} Removido: .kiro (vazio)"
fi
echo ""

echo -e "${GREEN}✅ Reestruturação concluída!${NC}"
echo ""
echo "Nova estrutura:"
echo "  backend/          - Todo código Django"
echo "  frontend/         - Todo código Vue 3"
echo "  documentation/    - Toda documentação"
echo ""
echo "Próximos passos:"
echo "1. Revisar a nova estrutura"
echo "2. Atualizar paths nos arquivos de configuração"
echo "3. Testar backend: cd backend && python manage.py runserver"
echo "4. Testar frontend: cd frontend && npm run dev"
echo "5. Commit das mudanças: git add . && git commit -m 'Reestruturação do projeto'"
echo ""
