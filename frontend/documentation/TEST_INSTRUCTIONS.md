# 🧪 Instruções de Teste - OneStep Frontend

Guia rápido para testar o frontend com o Mock API.

## 🚀 Início Rápido

```bash
cd frontend

# Instalar dependências (primeira vez)
npm install

# Iniciar com Mock API
npm run dev:mock

# Ou usar o script
./start-with-mock.sh
```

**URLs**:
- Frontend: http://localhost:5173
- Mock API: http://localhost:8000

## ✅ Checklist de Testes

### 1. Autenticação (Placeholder)
- [ ] Acessar http://localhost:5173
- [ ] Ver dashboard (sem autenticação por enquanto)

### 2. Navegação
- [ ] Clicar em "Initiatives" no menu lateral
- [ ] Ver lista de iniciativas
- [ ] Menu lateral responsivo (testar em mobile)
- [ ] Theme switcher (light/dark)
- [ ] Language switcher (en/pt-BR)

### 3. Lista de Iniciativas
- [ ] Ver 5 iniciativas de exemplo
- [ ] Cards mostram informações corretas
- [ ] Ícones diferentes por tipo (Program, Project, Event)

### 4. Busca
- [ ] Digitar "Programa" na busca
- [ ] Ver resultados filtrados (debounce de 300ms)
- [ ] Limpar busca

### 5. Filtros
- [ ] Filtrar por tipo "Program"
- [ ] Ver apenas programas
- [ ] Clicar em "Filters" para filtros avançados
- [ ] Filtrar por data de início
- [ ] Limpar todos os filtros

### 6. Ordenação
- [ ] Ordenar por "Name (A-Z)"
- [ ] Ver lista ordenada
- [ ] Ordenar por "Newest First"

### 7. Paginação
- [ ] Ver paginação (se houver mais de 12 itens)
- [ ] Navegar entre páginas
- [ ] Scroll automático ao topo

### 8. Ações
- [ ] Clicar em "Refresh" - recarregar dados
- [ ] Clicar em "Export" - baixar CSV
- [ ] Verificar arquivo CSV baixado

### 9. Detalhes (Quando implementado)
- [ ] Clicar em um card
- [ ] Ver detalhes da iniciativa
- [ ] Ver membros da equipe
- [ ] Ver estudantes

### 10. Criar (Quando implementado)
- [ ] Clicar em "Create Initiative"
- [ ] Preencher formulário
- [ ] Salvar
- [ ] Ver nova iniciativa na lista

## 🔍 Testes da API Mock

### Testar Endpoints Diretamente

```bash
# Listar iniciativas
curl http://localhost:8000/initiatives

# Obter uma iniciativa
curl http://localhost:8000/initiatives/1

# Criar iniciativa
curl -X POST http://localhost:8000/initiatives \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste API",
    "description": "Descrição teste",
    "type": "PROJECT",
    "start_date": "2024-01-01",
    "coordinator": {
      "id": 1,
      "first_name": "Maria",
      "last_name": "Silva",
      "email": "maria.silva@example.com",
      "full_name": "Maria Silva"
    }
  }'

# Atualizar iniciativa
curl -X PATCH http://localhost:8000/initiatives/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Nome Atualizado"}'

# Deletar iniciativa
curl -X DELETE http://localhost:8000/initiatives/1

# Buscar
curl "http://localhost:8000/initiatives?name_like=Programa"

# Filtrar por tipo
curl "http://localhost:8000/initiatives?type=PROGRAM"

# Paginação
curl "http://localhost:8000/initiatives?_page=1&_limit=2"
```

## 🐛 Troubleshooting

### Porta 8000 já em uso

```bash
# Verificar o que está usando a porta
lsof -i :8000

# Matar o processo
kill -9 <PID>

# Ou mudar a porta no package.json
"mock-api": "json-server ... --port 8001"
```

### Frontend não conecta ao Mock API

1. Verificar se mock API está rodando: http://localhost:8000/initiatives
2. Verificar console do navegador para erros
3. Verificar `.env.development`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

### Dados não aparecem

1. Abrir DevTools (F12)
2. Ir para Network tab
3. Verificar requisições para `/initiatives`
4. Ver resposta da API
5. Verificar console para erros

### Mudanças no código não aparecem

1. Verificar se Vite está rodando
2. Verificar console para erros de compilação
3. Fazer hard refresh (Ctrl+Shift+R)
4. Limpar cache do navegador

## 📊 Dados de Teste

### Iniciativas Disponíveis

1. **Programa de Extensão Rural** (ID: 1)
   - Tipo: PROGRAM
   - Coordenador: Maria Silva
   - 2 membros, 1 estudante

2. **Projeto de Capacitação em Tecnologias Digitais** (ID: 2)
   - Tipo: PROJECT
   - Coordenador: João Santos
   - Parent: Programa de Extensão Rural
   - 1 membro, 2 estudantes

