#!/bin/bash

# Script de Verificação da Estrutura do Projeto OneStep
# Verifica se todos os arquivos e diretórios estão nos lugares corretos

echo "🔍 Verificando estrutura do projeto OneStep..."
echo "================================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de erros
ERRORS=0

# Função para verificar se arquivo/diretório existe
check_exists() {
    if [ -e "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (FALTANDO)"
        ((ERRORS++))
    fi
}

# Função para verificar se arquivo/diretório NÃO existe
check_not_exists() {
    if [ ! -e "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 (removido corretamente)"
    else
        echo -e "${YELLOW}⚠${NC} $1 (deveria ter sido removido)"
    fi
}

echo "📁 Verificando Backend..."
echo "------------------------"
check_exists "backend"
check_exists "backend/apps"
check_exists "backend/onestep"
check_exists "backend/manage.py"
check_exists "backend/requirements.txt"
check_exists "backend/Dockerfile"
check_exists "backend/docker-compose.yml"
check_exists "backend/Makefile"
check_exists "backend/README.md"
check_exists "backend/scripts"
check_exists "backend/docker"
check_exists "backend/logs"
check_exists "backend/media"
check_exists "backend/staticfiles"
echo ""

echo "📁 Verificando Frontend..."
echo "-------------------------"
check_exists "frontend"
check_exists "frontend/src"
check_exists "frontend/package.json"
check_exists "frontend/vite.config.ts"
check_exists "frontend/README.md"
echo ""

echo "📁 Verificando Documentation..."
echo "-------------------------------"
check_exists "documentation"
check_exists "documentation/specs"
check_exists "documentation/api"
check_exists "documentation/guides"
check_exists "documentation/proposals"
check_exists "documentation/architecture"
check_exists "documentation/README.md"
check_exists "documentation/proposals/FRONTEND_PROPOSAL.md"
check_exists "documentation/proposals/FRONTEND_SPEC_SUMMARY.md"
echo ""

echo "📁 Verificando Raiz..."
echo "---------------------"
check_exists "README.md"
check_exists "docker-compose.yml"
check_exists ".gitignore"
check_exists ".dockerignore"
check_exists ".kiro"
check_exists ".vscode"
echo ""

echo "🗑️  Verificando Limpeza..."
echo "-------------------------"
check_not_exists "apps"
check_not_exists "onestep"
check_not_exists "manage.py"
check_not_exists "requirements.txt"
check_not_exists "Dockerfile"
check_not_exists "Makefile"
check_not_exists "docs"
check_not_exists "documentations"
echo ""

echo "================================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Estrutura verificada com sucesso!${NC}"
    echo "Todos os arquivos e diretórios estão nos lugares corretos."
    exit 0
else
    echo -e "${RED}❌ Encontrados $ERRORS erros na estrutura!${NC}"
    echo "Verifique os itens marcados como FALTANDO acima."
    exit 1
fi
