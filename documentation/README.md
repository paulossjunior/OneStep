# OneStep - Documentação

Documentação completa do projeto OneStep.

## 📚 Estrutura da Documentação

```
documentation/
├── specs/              # Especificações técnicas
│   ├── frontend-vue3-typescript/  # Spec do frontend
│   └── ...
├── api/                # Documentação da API
├── guides/             # Guias de uso e desenvolvimento
├── proposals/          # Propostas e RFCs
└── architecture/       # Diagramas e arquitetura
```

## 📖 Índice

### Especificações

#### Frontend Vue 3 + TypeScript
- [README](./specs/frontend-vue3-typescript/README.md)
- [Requirements](./specs/frontend-vue3-typescript/requirements.md) - 60+ user stories
- [Design](./specs/frontend-vue3-typescript/design.md) - Arquitetura detalhada
- [Tasks](./specs/frontend-vue3-typescript/tasks.md) - Plano de implementação
- [Index](./specs/frontend-vue3-typescript/index.md) - Navegação rápida

### Propostas

- [Frontend Proposal](./proposals/FRONTEND_PROPOSAL.md) - Proposta original do frontend
- [Frontend Spec Summary](./proposals/FRONTEND_SPEC_SUMMARY.md) - Resumo executivo

### API

- [API Documentation](./api/) - Documentação completa da API REST
- [OpenAPI Schema](./api/schema/) - Especificação OpenAPI/Swagger

### Guias

- [Guias de Desenvolvimento](./guides/) - Como desenvolver no projeto
- [Guias de Deploy](./guides/) - Como fazer deploy
- [Guias de Uso](./guides/) - Como usar o sistema

## 🎯 Visão Geral do Projeto

### OneStep

Sistema de gestão de iniciativas de pesquisa, bolsas de estudo e grupos organizacionais.

**Componentes:**
- **Backend**: Django REST API
- **Frontend**: Vue 3 + TypeScript SPA
- **Database**: PostgreSQL
- **Analytics**: Apache Superset (opcional)

### Funcionalidades Principais

1. **Gestão de Iniciativas**
   - Programas, projetos e eventos
   - Estrutura hierárquica
   - Gerenciamento de equipe
   - Importação em massa (CSV/ZIP)

2. **Gestão de Bolsas**
   - Bolsas de estudo
   - Estatísticas e relatórios
   - Importação em massa

3. **Gestão de Pessoas**
   - Coordenadores, membros, estudantes
   - Busca e filtros
   - Histórico de atividades

4. **Gestão Organizacional**
   - Unidades organizacionais
   - Campi
   - Áreas de conhecimento
   - Liderança

## 🏗️ Arquitetura

### Backend (Django)

```
Django REST API
├── Core (shared)
├── Initiatives (domain)
├── Scholarships (domain)
├── People (domain)
└── Organizational Group (domain)
```

### Frontend (Vue 3)

```
Vue 3 SPA
├── Core (shared)
├── Modules
│   ├── Initiatives
│   ├── Scholarships
│   ├── People
│   └── Organizational Group
```

### Arquitetura Domain-Driven

Cada Django app é mapeado para um módulo frontend independente:

```
Django App              →  Frontend Module
─────────────────────────────────────────────
apps/initiatives        →  modules/initiatives
apps/scholarships       →  modules/scholarships
apps/people             →  modules/people
apps/organizational_group → modules/organizational_group
```

## 📊 Diagramas

### Modelo de Dados

```mermaid
classDiagram
    class Initiative {
        +String name
        +String description
        +Date start_date
        +Date end_date
        +String type
    }
    
    class Person {
        +String name
        +String email
    }
    
    class Scholarship {
        +Decimal value
        +Date start_date
        +Date end_date
    }
    
    Initiative ||--o{ Initiative : parent/child
    Initiative }o--|| Person : coordinator
    Initiative }o--o{ Person : team_members
    Scholarship }o--|| Person : student
    Scholarship }o--|| Person : supervisor
```

## 🚀 Quick Start

### Para Desenvolvedores

1. **Backend**: Ver [backend/README.md](../backend/README.md)
2. **Frontend**: Ver [frontend/README.md](../frontend/README.md)
3. **Specs**: Ver [specs/frontend-vue3-typescript/](./specs/frontend-vue3-typescript/)

### Para Product Managers

1. **Requirements**: Ver [specs/frontend-vue3-typescript/requirements.md](./specs/frontend-vue3-typescript/requirements.md)
2. **User Stories**: 60+ user stories organizadas por épico
3. **Timeline**: 10-14 semanas para frontend completo

### Para Designers

1. **Requirements**: Ver user stories para entender funcionalidades
2. **Design**: Ver [specs/frontend-vue3-typescript/design.md](./specs/frontend-vue3-typescript/design.md)
3. **Components**: Lista completa de componentes necessários

### Para QA

1. **Acceptance Criteria**: Ver user stories
2. **Testing Strategy**: Ver design document
3. **Test Plans**: Criar baseado nos critérios de aceitação

## 📝 Convenções

### Commits

```
feat: adiciona nova funcionalidade
fix: corrige bug
docs: atualiza documentação
style: formatação de código
refactor: refatoração
test: adiciona testes
chore: tarefas de manutenção
```

### Branches

```
main          - Produção
develop       - Desenvolvimento
feature/*     - Novas funcionalidades
bugfix/*      - Correções de bugs
hotfix/*      - Correções urgentes
release/*     - Preparação de release
```

## 🔗 Links Úteis

- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [API Schema](http://localhost:8000/api/schema/)
- [Admin Interface](http://localhost:8000/admin/)
- [Frontend Dev](http://localhost:3000/)

## 📞 Suporte

Para questões sobre a documentação:
1. Verifique o documento relevante
2. Consulte os guias
3. Entre em contato com o tech lead

---

**Última Atualização**: 2024-11-30  
**Versão**: 1.0
