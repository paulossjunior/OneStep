# Frontend Vue 3 + TypeScript - Design Document

## Architecture Overview

### Domain-Driven Modular Architecture

The frontend follows a domain-driven architecture where each Django app is mapped to an independent frontend module. This ensures:
- **Separation of Concerns**: Each module handles its own domain logic
- **Scalability**: Modules can be developed and tested independently
- **Maintainability**: Clear boundaries between domains
- **Reusability**: Modules can be extracted to separate packages

### Module Structure

```
modules/{domain}/
├── api/              # API layer - HTTP requests
├── components/       # Domain-specific Vue components
├── composables/      # Domain-specific composition functions
├── router/           # Domain routes
├── stores/           # Domain state management
├── types/            # TypeScript types/interfaces
├── utils/            # Domain-specific utilities
├── views/            # Page components
└── index.ts          # Module public API exports
```

## Technology Stack

### Core Framework
- **Vue 3.4+**: Progressive JavaScript framework with Composition API
- **TypeScript 5.0+**: Type-safe development
- **Vite 5.0+**: Fast build tool and dev server

### State Management
- **Pinia**: Vue's official state management (for UI state)
- **TanStack Query**: Server state management with caching

### Routing
- **Vue Router 4**: Client-side routing with guards

### UI Framework
- **Vuetify 3** OR **PrimeVue 3**: Component library
- **TailwindCSS**: Utility-first CSS framework

### HTTP Client
- **Axios**: HTTP client with interceptors

### Forms & Validation
- **VeeValidate 4**: Form validation
- **Yup** or **Zod**: Schema validation


### Additional Libraries
- **date-fns**: Date manipulation
- **Chart.js + vue-chartjs**: Data visualization
- **VueUse**: Vue composition utilities
- **vue-i18n**: Internationalization

## Domain Modules

### 1. Core Module (`src/core/`)

**Purpose**: Shared functionality across all modules

**Components**:
- AppHeader, AppSidebar, AppFooter
- DataTable, SearchBar, FilterPanel, Pagination
- LoadingSpinner, ErrorBoundary, ConfirmDialog
- NotificationToast

**Composables**:
- useAuth: Authentication logic
- useFilters: Generic filtering
- usePagination: Pagination logic
- useNotifications: Toast notifications
- usePermissions: Permission checks
- useValidation: Form validation

**Stores**:
- auth: User authentication state
- ui: UI state (sidebar, theme, etc.)

### 2. Initiatives Module (`src/modules/initiatives/`)

**Purpose**: Manage research initiatives (programs, projects, events)

**Key Features**:
- CRUD operations for initiatives
- Hierarchical structure visualization
- Team member management
- CSV/ZIP bulk import
- Failed import tracking
- Coordinator change history

**Components**:
- InitiativeCard, InitiativeForm
- InitiativeHierarchy (tree view)
- InitiativeTimeline
- TeamMemberList, StudentList
- CoordinatorChangeHistory
- FailedImportList, BulkImportUploader

**API Endpoints**:
- GET /api/initiatives/
- POST /api/initiatives/
- GET /api/initiatives/{id}/
- PATCH /api/initiatives/{id}/
- DELETE /api/initiatives/{id}/
- GET /api/initiatives/{id}/hierarchy/
- POST /api/initiatives/{id}/add_team_member/
- POST /api/initiatives/{id}/remove_team_member/
- POST /api/initiatives/import/
- GET /api/initiatives/failed-imports/

### 3. Scholarships Module (`src/modules/scholarships/`)

**Purpose**: Manage student scholarships

**Key Features**:
- CRUD operations for scholarships
- Statistics dashboard
- CSV/ZIP bulk import
- Failed import tracking
- Duration and value calculations

**Components**:
- ScholarshipCard, ScholarshipForm
- ScholarshipStats (charts)
- ScholarshipImport
- FailedScholarshipImportList
- ValueCalculator, DurationDisplay

**API Endpoints**:
- GET /api/scholarships/
- POST /api/scholarships/
- GET /api/scholarships/{id}/
- PATCH /api/scholarships/{id}/
- DELETE /api/scholarships/{id}/
- GET /api/scholarships/statistics/
- POST /api/scholarships/import/
- GET /api/scholarships/failed-imports/

### 4. People Module (`src/modules/people/`)

**Purpose**: Manage people (coordinators, team members, students)

**Key Features**:
- CRUD operations for people
- Search functionality
- View person's initiatives
- Activity timeline

**Components**:
- PersonCard, PersonForm
- PersonSelector (autocomplete)
- PersonAvatar
- InitiativesList
- ActivityTimeline

**API Endpoints**:
- GET /api/people/
- POST /api/people/
- GET /api/people/{id}/
- PATCH /api/people/{id}/
- DELETE /api/people/{id}/
- GET /api/people/search/
- GET /api/people/{id}/initiatives/

### 5. Organizational Group Module (`src/modules/organizational_group/`)

**Purpose**: Manage organizational units, campuses, knowledge areas

