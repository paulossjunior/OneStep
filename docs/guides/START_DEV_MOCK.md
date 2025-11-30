# 🚀 Iniciar Frontend com Mock API

## Comando para Executar

Abra um terminal e execute:

```bash
cd frontend
npm run dev:mock
```

Ou use o script bash:

```bash
cd frontend
./start-with-mock.sh
```

## O que será iniciado

1. **json-server** (Mock API)
   - Porta: 8000
   - URL: http://localhost:8000
   - Dados: mock-api/db.json

2. **Vite Dev Server** (Frontend)
   - Porta: 5173
   - URL: http://localhost:5173

## Verificar se está funcionando

### 1. Mock API
Abra em outra aba do terminal:
```bash
curl http://localhost:8000/initiatives
```

Deve retornar JSON com as iniciativas.

### 2. Frontend
Abra no navegador:
```
http://localhost:5173
```

Deve ver a aplicação rodando.

### 3. Initiatives List
Navegue para:
```
http://localhost:5173/initiatives
```

Deve ver a lista de iniciativas com:
- 5 iniciativas de exemplo
- Busca funcionando
- Filtros funcionando
- Ordenação funcionando
- Export funcionando

## Logs

Você verá logs de ambos os serviços no terminal:

```
[0] 
[0]   \{^_^}/ hi!
[0] 
[0]   Loading mock-api/db.json
[0]   Done
[0] 
[0]   Resources
[0]   http://localhost:8000/initiatives
[0]   http://localhost:8000/people
[0]   http://localhost:8000/organizational_groups
[0]   http://localhost:8000/failed_imports
[0]   http://localhost:8000/coordinator_changes
[0] 
[0]   Home
[0]   http://localhost:8000
[0] 
[1] 
[1]   VITE v5.x.x  ready in xxx ms
[1] 
[1]   ➜  Local:   http://localhost:5173/
[1]   ➜  Network: use --host to expose
[1]   ➜  press h + enter to show help
```

## Parar os Serviços

Pressione `Ctrl+C` no terminal para parar ambos os serviços.

## Troubleshooting

### Porta 8000 já em uso

```bash
# Verificar o que está usando
lsof -i :8000

# Matar o processo
kill -9 <PID>
```

### Porta 5173 já em uso

```bash
# Verificar o que está usando
lsof -i :5173

# Matar o processo
kill -9 <PID>
```

### npm não encontrado

Certifique-se de ter Node.js instalado:
```bash
node --version
npm --version
```

Se não tiver, instale via nvm:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

## Próximos Passos

1. ✅ Abrir http://localhost:5173
2. ✅ Navegar para Initiatives
3. ✅ Testar busca, filtros, ordenação
4. ✅ Testar export
5. ✅ Testar tema light/dark
6. ✅ Testar idioma en/pt-BR

---

**Nota**: Como o processo de desenvolvimento é interativo e de longa duração, é melhor executá-lo manualmente no terminal ao invés de através de scripts automatizados.
