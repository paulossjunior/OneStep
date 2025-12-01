# OneStep Frontend

Modern Single Page Application built with Vue 3, TypeScript, and Composition API.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test:unit

# Lint and format
npm run lint
npm run format
```

## 📁 Project Structure

```
src/
├── core/                    # Core module (shared functionality)
│   ├── api/                # API client and utilities
│   ├── components/         # Shared components
│   ├── composables/        # Shared composables
│   ├── layouts/            # Layout components
│   ├── router/             # Vue Router configuration
│   ├── stores/             # Pinia stores
│   ├── types/              # TypeScript types
│   ├── utils/              # Utility functions
│   └── views/              # Core views (Dashboard, Login, etc.)
├── modules/                # Domain modules
│   ├── initiatives/        # Initiatives module
│   ├── scholarships/       # Scholarships module
│   ├── people/             # People module
│   └── organizational_group/ # Organizational Group module
├── assets/                 # Static assets
├── plugins/                # Vue plugins configuration
├── App.vue                 # Root component
└── main.ts                 # Application entry point
```

## 🛠️ Technology Stack

- **Vue 3.4+** - Progressive JavaScript framework
- **TypeScript 5.0+** - Type-safe development
- **Vite 5.0+** - Fast build tool
- **Pinia** - State management
- **TanStack Query** - Server state management
- **Vue Router 4** - Routing
- **Vuetify 3** - UI component library
- **TailwindCSS** - Utility-first CSS
- **Axios** - HTTP client
- **VeeValidate** - Form validation
- **Chart.js** - Data visualization
- **vue-i18n** - Internationalization

## 📝 Development Guidelines

### Code Style

- Use TypeScript strict mode
- Follow Vue 3 Composition API patterns
- Use `<script setup>` syntax
- Follow ESLint and Prettier rules

### Component Naming

- PascalCase for component files: `InitiativeCard.vue`
- Prefix with domain: `InitiativeCard`, `ScholarshipForm`
- Use descriptive names

### State Management

- **Pinia**: For UI state (filters, preferences)
- **TanStack Query**: For server state (API data)

### API Calls

- Use composables for data fetching
- Implement proper error handling
- Use TypeScript interfaces for responses

## 🧪 Testing

```bash
# Run unit tests
npm run test:unit

# Run E2E tests
npm run test:e2e

# Type checking
npm run type-check
```

## 🌐 Environment Variables

Create `.env.local` for local overrides:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=OneStep - Local
```

## 📚 Documentation

- [Requirements](./.kiro/specs/frontend-vue3-typescript/requirements.md)
- [Design](./.kiro/specs/frontend-vue3-typescript/design.md)
- [Tasks](./.kiro/specs/frontend-vue3-typescript/tasks.md)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## 📄 License

This project is part of the OneStep platform.

## Implementation Status

### ✅ Phase 1: Foundation & Setup (Complete)
- Project initialization and configuration
- Core API client with interceptors
- Authentication system with JWT
- Layout components (Default, Auth)
- Shared components (DataTable, SearchBar, FilterPanel, etc.)
- Core composables (useAuth, useFilters, usePagination, etc.)
- Router with guards and lazy loading
- Internationalization (English, Portuguese)

### ✅ Phase 2: Initiatives Module (Complete)
- Full CRUD operations for initiatives
- Initiative hierarchy visualization
- Team member and student management
- Bulk import (CSV/ZIP)
- Failed import management
- Coordinator change history
- Search, filters, and pagination
- 9 components, 6 views, 6 routes
- See `documentation/PHASE2_COMPLETE.md` for details

### 🔜 Next Steps
1. **Phase 3**: Scholarships Module
2. **Phase 4**: People & Organizations
3. **Phase 5**: Dashboard & Reports
4. **Phase 6**: Polish & Testing
5. **Phase 7**: Deployment

## Quick Start

```bash
# Install dependencies
npm install

# Start mock API (in one terminal)
npm run mock-api

# Start dev server (in another terminal)
npm run dev

# Login credentials
# Username: admin
# Password: admin123
```

## Documentation

- [Phase 2 Complete](./documentation/PHASE2_COMPLETE.md) - Full implementation details
- [Testing Guide](./documentation/TESTING_PHASE2.md) - How to test Phase 2 features
- [Services & Mock API](./documentation/SERVICES_AND_MOCK_API.md) - API documentation
- [Mock API Auth Guide](./documentation/MOCK_API_AUTH_GUIDE.md) - Authentication details
