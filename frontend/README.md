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

## Phase 1 Status

### ✅ Completed
- Project initialization
- Configuration files
- Package.json with all dependencies
- TypeScript configuration
- ESLint and Prettier setup
- Vite configuration
- TailwindCSS setup
- Environment files
- Basic folder structure

### 🚧 In Progress
- Core API client
- Authentication module
- Layout components
- Shared components
- Core composables
- Router setup

### 📋 Next Steps
1. Run `npm install` to install dependencies
2. Create remaining Phase 1 files (see PHASE1_IMPLEMENTATION_GUIDE.md)
3. Test the foundation
4. Proceed to Phase 2
