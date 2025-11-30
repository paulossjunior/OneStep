#!/bin/bash

echo "🧪 Testando Mock API..."
echo "======================="
echo ""

# Test 1: Check if API is running
echo "1️⃣  Verificando se API está rodando..."
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "   ✅ API está rodando"
else
    echo "   ❌ API não está rodando"
    echo "   Execute: npm run dev:mock"
    exit 1
fi
echo ""

# Test 2: Test initiatives endpoint
echo "2️⃣  Testando endpoint /initiatives..."
INITIATIVES=$(curl -s http://localhost:8000/initiatives)
if [ ! -z "$INITIATIVES" ]; then
    echo "   ✅ Endpoint /initiatives funcionando"
    echo "   Iniciativas encontradas: $(echo $INITIATIVES | grep -o '"id"' | wc -l)"
else
    echo "   ❌ Endpoint /initiatives não responde"
fi
echo ""

# Test 3: Test auth endpoint
echo "3️⃣  Testando endpoint /auth/login..."
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

if echo "$AUTH_RESPONSE" | grep -q "access"; then
    echo "   ✅ Login funcionando"
    echo "   Token recebido: $(echo $AUTH_RESPONSE | grep -o '"access":"[^"]*"' | cut -d'"' -f4 | cut -c1-20)..."
else
    echo "   ❌ Login não funcionando"
    echo "   Resposta: $AUTH_RESPONSE"
fi
echo ""

# Test 4: Test with invalid credentials
echo "4️⃣  Testando login com credenciais inválidas..."
INVALID_AUTH=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "wrong"}')

if echo "$INVALID_AUTH" | grep -q "Invalid"; then
    echo "   ✅ Validação de credenciais funcionando"
else
    echo "   ⚠️  Validação pode não estar funcionando corretamente"
fi
echo ""

# Test 5: Test API with /api prefix
echo "5️⃣  Testando endpoint /api/initiatives..."
API_INITIATIVES=$(curl -s http://localhost:8000/api/initiatives)
if [ ! -z "$API_INITIATIVES" ]; then
    echo "   ✅ Endpoint /api/initiatives funcionando"
else
    echo "   ❌ Endpoint /api/initiatives não responde"
fi
echo ""

# Test 6: Test auth with /api prefix
echo "6️⃣  Testando endpoint /api/auth/login..."
API_AUTH=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

if echo "$API_AUTH" | grep -q "access"; then
    echo "   ✅ Login via /api funcionando"
else
    echo "   ❌ Login via /api não funcionando"
fi
echo ""

echo "======================="
echo "✨ Testes concluídos!"
echo ""
echo "Se todos os testes passaram, você pode:"
echo "1. Abrir http://localhost:5173/login"
echo "2. Usar: admin / admin123"
echo "3. Testar a aplicação"
echo ""