**Key Features**:
- CRUD for organizational units
- Leadership management
- Campus management
- Knowledge area management
- CSV import for units

**Components**:
- OrganizationalUnitCard, OrganizationalUnitForm
- CampusCard, CampusSelector
- KnowledgeAreaCard, KnowledgeAreaSelector
- LeadershipHistory
- MemberList

**API Endpoints**:
- GET /api/organizational-units/
- POST /api/organizational-units/
- GET /api/organizational-units/{id}/
- POST /api/organizational-units/{id}/add_leader/
- POST /api/organizational-units/{id}/remove_leader/
- GET /api/campuses/
- GET /api/knowledge-areas/
- POST /api/organizational-units/import/

## State Management Strategy

### Pinia Stores (UI State)

Used for client-side state that doesn't come from the server:
- User preferences
- UI state (sidebar open/closed, theme)
- Form state
- Filters and search terms

Example:
```typescript
// src/modules/initiatives/stores/initiatives.store.ts
export const useInitiativesStore = defineStore('initiatives', () => {
  const filters = ref({
    search: '',
    type: '',
    campus: '',
    status: '',
  })

  function setFilters(newFilters) {
    filters.value = { ...filters.value, ...newFilters }
  }

  return { filters, setFilters }
})
```

### TanStack Query (Server State)

Used for server data with automatic caching, refetching, and synchronization:
- API data (initiatives, scholarships, people)
- Automatic cache invalidation
- Optimistic updates
- Background refetching

Example:
```typescript
// src/modules/initiatives/composables/useInitiatives.ts
export function useInitiatives() {
  const useInitiativesList = (filters) => {
    return useQuery({
      queryKey: ['initiatives', filters],
      queryFn: () => initiativesApi.list(filters.value),
      staleTime: 5 * 60 * 1000, // 5 minutes
    })
  }

  return { useInitiativesList }
}
```

## Routing Architecture

### Route Structure

```
/                           → Dashboard
/login                      → Login page
/initiatives                → Initiative list
/initiatives/create         → Create initiative
/initiatives/:id            → Initiative detail
/initiatives/:id/edit       → Edit initiative
/initiatives/import         → Import initiatives
/initiatives/failed-imports → Failed imports
/scholarships               → Scholarship list
/scholarships/create        → Create scholarship
/scholarships/:id           → Scholarship detail
/scholarships/statistics    → Scholarship stats
/people                     → People list
/people/:id                 → Person detail
/organizations              → Organization list
/organizations/units        → Organizational units
/organizations/campuses     → Campuses
/organizations/knowledge-areas → Knowledge areas
```

### Route Guards

```typescript
// src/core/router/guards.ts
export const authGuard = (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
}

export const permissionGuard = (to, from, next) => {
  const authStore = useAuthStore()
  const requiredPermission = to.meta.permission
  
  if (requiredPermission && !authStore.hasPermission(requiredPermission)) {
    next('/unauthorized')
  } else {
    next()
  }
}
```

## API Integration

### API Client Configuration

```typescript
// src/core/api/client.ts
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// Response interceptor - Handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      await authStore.refreshToken()
      return apiClient(error.config)
    }
    return Promise.reject(error)
  }
)
```

### Type-Safe API Calls

```typescript
// src/modules/initiatives/api/initiatives.api.ts
export const initiativesApi = {
  list: (params?: InitiativeFilters) => {
    return apiClient.get<PaginatedResponse<Initiative>>('/initiatives/', { params })
  },
  
  get: (id: number) => {
    return apiClient.get<Initiative>(`/initiatives/${id}/`)
  },
  
  create: (data: InitiativeCreate) => {
    return apiClient.post<Initiative>('/initiatives/', data)
  },
}
```

## Component Architecture

### Component Hierarchy

```
App.vue
├── DefaultLayout.vue
│   ├── AppHeader.vue
│   ├── AppSidebar.vue
│   └── RouterView
│       └── [Page Components]
│           ├── [Domain Components]
│           └── [Shared Components]
```

### Component Types

1. **Layout Components**: Page structure (Header, Sidebar, Footer)
2. **Page Components**: Route-level components (views)
3. **Feature Components**: Domain-specific components
4. **Shared Components**: Reusable across modules
5. **UI Components**: Generic UI elements

### Component Naming Convention

- PascalCase for component files: `InitiativeCard.vue`
- Prefix with domain for clarity: `InitiativeCard`, `ScholarshipForm`
- Use descriptive names: `InitiativeHierarchyTree` not `Tree`

## Form Handling

### VeeValidate Integration

```typescript
// Example form with validation
<script setup lang="ts">
import { useForm } from 'vee-validate'
import * as yup from 'yup'

const schema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  startDate: yup.date().required('Start date is required'),
})

const { handleSubmit, errors } = useForm({
  validationSchema: schema,
})

const onSubmit = handleSubmit((values) => {
  // Submit form
})
</script>
```

## Error Handling

### Error Boundary

