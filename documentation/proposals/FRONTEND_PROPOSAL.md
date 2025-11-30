# OneStep Frontend Proposal - Vue 3 + TypeScript

## Executive Summary

A modern, responsive Single Page Application (SPA) built with Vue 3, TypeScript, and Composition API to consume the OneStep Django REST API. The frontend will provide intuitive interfaces for managing research initiatives, scholarships, people, and organizational groups.

## Technology Stack

### Core Framework
- **Vue 3.4+** - Progressive JavaScript framework with Composition API
- **TypeScript 5.0+** - Type-safe development
- **Vite 5.0+** - Fast build tool and dev server
- **Pinia** - State management (Vue's official store)
- **Vue Router 4** - Client-side routing

### UI Framework & Components
- **Vuetify 3** or **PrimeVue 3** - Material Design component library
- **TailwindCSS** - Utility-first CSS framework
- **Chart.js + vue-chartjs** - Data visualization
- **VueUse** - Collection of Vue composition utilities

### API & Data Management
- **Axios** - HTTP client with interceptors
- **TanStack Query (Vue Query)** - Server state management, caching
- **Zod** - Runtime type validation for API responses

### Forms & Validation
- **VeeValidate 4** - Form validation
- **Yup** or **Zod** - Schema validation

### Additional Tools
- **date-fns** - Date manipulation
- **vue-i18n** - Internationalization
- **unplugin-auto-import** - Auto-import Vue APIs
- **unplugin-vue-components** - Auto-import components

## Project Structure - Domain-Driven Modular Architecture

Each Django app is mapped to a frontend domain module with complete isolation and independence.

```
frontend/
├── public/
│   ├── favicon.ico
│   └── assets/
├── src/
│   ├── core/                      # Core/Shared module (maps to Django core app)
│   │   ├── api/
│   │   │   ├── client.ts         # Axios instance with interceptors
│   │   │   └── types.ts          # Shared API types
│   │   ├── components/           # Shared components
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   ├── AppFooter.vue
│   │   │   ├── DataTable.vue
│   │   │   ├── SearchBar.vue
│   │   │   ├── FilterPanel.vue
│   │   │   ├── Pagination.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   ├── ErrorBoundary.vue
│   │   │   ├── ConfirmDialog.vue
│   │   │   └── NotificationToast.vue
│   │   ├── composables/          # Shared composables
│   │   │   ├── useAuth.ts
│   │   │   ├── useFilters.ts
│   │   │   ├── usePagination.ts
│   │   │   ├── useNotifications.ts
│   │   │   ├── usePermissions.ts
│   │   │   └── useValidation.ts
│   │   ├── layouts/              # Layout components
│   │   │   ├── DefaultLayout.vue
│   │   │   ├── AuthLayout.vue
│   │   │   └── DashboardLayout.vue
│   │   ├── router/               # Core routing
│   │   │   ├── index.ts
│   │   │   └── guards.ts
│   │   ├── stores/               # Core stores
│   │   │   ├── auth.ts
│   │   │   └── ui.ts
│   │   ├── types/                # Shared types
│   │   │   ├── common.ts
│   │   │   ├── api.ts
│   │   │   └── enums.ts
│   │   ├── utils/                # Shared utilities
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   ├── helpers.ts
│   │   │   └── constants.ts
│   │   └── views/                # Core views
│   │       ├── DashboardView.vue
│   │       ├── LoginView.vue
│   │       └── NotFoundView.vue
│   │
│   ├── modules/                   # Domain modules (each maps to Django app)
│   │   │
│   │   ├── initiatives/          # Initiatives domain module
│   │   │   ├── api/
│   │   │   │   ├── initiatives.api.ts      # API endpoints
│   │   │   │   └── types.ts                # Initiative-specific types
│   │   │   ├── components/
│   │   │   │   ├── InitiativeCard.vue
│   │   │   │   ├── InitiativeForm.vue
│   │   │   │   ├── InitiativeHierarchy.vue
│   │   │   │   ├── InitiativeTimeline.vue
│   │   │   │   ├── InitiativeTypeSelector.vue
│   │   │   │   ├── TeamMemberList.vue
│   │   │   │   ├── StudentList.vue
│   │   │   │   ├── CoordinatorChangeHistory.vue
│   │   │   │   ├── FailedImportList.vue
│   │   │   │   └── BulkImportUploader.vue
│   │   │   ├── composables/
│   │   │   │   ├── useInitiatives.ts
│   │   │   │   ├── useInitiativeTypes.ts
│   │   │   │   ├── useInitiativeHierarchy.ts
│   │   │   │   ├── useInitiativeImport.ts
│   │   │   │   └── useFailedImports.ts
│   │   │   ├── router/
│   │   │   │   └── initiatives.routes.ts
│   │   │   ├── stores/
│   │   │   │   ├── initiatives.store.ts
│   │   │   │   └── initiativeTypes.store.ts
│   │   │   ├── types/
│   │   │   │   ├── initiative.types.ts
│   │   │   │   ├── initiativeType.types.ts
│   │   │   │   └── enums.ts
│   │   │   ├── utils/
│   │   │   │   ├── initiative.helpers.ts
│   │   │   │   └── hierarchy.helpers.ts
│   │   │   ├── views/
│   │   │   │   ├── InitiativeListView.vue
│   │   │   │   ├── InitiativeDetailView.vue
│   │   │   │   ├── InitiativeCreateView.vue
│   │   │   │   ├── InitiativeEditView.vue
│   │   │   │   ├── InitiativeImportView.vue
│   │   │   │   ├── FailedImportsView.vue
│   │   │   │   └── CoordinatorChangesView.vue
│   │   │   └── index.ts          # Module exports
│   │   │
│   │   ├── scholarships/         # Scholarships domain module
│   │   │   ├── api/
│   │   │   │   ├── scholarships.api.ts
│   │   │   │   └── types.ts
│   │   │   ├── components/
│   │   │   │   ├── ScholarshipCard.vue
│   │   │   │   ├── ScholarshipForm.vue
│   │   │   │   ├── ScholarshipStats.vue
│   │   │   │   ├── ScholarshipTypeSelector.vue
│   │   │   │   ├── ScholarshipImport.vue
│   │   │   │   ├── FailedScholarshipImportList.vue
│   │   │   │   ├── ValueCalculator.vue
│   │   │   │   └── DurationDisplay.vue
│   │   │   ├── composables/
│   │   │   │   ├── useScholarships.ts
│   │   │   │   ├── useScholarshipTypes.ts
│   │   │   │   ├── useScholarshipImport.ts
│   │   │   │   ├── useScholarshipStats.ts
│   │   │   │   └── useFailedScholarshipImports.ts
│   │   │   ├── router/
│   │   │   │   └── scholarships.routes.ts
│   │   │   ├── stores/
│   │   │   │   ├── scholarships.store.ts
│   │   │   │   └── scholarshipTypes.store.ts
│   │   │   ├── types/
│   │   │   │   ├── scholarship.types.ts
│   │   │   │   ├── scholarshipType.types.ts
│   │   │   │   └── enums.ts
│   │   │   ├── utils/
│   │   │   │   ├── scholarship.helpers.ts
│   │   │   │   └── value.calculators.ts
│   │   │   ├── views/
│   │   │   │   ├── ScholarshipListView.vue
│   │   │   │   ├── ScholarshipDetailView.vue
│   │   │   │   ├── ScholarshipCreateView.vue
│   │   │   │   ├── ScholarshipEditView.vue
│   │   │   │   ├── ScholarshipImportView.vue
│   │   │   │   ├── ScholarshipStatsView.vue
│   │   │   │   └── FailedScholarshipImportsView.vue
│   │   │   └── index.ts
│   │   │
│   │   ├── people/               # People domain module
│   │   │   ├── api/
│   │   │   │   ├── people.api.ts
│   │   │   │   └── types.ts
│   │   │   ├── components/
│   │   │   │   ├── PersonCard.vue
│   │   │   │   ├── PersonForm.vue
│   │   │   │   ├── PersonSelector.vue
│   │   │   │   ├── PersonAvatar.vue
│   │   │   │   ├── PersonEmailList.vue
│   │   │   │   ├── InitiativesList.vue
│   │   │   │   └── ActivityTimeline.vue
│   │   │   ├── composables/
│   │   │   │   ├── usePeople.ts
│   │   │   │   ├── usePersonSearch.ts
│   │   │   │   └── usePersonInitiatives.ts
│   │   │   ├── router/
│   │   │   │   └── people.routes.ts
│   │   │   ├── stores/
│   │   │   │   └── people.store.ts
│   │   │   ├── types/
│   │   │   │   ├── person.types.ts
│   │   │   │   └── enums.ts
│   │   │   ├── utils/
│   │   │   │   └── person.helpers.ts
│   │   │   ├── views/
│   │   │   │   ├── PeopleListView.vue
│   │   │   │   ├── PersonDetailView.vue
│   │   │   │   ├── PersonCreateView.vue
│   │   │   │   └── PersonEditView.vue
│   │   │   └── index.ts
│   │   │
│   │   └── organizational_group/  # Organizational Group domain module
│   │       ├── api/
│   │       │   ├── organizations.api.ts
│   │       │   ├── campuses.api.ts
│   │       │   ├── knowledgeAreas.api.ts
│   │       │   ├── organizationalUnits.api.ts
│   │       │   └── types.ts
│   │       ├── components/
│   │       │   ├── OrganizationCard.vue
│   │       │   ├── OrganizationForm.vue
│   │       │   ├── OrganizationalUnitCard.vue
│   │       │   ├── OrganizationalUnitForm.vue
│   │       │   ├── CampusCard.vue
│   │       │   ├── CampusSelector.vue
│   │       │   ├── KnowledgeAreaCard.vue
│   │       │   ├── KnowledgeAreaSelector.vue
│   │       │   ├── LeadershipHistory.vue
│   │       │   ├── MemberList.vue
│   │       │   └── UnitImportUploader.vue
│   │       ├── composables/
│   │       │   ├── useOrganizations.ts
│   │       │   ├── useCampuses.ts
│   │       │   ├── useKnowledgeAreas.ts
│   │       │   ├── useOrganizationalUnits.ts
│   │       │   ├── useLeadership.ts
│   │       │   └── useUnitImport.ts
│   │       ├── router/
│   │       │   └── organizational.routes.ts
│   │       ├── stores/
│   │       │   ├── organizations.store.ts
│   │       │   ├── campuses.store.ts
│   │       │   ├── knowledgeAreas.store.ts
│   │       │   └── organizationalUnits.store.ts
│   │       ├── types/
│   │       │   ├── organization.types.ts
│   │       │   ├── campus.types.ts
│   │       │   ├── knowledgeArea.types.ts
│   │       │   ├── organizationalUnit.types.ts
│   │       │   └── enums.ts
│   │       ├── utils/
│   │       │   └── organizational.helpers.ts
│   │       ├── views/
│   │       │   ├── OrganizationListView.vue
│   │       │   ├── OrganizationDetailView.vue
│   │       │   ├── OrganizationalUnitListView.vue
│   │       │   ├── OrganizationalUnitDetailView.vue
│   │       │   ├── OrganizationalUnitCreateView.vue
│   │       │   ├── OrganizationalUnitEditView.vue
│   │       │   ├── OrganizationalUnitImportView.vue
│   │       │   ├── CampusListView.vue
│   │       │   ├── CampusDetailView.vue
│   │       │   ├── KnowledgeAreaListView.vue
│   │       │   └── KnowledgeAreaDetailView.vue
│   │       └── index.ts
│   │
│   ├── assets/                    # Global static assets
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   │       ├── main.css
│   │       ├── variables.css
│   │       └── themes/
│   │
│   ├── App.vue
│   └── main.ts
│
├── .env.development
├── .env.production
├── .eslintrc.js
├── .prettierrc
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### Module Structure Explanation

Each domain module follows this structure:

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

### Module Independence

Each module is:
- **Self-contained**: All domain logic within the module
- **Independently testable**: Can be tested in isolation
- **Loosely coupled**: Minimal dependencies on other modules
- **Reusable**: Can be extracted to separate package if needed

## Key Features by Module

### 1. Authentication & Authorization
- JWT token-based authentication
- Login/logout functionality
- Token refresh mechanism
- Role-based access control (RBAC)
- Protected routes

### 2. Dashboard
- **Overview Statistics**
  - Total initiatives, scholarships, people
  - Active vs completed initiatives
  - Scholarship funding summary
- **Recent Activity Feed**
- **Quick Actions** (Create Initiative, Add Scholarship, etc.)
- **Charts & Visualizations**
  - Initiatives by type (pie chart)
  - Scholarships by campus (bar chart)
  - Timeline of initiatives (Gantt chart)

### 3. Initiatives Management
- **List View**
  - Filterable table (by type, campus, coordinator, status)
  - Search functionality
  - Sortable columns
  - Pagination
  - Bulk actions
- **Detail View**
  - Initiative information
  - Hierarchical structure visualization (tree view)
  - Team members management
  - Students list
  - Associated organizations
  - Knowledge areas
  - Timeline visualization
  - Coordinator change history
- **Create/Edit Forms**
  - Multi-step form wizard
  - Validation with real-time feedback
  - Auto-complete for coordinators
  - Campus selector
  - Parent initiative selector (with hierarchy preview)
- **CSV Import**
  - Drag & drop file upload
  - Bulk ZIP import support
  - Import progress tracking
  - Error reporting with row details
  - Failed imports management

### 4. Scholarships Management
- **List View**
  - Filterable table (by type, campus, supervisor, status)
  - Search by student/supervisor
  - Date range filters
  - Value range filters
- **Detail View**
  - Scholarship details
  - Student information
  - Supervisor information
  - Initiative linkage
  - Duration calculator
  - Total value display
  - Status indicator (active/completed)
- **Create/Edit Forms**
  - Student selector with search
  - Supervisor selector
  - Initiative linkage
  - Value calculator
  - Date pickers with validation
- **CSV Import**
  - Similar to initiatives import
  - Bulk processing
  - Error tracking
- **Statistics Dashboard**
  - Total funding by campus
  - Scholarships by type
  - Active scholarships timeline

### 5. People Management
- **List View**
  - Searchable directory
  - Filter by role (coordinator, team member, student)
  - Email verification status
- **Detail View**
  - Personal information
  - Coordinated initiatives
  - Team initiatives
  - Student initiatives
  - Activity timeline
- **Create/Edit Forms**
  - Email validation
  - Duplicate detection
  - Contact information

### 6. Organizations Management
- **Organizational Units**
  - List with campus grouping
  - Knowledge area filtering
  - Type filtering (Research, Extension)
  - Leadership history
  - Member management
- **Campuses**
  - Campus directory
  - Units by campus
  - Statistics
- **Knowledge Areas**
  - Area directory
  - Associated units and initiatives

### 7. Reports & Analytics
- **Initiative Reports**
  - Initiatives by type/campus/status
  - Team size distribution
  - Duration analysis
  - Hierarchy depth analysis
- **Scholarship Reports**
  - Funding by campus/type/sponsor
  - Student distribution
  - Duration and value analysis
- **Export Options**
  - PDF reports
  - Excel exports
  - CSV downloads

## Domain Module Examples

### Module Index Pattern

Each module exports its public API through `index.ts`:

```typescript
// src/modules/initiatives/index.ts
export * from './api/initiatives.api'
export * from './types/initiative.types'
export * from './composables/useInitiatives'
export * from './stores/initiatives.store'

// Named exports for components (lazy-loaded)
export { default as InitiativeCard } from './components/InitiativeCard.vue'
export { default as InitiativeForm } from './components/InitiativeForm.vue'

// Route registration
export { default as initiativesRoutes } from './router/initiatives.routes'
```

### Cross-Module Communication

Modules communicate through:
1. **Shared Core Services** (auth, notifications)
2. **Event Bus** (for loosely coupled events)
3. **Direct API calls** (when needed)

```typescript
// Example: People module using Initiatives data
import { useInitiatives } from '@/modules/initiatives'
import { usePeople } from '@/modules/people'

const { getPersonInitiatives } = usePeople()
const { useInitiativesList } = useInitiatives()
```

## API Integration Architecture

### Core API Client Setup

```typescript
// src/core/api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - Handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401) {
      // Token expired - attempt refresh
      try {
        await authStore.refreshToken()
        // Retry original request
        return apiClient(error.config)
      } catch {
        // Refresh failed - logout
        authStore.logout()
        router.push('/login')
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
```

### Domain-Specific API Endpoints

#### Initiatives Module API

```typescript
// src/modules/initiatives/api/initiatives.api.ts
import apiClient from '@/core/api/client'
import type { 
  Initiative, 
  InitiativeCreate, 
  InitiativeUpdate,
  InitiativeFilters 
} from '../types/initiative.types'
import type { PaginatedResponse } from '@/core/types/api'

export const initiativesApi = {
  // List initiatives with filters
  list: (params?: {
    page?: number
    page_size?: number
    search?: string
    type?: string
    campus?: string
    coordinator?: string
  }) => {
    return apiClient.get<PaginatedResponse<Initiative>>('/initiatives/', { params })
  },

  // Get single initiative
  get: (id: number) => {
    return apiClient.get<Initiative>(`/initiatives/${id}/`)
  },

  // Create initiative
  create: (data: InitiativeCreate) => {
    return apiClient.post<Initiative>('/initiatives/', data)
  },

  // Update initiative
  update: (id: number, data: InitiativeUpdate) => {
    return apiClient.patch<Initiative>(`/initiatives/${id}/`, data)
  },

  // Delete initiative
  delete: (id: number) => {
    return apiClient.delete(`/initiatives/${id}/`)
  },

  // Get hierarchy
  getHierarchy: (id: number) => {
    return apiClient.get<Initiative>(`/initiatives/${id}/hierarchy/`)
  },

  // Add team member
  addTeamMember: (id: number, personId: number) => {
    return apiClient.post(`/initiatives/${id}/add_team_member/`, { person_id: personId })
  },

  // Remove team member
  removeTeamMember: (id: number, personId: number) => {
    return apiClient.post(`/initiatives/${id}/remove_team_member/`, { person_id: personId })
  },

  // CSV Import
  importCSV: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/initiatives/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // Bulk ZIP Import
  importBulk: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/initiatives/import-bulk/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}
```

#### Scholarships Module API

```typescript
// src/modules/scholarships/api/scholarships.api.ts
import apiClient from '@/core/api/client'
import type { 
  Scholarship, 
  ScholarshipCreate, 
  ScholarshipUpdate,
  ScholarshipFilters 
} from '../types/scholarship.types'
import type { PaginatedResponse } from '@/core/types/api'

export const scholarshipsApi = {
  list: (params?: ScholarshipFilters) => {
    return apiClient.get<PaginatedResponse<Scholarship>>('/scholarships/', { params })
  },

  get: (id: number) => {
    return apiClient.get<Scholarship>(`/scholarships/${id}/`)
  },

  create: (data: ScholarshipCreate) => {
    return apiClient.post<Scholarship>('/scholarships/', data)
  },

  update: (id: number, data: ScholarshipUpdate) => {
    return apiClient.patch<Scholarship>(`/scholarships/${id}/`, data)
  },

  delete: (id: number) => {
    return apiClient.delete(`/scholarships/${id}/`)
  },

  statistics: () => {
    return apiClient.get('/scholarships/statistics/')
  },

  importCSV: (file: File) => {
    const formData = new FormData()
    formData.append('csv_file', file)
    return apiClient.post('/scholarships/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  getFailedImports: (params?: { resolved?: boolean }) => {
    return apiClient.get('/scholarships/failed-imports/', { params })
  },
}
```

#### People Module API

```typescript
// src/modules/people/api/people.api.ts
import apiClient from '@/core/api/client'
import type { Person, PersonCreate, PersonUpdate } from '../types/person.types'
import type { PaginatedResponse } from '@/core/types/api'

export const peopleApi = {
  list: (params?: { search?: string; page?: number }) => {
    return apiClient.get<PaginatedResponse<Person>>('/people/', { params })
  },

  get: (id: number) => {
    return apiClient.get<Person>(`/people/${id}/`)
  },

  create: (data: PersonCreate) => {
    return apiClient.post<Person>('/people/', data)
  },

  update: (id: number, data: PersonUpdate) => {
    return apiClient.patch<Person>(`/people/${id}/`, data)
  },

  delete: (id: number) => {
    return apiClient.delete(`/people/${id}/`)
  },

  search: (query: string) => {
    return apiClient.get<Person[]>(`/people/search/?q=${query}`)
  },

  getInitiatives: (id: number) => {
    return apiClient.get(`/people/${id}/initiatives/`)
  },
}
```

#### Organizational Group Module API

```typescript
// src/modules/organizational_group/api/organizationalUnits.api.ts
import apiClient from '@/core/api/client'
import type { 
  OrganizationalUnit, 
  OrganizationalUnitCreate,
  OrganizationalUnitUpdate 
} from '../types/organizationalUnit.types'
import type { PaginatedResponse } from '@/core/types/api'

export const organizationalUnitsApi = {
  list: (params?: { campus?: string; type?: string; knowledge_area?: string }) => {
    return apiClient.get<PaginatedResponse<OrganizationalUnit>>('/organizational-units/', { params })
  },

  get: (id: number) => {
    return apiClient.get<OrganizationalUnit>(`/organizational-units/${id}/`)
  },

  create: (data: OrganizationalUnitCreate) => {
    return apiClient.post<OrganizationalUnit>('/organizational-units/', data)
  },

  update: (id: number, data: OrganizationalUnitUpdate) => {
    return apiClient.patch<OrganizationalUnit>(`/organizational-units/${id}/`, data)
  },

  delete: (id: number) => {
    return apiClient.delete(`/organizational-units/${id}/`)
  },

  addLeader: (id: number, personId: number, startDate: string) => {
    return apiClient.post(`/organizational-units/${id}/add_leader/`, { 
      person_id: personId,
      start_date: startDate 
    })
  },

  removeLeader: (id: number, personId: number, endDate: string) => {
    return apiClient.post(`/organizational-units/${id}/remove_leader/`, { 
      person_id: personId,
      end_date: endDate 
    })
  },

  getCurrentLeaders: (id: number) => {
    return apiClient.get(`/organizational-units/${id}/current_leaders/`)
  },

  getLeadershipHistory: (id: number) => {
    return apiClient.get(`/organizational-units/${id}/leadership_history/`)
  },

  importCSV: (file: File) => {
    const formData = new FormData()
    formData.append('csv_file', file)
    return apiClient.post('/organizational-units/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}

// src/modules/organizational_group/api/campuses.api.ts
export const campusesApi = {
  list: () => apiClient.get('/campuses/'),
  get: (id: number) => apiClient.get(`/campuses/${id}/`),
  create: (data: any) => apiClient.post('/campuses/', data),
  update: (id: number, data: any) => apiClient.patch(`/campuses/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/campuses/${id}/`),
}

// src/modules/organizational_group/api/knowledgeAreas.api.ts
export const knowledgeAreasApi = {
  list: () => apiClient.get('/knowledge-areas/'),
  get: (id: number) => apiClient.get(`/knowledge-areas/${id}/`),
  create: (data: any) => apiClient.post('/knowledge-areas/', data),
  update: (id: number, data: any) => apiClient.patch(`/knowledge-areas/${id}/`, data),
  delete: (id: number) => apiClient.delete(`/knowledge-areas/${id}/`),
}
```

### Domain Composables

#### Initiatives Module Composable

```typescript
// src/modules/initiatives/composables/useInitiatives.ts
import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { initiativesApi } from '../api/initiatives.api'
import { useNotifications } from '@/core/composables/useNotifications'
import type { Initiative, InitiativeCreate } from '../types/initiative.types'

export function useInitiatives() {
  const queryClient = useQueryClient()
  const { showSuccess, showError } = useNotifications()

  // List initiatives with caching
  const useInitiativesList = (filters = ref({})) => {
    return useQuery({
      queryKey: ['initiatives', filters],
      queryFn: () => initiativesApi.list(filters.value),
      staleTime: 5 * 60 * 1000, // 5 minutes
    })
  }

  // Get single initiative
  const useInitiative = (id: Ref<number>) => {
    return useQuery({
      queryKey: ['initiative', id],
      queryFn: () => initiativesApi.get(id.value),
      enabled: computed(() => !!id.value),
    })
  }

  // Create initiative mutation
  const createInitiative = useMutation({
    mutationFn: (data: InitiativeCreate) => initiativesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] })
      showSuccess('Initiative created successfully')
    },
    onError: (error) => {
      showError('Failed to create initiative')
    },
  })

  // Update initiative mutation
  const updateInitiative = useMutation({
    mutationFn: ({ id, data }: { id: number; data: InitiativeUpdate }) =>
      initiativesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] })
      queryClient.invalidateQueries({ queryKey: ['initiative', variables.id] })
      showSuccess('Initiative updated successfully')
    },
    onError: () => {
      showError('Failed to update initiative')
    },
  })

  // Delete initiative mutation
  const deleteInitiative = useMutation({
    mutationFn: (id: number) => initiativesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['initiatives'] })
      showSuccess('Initiative deleted successfully')
    },
    onError: () => {
      showError('Failed to delete initiative')
    },
  })

  return {
    useInitiativesList,
    useInitiative,
    createInitiative,
    updateInitiative,
    deleteInitiative,
  }
}
```

## UI/UX Design Principles

### 1. Responsive Design
- Mobile-first approach
- Breakpoints: 320px, 768px, 1024px, 1440px
- Touch-friendly interactions
- Adaptive layouts

### 2. Performance Optimization
- Code splitting by route
- Lazy loading components
- Virtual scrolling for large lists
- Image optimization
- API response caching
- Debounced search inputs

### 3. Accessibility (WCAG 2.1 AA)
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support
- Color contrast compliance
- Focus management

### 4. User Experience
- Loading states with skeletons
- Optimistic UI updates
- Error boundaries
- Toast notifications
- Confirmation dialogs for destructive actions
- Breadcrumb navigation
- Contextual help tooltips

## State Management Strategy

### Pinia Stores

```typescript
// src/stores/initiatives.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Initiative } from '@/types/models'