3. **Seminário de Inovação Agrícola** (ID: 3)
   - Tipo: EVENT
   - Coordenador: Carlos Rodrigues
   - 1 membro

4. **Programa de Pesquisa em Sustentabilidade** (ID: 4)
   - Tipo: PROGRAM
   - Coordenador: Patricia Almeida
   - 2 membros, 1 estudante

5. **Projeto de Monitoramento Ambiental** (ID: 5)
   - Tipo: PROJECT
   - Coordenador: Roberto Souza
   - Parent: Programa de Pesquisa em Sustentabilidade
   - 1 membro, 1 estudante

### Pessoas Disponíveis

- Maria Silva (ID: 1)
- João Santos (ID: 2)
- Ana Costa (ID: 3)
- Carlos Rodrigues (ID: 4)
- Fernanda Lima (ID: 5)
- Patricia Almeida (ID: 6)
- Roberto Souza (ID: 7)
- Juliana Martins (ID: 8)
- E mais...

## 🎯 Cenários de Teste

### Cenário 1: Busca e Filtro
1. Abrir lista de iniciativas
2. Buscar "Programa"
3. Ver 2 resultados
4. Filtrar por tipo "PROGRAM"
5. Ver mesmos 2 resultados
6. Limpar filtros
7. Ver todas as 5 iniciativas

### Cenário 2: Ordenação
1. Ordenar por "Name (A-Z)"
2. Verificar ordem alfabética
3. Ordenar por "Name (Z-A)"
4. Verificar ordem reversa

### Cenário 3: Export
1. Filtrar iniciativas
2. Clicar em "Export"
3. Verificar arquivo CSV baixado
4. Abrir CSV e verificar dados

### Cenário 4: Responsividade
1. Abrir DevTools (F12)
2. Ativar modo mobile (Ctrl+Shift+M)
3. Testar em diferentes tamanhos
4. Verificar menu lateral colapsa
5. Verificar cards empilham verticalmente

### Cenário 5: Tema e Idioma
1. Clicar no ícone de sol/lua
2. Ver tema mudar
3. Verificar persistência (recarregar página)
4. Clicar no ícone de tradução
5. Mudar para Português
6. Ver textos em português
7. Verificar persistência

## 📝 Checklist de Funcionalidades

### Implementado ✅
- [x] Lista de iniciativas
- [x] Busca com debounce
- [x] Filtros (tipo, datas)
- [x] Ordenação
- [x] Paginação
- [x] Export CSV
- [x] Refresh
- [x] Loading states
- [x] Empty states
- [x] Error handling
- [x] Tema light/dark
- [x] Internacionalização
- [x] Navegação responsiva

### Pendente ⏳
- [ ] Detalhes da iniciativa
- [ ] Criar iniciativa
- [ ] Editar iniciativa
- [ ] Deletar iniciativa
- [ ] Gerenciar membros
- [ ] Gerenciar estudantes
- [ ] Visualizar hierarquia
- [ ] Importar CSV/ZIP
- [ ] Ver importações falhadas

## 🎓 Dicas de Teste

1. **Use o DevTools**: Sempre tenha o console aberto para ver erros

2. **Network Tab**: Veja as requisições HTTP sendo feitas

3. **Vue DevTools**: Instale a extensão para inspecionar componentes

4. **Teste Edge Cases**:
   - Lista vazia
   - Busca sem resultados
   - Filtros sem resultados
   - Erros de rede (parar o mock API)

5. **Teste Performance**:
   - Busca rápida (debounce funciona?)
   - Múltiplos filtros
   - Paginação com muitos itens

6. **Teste Responsividade**:
   - Mobile (320px)
   - Tablet (768px)
   - Desktop (1024px+)

## 📞 Suporte

Se encontrar problemas:

1. Verificar console do navegador
2. Verificar se mock API está rodando
3. Verificar documentação em `mock-api/README.md`
4. Verificar `SERVICES_AND_MOCK_API.md`

## ✨ Próximos Testes

Quando as próximas views forem implementadas:

1. **InitiativeDetailView**:
   - Ver todos os detalhes
   - Ver membros e estudantes
   - Ver grupos organizacionais
   - Ver histórico de coordenador

2. **InitiativeCreateView**:
   - Criar nova iniciativa
   - Validação de campos
   - Seleção de coordenador
   - Seleção de parent

3. **InitiativeEditView**:
   - Editar iniciativa existente
   - Atualizar campos
   - Salvar mudanças

4. **InitiativeImportView**:
   - Upload CSV
   - Upload ZIP
   - Ver progresso
   - Ver resultados

---

**Boa sorte com os testes!** 🚀

Se tudo funcionar, você está pronto para continuar o desenvolvimento!