```vue
<!-- src/core/components/ErrorBoundary.vue -->
<template>
  <div v-if="error" class="error-boundary">
    <h2>Something went wrong</h2>
    <p>{{ error.message }}</p>
    <button @click="reset">Try again</button>
  </div>
  <slot v-else />
</template>
```

### API Error Handling

```typescript
// Centralized error handling
export function handleApiError(error: any) {
  const { showError } = useNotifications()
  
  if (error.response) {
    // Server responded with error
    const message = error.response.data?.message || 'An error occurred'
    showError(message)
  } else if (error.request) {
    // Request made but no response
    showError('Network error. Please check your connection.')
  } else {
    // Something else happened
    showError('An unexpected error occurred')
  }
}
```

## Performance Optimization

### Code Splitting

```typescript
// Lazy load routes
const routes = [
  {
    path: '/initiatives',
    component: () => import('@/modules/initiatives/views/InitiativeListView.vue'),
  },
]
```

### Virtual Scrolling

```vue
<!-- For large lists -->
<template>
  <RecycleScroller
    :items="initiatives"
    :item-size="80"
    key-field="id"
  >
    <template #default="{ item }">
      <InitiativeCard :initiative="item" />
    </template>
  </RecycleScroller>
</template>
```

### Image Optimization

- Use WebP format with fallbacks
- Lazy load images below the fold
- Use responsive images with srcset

### Bundle Optimization

- Tree shaking unused code
- Minification in production
- Gzip compression
- CDN for static assets

## Testing Strategy

### Unit Tests (Vitest)

```typescript
// Test composable
describe('useInitiatives', () => {
  it('should fetch initiatives', async () => {
    const { useInitiativesList } = useInitiatives()
    const { data, isLoading } = useInitiativesList(ref({}))
    
    await waitFor(() => expect(isLoading.value).toBe(false))
    expect(data.value).toBeDefined()
  })
})
```

### Component Tests

```typescript
// Test component
describe('InitiativeCard', () => {
  it('should render initiative name', () => {
    const wrapper = mount(InitiativeCard, {
      props: { initiative: mockInitiative },
    })
    
    expect(wrapper.text()).toContain(mockInitiative.name)
  })
})
```

### E2E Tests (Playwright)

```typescript
// Test user flow
test('create initiative', async ({ page }) => {
  await page.goto('/initiatives/create')
  await page.fill('[name="name"]', 'Test Initiative')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL(/\/initiatives\/\d+/)
})
```

## Deployment

### Build Process

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Docker Deployment

```dockerfile
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Variables

```env
# .env.production
VITE_API_BASE_URL=https://api.onestep.com
VITE_APP_TITLE=OneStep
VITE_ENABLE_DEVTOOLS=false
```

## Security Considerations

1. **XSS Prevention**: Sanitize user inputs, use v-text instead of v-html
2. **CSRF Protection**: Include CSRF tokens in requests
3. **Secure Storage**: Use HttpOnly cookies for tokens
4. **Content Security Policy**: Restrict resource loading
5. **HTTPS Only**: Force secure connections in production
6. **Input Validation**: Validate on client and server
7. **Rate Limiting**: Prevent API abuse

## Accessibility (WCAG 2.1 AA)

1. **Semantic HTML**: Use proper HTML elements
2. **ARIA Labels**: Add labels for screen readers
3. **Keyboard Navigation**: All interactive elements accessible via keyboard
4. **Color Contrast**: Minimum 4.5:1 ratio for text
5. **Focus Management**: Visible focus indicators
6. **Alt Text**: Descriptive alt text for images
7. **Form Labels**: Associate labels with inputs

## Internationalization

```typescript
// src/core/i18n/index.ts
import { createI18n } from 'vue-i18n'

const i18n = createI18n({
  locale: 'pt-BR',
  fallbackLocale: 'en-US',
  messages: {
    'pt-BR': {
      initiatives: {
        title: 'Iniciativas',
        create: 'Criar Iniciativa',
      },
    },
    'en-US': {
      initiatives: {
        title: 'Initiatives',
        create: 'Create Initiative',
      },
    },
  },
})
```

## Monitoring & Analytics

1. **Error Tracking**: Sentry or similar
2. **Performance Monitoring**: Web Vitals
3. **User Analytics**: Google Analytics or Plausible
4. **API Monitoring**: Track API response times
5. **Bundle Analysis**: Analyze bundle size

## Documentation

1. **Component Documentation**: Storybook
2. **API Documentation**: TypeDoc
3. **User Guide**: Markdown docs
4. **Developer Guide**: README files
5. **Changelog**: Track version changes

## Future Enhancements

1. **PWA Support**: Offline functionality
2. **Real-time Updates**: WebSocket integration
3. **Advanced Search**: Elasticsearch integration
4. **Custom Reports**: Report builder
5. **Mobile Apps**: React Native or Flutter
6. **AI Features**: Predictive analytics
7. **Collaboration**: Real-time collaboration features