export const useInitiativesStore = defineStore('initiatives', () => {
  // State
  const initiatives = ref<Initiative[]>([])
  const selectedInitiative = ref<Initiative | null>(null)
  const filters = ref({
    search: '',
    type: '',
    campus: '',
    status: '',
  })

  // Getters
  const filteredInitiatives = computed(() => {
    return initiatives.value.filter(initiative => {
      // Apply filters
      if (filters.value.search && !initiative.name.toLowerCase().includes(filters.value.search.toLowerCase())) {
        return false
      }
      if (filters.value.type && initiative.type !== filters.value.type) {
        return false
      }
      // ... more filters
      return true
    })
  })

  const activeInitiatives = computed(() => {
    return initiatives.value.filter(i => i.status === 'active')
  })

  // Actions
  function setFilters(newFilters: Partial<typeof filters.value>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function clearFilters() {
    filters.value = {
      search: '',
      type: '',
      campus: '',
      status: '',
    }
  }

  return {
    initiatives,
    selectedInitiative,
    filters,
    filteredInitiatives,
    activeInitiatives,
    setFilters,
    clearFilters,
  }
})
```

## Routing Structure

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { layout: 'auth' },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/dashboard/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/initiatives',
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'initiatives-list',
          component: () => import('@/views/initiatives/InitiativeListView.vue'),
        },
        {
          path: 'create',
          name: 'initiatives-create',
          component: () => import('@/views/initiatives/InitiativeCreateView.vue'),
        },
        {
          path: ':id',
          name: 'initiatives-detail',
          component: () => import('@/views/initiatives/InitiativeDetailView.vue'),
        },
        {
          path: ':id/edit',
          name: 'initiatives-edit',
          component: () => import('@/views/initiatives/InitiativeEditView.vue'),
        },
        {
          path: 'import',
          name: 'initiatives-import',
          component: () => import('@/views/initiatives/InitiativeImportView.vue'),
        },
      ],
    },
    // Similar structure for scholarships, people, organizations
  ],
})

router.beforeEach(authGuard)

export default router
```

## Development Workflow

### 1. Setup & Installation
```bash
# Create project
npm create vite@latest onestep-frontend -- --template vue-ts

# Install dependencies
npm install vue-router@4 pinia axios @tanstack/vue-query
npm install -D @types/node

# Install UI framework (choose one)
npm install vuetify@next  # OR
npm install primevue primeicons

# Install utilities
npm install date-fns zod vee-validate yup
npm install @vueuse/core vue-i18n
```

### 2. Environment Configuration
```env
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=OneStep - Development
VITE_ENABLE_DEVTOOLS=true

# .env.production
VITE_API_BASE_URL=https://api.onestep.com
VITE_APP_TITLE=OneStep
VITE_ENABLE_DEVTOOLS=false
```

### 3. Build & Deployment
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## Testing Strategy

### Unit Tests (Vitest)
- Component testing
- Composable testing
- Store testing
- Utility function testing

### E2E Tests (Playwright)
- Critical user flows
- Form submissions
- Navigation
- Authentication

### API Integration Tests
- Mock API responses
- Error handling
- Loading states

## Deployment Options

### 1. Static Hosting
- **Vercel** - Zero-config deployment
- **Netlify** - Continuous deployment
- **AWS S3 + CloudFront** - Scalable CDN

### 2. Docker Container
```dockerfile
# Dockerfile
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

### 3. Integration with Django
- Serve from Django static files
- Reverse proxy with Nginx
- Separate domains with CORS

## Performance Targets

- **First Contentful Paint (FCP)**: < 1.5s
- **Time to Interactive (TTI)**: < 3.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **Bundle Size**: < 500KB (gzipped)

## Security Considerations

1. **XSS Prevention**: Sanitize user inputs
2. **CSRF Protection**: Use Django CSRF tokens
3. **Secure Storage**: HttpOnly cookies for tokens
4. **Content Security Policy**: Restrict resource loading
5. **HTTPS Only**: Force secure connections
6. **Input Validation**: Client and server-side
7. **Rate Limiting**: Prevent API abuse

## Internationalization (i18n)

Support for multiple languages:
- Portuguese (pt-BR) - Primary
- English (en-US)
- Spanish (es-ES)

## Browser Support

- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Timeline Estimate

### Phase 1: Foundation (2-3 weeks)
- Project setup
- Authentication
- Basic routing
- API client
- Core components

### Phase 2: Initiatives Module (2-3 weeks)
- List/detail/create/edit views
- Hierarchy visualization
- Team management
- CSV import

### Phase 3: Scholarships Module (2 weeks)
- CRUD operations
- Statistics dashboard
- CSV import

### Phase 4: People & Organizations (2 weeks)
- People management
- Organization management
- Campus and knowledge areas

### Phase 5: Dashboard & Reports (1-2 weeks)
- Dashboard with statistics
- Charts and visualizations
- Report generation

### Phase 6: Polish & Testing (1-2 weeks)
- UI/UX refinements
- Performance optimization
- Testing
- Documentation

**Total Estimated Time: 10-14 weeks**

## Conclusion

This Vue 3 + TypeScript frontend will provide a modern, performant, and user-friendly interface for the OneStep platform. The architecture is scalable, maintainable, and follows industry best practices for enterprise applications.

### Key Benefits:
- ✅ Type-safe development with TypeScript
- ✅ Reactive and performant with Vue 3 Composition API
- ✅ Efficient state management with Pinia
- ✅ Smart caching with TanStack Query
- ✅ Responsive and accessible UI
- ✅ Comprehensive CSV import with error handling
- ✅ Real-time data synchronization
- ✅ Modular and maintainable codebase

### Next Steps:
1. Review and approve architecture
2. Set up development environment
3. Create design mockups/wireframes
4. Begin Phase 1 implementation
5. Establish CI/CD pipeline
6. Set up staging environment
