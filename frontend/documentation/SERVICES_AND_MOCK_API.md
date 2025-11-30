# Services, Handlers & Mock API - Implementation Complete

**Date**: November 30, 2024  
**Status**: ✅ Complete

## Overview

Implemented comprehensive service layer, handlers, and mock backend for testing the frontend without depending on the Django backend.

## 📦 What Was Implemented

### 1. Service Layer ✅

**File**: `src/modules/initiatives/services/initiative.service.ts`

**Features**:
- Complete business logic for all initiative operations
- Input validation before API calls
- Error handling and transformation
- User-friendly error messages
- File validation for imports
- Singleton pattern for easy use

**Methods**:
- `getInitiatives()` - Fetch paginated list with filters
- `getInitiative()` - Fetch single initiative
- `createInitiative()` - Create with validation
- `updateInitiative()` - Update initiative
- `deleteInitiative()` - Delete initiative
- `getHierarchy()` - Get hierarchy tree
- `getChildren()` - Get child initiatives
- `addTeamMember()` / `removeTeamMember()` - Team management
- `addStudent()` / `removeStudent()` - Student management
- `getCoordinatorChanges()` - Change history
- `importCSV()` / `importZIP()` - Bulk import
- `getFailedImports()` - Failed imports
- `retryFailedImport()` / `deleteFailedImport()` - Import management
- `getStatistics()` - Statistics

### 2. Handlers ✅

**File**: `src/modules/initiatives/handlers/initiative.handlers.ts`

**Handlers Implemented**:

#### `useCreateInitiativeHandler()`
- Handles initiative creation
- Shows success notification
- Redirects to detail page
- Error handling

#### `useUpdateInitiativeHandler()`
- Handles initiative updates
- Shows success notification
- Redirects to detail page
- Error handling

#### `useDeleteInitiativeHandler()`
- Handles initiative deletion
- Shows success notification
- Redirects to list
- Error handling

#### `useTeamMemberHandler()`
- Add/remove team members
- Success notifications
- Error handling

#### `useStudentHandler()`
- Add/remove students
- Success notifications
- Error handling

#### `useImportHandler()`
- CSV/ZIP import
- Progress tracking
- Result display
- Error handling

#### `useFailedImportHandler()`
- Retry failed imports
- Delete failed imports
- Error handling

#### `useBulkOperationsHandler()`
- Bulk delete operations
- Progress tracking
- Error collection

#### `useSearchHandler()`
- Debounced search
- Query management
- Clear functionality

#### `useExportHandler()`
- Export to CSV
- File download
- Error handling

### 3. Updated InitiativeListView ✅

**Improvements**:
- Uses service layer through composables
- Uses handlers for operations
- Debounced search
- Advanced filters with clear functionality
- Export functionality
- Refresh functionality
- Better loading states
- Improved error handling
- Active filter indicators

### 4. Mock API Backend ✅

**Files Created**:
- `mock-api/db.json` - Sample data
- `mock-api/routes.json` - Custom routes
- `mock-api/middleware.js` - Custom middleware
- `mock-api/README.md` - Documentation

**Features**:
- **5 sample initiatives** (programs, projects, events)
- **14 people** (coordinators, team members, students)
- **3 organizational groups**
- **2 failed imports**
- **1 coordinator change**
- Pagination support
- Search and filtering
- Sorting
- CORS headers
- 300ms latency simulation
- Auto-reload on changes

**Endpoints**:
- `GET /initiatives` - List with pagination
- `GET /initiatives/:id` - Get single
- `POST /initiatives` - Create
- `PATCH /initiatives/:id` - Update
- `DELETE /initiatives/:id` - Delete
- `GET /people` - List people
- `GET /organizational_groups` - List groups
- `GET /failed_imports` - List failed imports
- `GET /coordinator_changes` - List changes

### 5. Package.json Updates ✅

**New Scripts**:
```json
{
  "dev:mock": "concurrently \"npm run mock-api\" \"npm run dev\"",
  "mock-api": "json-server --watch mock-api/db.json --port 8000 ..."
}
```

**New Dependencies**:
- `json-server` - Mock REST API
- `concurrently` - Run multiple commands

### 6. Translations ✅

**Updated Files**:
- `src/locales/en.json` - English translations
- `src/locales/pt-BR.json` - Portuguese translations

**New Keys**:
- `common.refresh`, `common.export`, `common.import`, `common.sortBy`
- `initiatives.*` - All initiative-related translations

## 🚀 How to Use

### Start with Mock API

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start mock API + frontend
npm run dev:mock
```

This starts:
- **Mock API**: http://localhost:8000
- **Frontend**: http://localhost:5173

### Start with Real Backend

```bash
# Terminal 1: Start Django backend
cd backend
docker-compose up

# Terminal 2: Start frontend
cd frontend
npm run dev
```

Update `.env.development`:
```env
VITE_API_URL=http://localhost:8000/api
```

## 📊 Architecture

```
Frontend Request Flow:
┌─────────────┐
│   View      │ (InitiativeListView.vue)
└──────┬──────┘
       │ uses
       ▼
┌─────────────┐
│  Handler    │ (useDeleteInitiativeHandler)
└──────┬──────┘
       │ calls
       ▼
┌─────────────┐
│  Service    │ (initiativeService)
└──────┬──────┘
       │ uses
       ▼
┌─────────────┐
│  API Client │ (initiativesApi)
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│  Backend    │ (Django or json-server)
└─────────────┘
```

## 🎯 Benefits

### Service Layer
- ✅ Centralized business logic
- ✅ Input validation
- ✅ Error handling
- ✅ Reusable across components
- ✅ Easy to test
- ✅ Type-safe

### Handlers
- ✅ Reusable UI logic
- ✅ Consistent notifications
- ✅ Loading states
- ✅ Error handling
- ✅ Navigation logic
- ✅ Composable pattern

### Mock API
- ✅ Develop without backend
- ✅ Fast iteration
- ✅ Realistic data
- ✅ Test edge cases
- ✅ Demo/presentation ready
- ✅ No database setup needed

## 📝 Example Usage

### Using Service Directly

```typescript
import { initiativeService } from '@/modules/initiatives/services/initiative.service';

// Create initiative
const initiative = await initiativeService.createInitiative({
  name: 'New Initiative',
  description: 'Description',
  type: 'PROJECT',
  start_date: '2024-01-01',
  coordinator_id: 1,
});

// Get initiatives with filters
const result = await initiativeService.getInitiatives(
  { type: 'PROGRAM', search: 'rural' },
  1,
  10
);
```

### Using Handlers in Component

```vue
<script setup>
import { useDeleteInitiativeHandler } from '@/modules/initiatives/handlers/initiative.handlers';

const { handleDelete, isDeleting } = useDeleteInitiativeHandler();

const onDelete = async (initiative) => {
  await handleDelete(initiative);
  // Automatically shows notification and redirects
};
</script>
```

### Using Composables (Recommended)

```vue
<script setup>
import { ref } from 'vue';
import { useInitiatives } from '@/modules/initiatives/composables/useInitiatives';

const filters = ref({ type: 'PROGRAM' });
const { items, isLoading, create, update, delete: deleteInit } = useInitiatives(filters);

// Data is automatically cached and updated
</script>
```

## 🧪 Testing

### Test with Mock API

```bash
# Start mock API
npm run dev:mock

# Open browser
http://localhost:5173/initiatives

# Try:
- Search initiatives
- Filter by type
- Sort
- Create (will save to db.json)
- Edit
- Delete
- Export
```

### Test API Directly

```bash
# List initiatives
curl http://localhost:8000/initiatives

# Get one
curl http://localhost:8000/initiatives/1

# Create
curl -X POST http://localhost:8000/initiatives \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","type":"PROJECT",...}'
```

## 🔄 Data Flow Examples

### Create Initiative

```
User clicks "Create" button
  ↓
InitiativeCreateView
  ↓
useCreateInitiativeHandler()
  ↓
initiativeService.createInitiative()
  ↓
initiativesApi.create()
  ↓
axios POST /api/initiatives
  ↓
Backend (Django or json-server)
  ↓
Response with created initiative
  ↓
Success notification shown
  ↓
Redirect to detail page
  ↓
Cache invalidated
  ↓
List refreshes automatically
```

### Search Initiatives

```
User types in search box
  ↓
useSearchHandler() debounces (300ms)
  ↓
filters.search updated
  ↓
useInitiatives() detects change
  ↓
TanStack Query refetches
  ↓
initiativesApi.list({ search: "..." })
  ↓
Backend returns filtered results
  ↓
UI updates with new data
```

## 📚 Next Steps

1. **Complete remaining views**:
   - InitiativeDetailView
   - InitiativeCreateView
   - InitiativeEditView
   - InitiativeImportView

2. **Add more components**:
   - InitiativeForm
   - TeamMemberList
   - StudentList
   - InitiativeHierarchy

3. **Add routes** to router

4. **Test with real backend** when available

5. **Add unit tests** for services and handlers

## 🎓 Best Practices Implemented

- ✅ Separation of concerns (View → Handler → Service → API)
- ✅ Single Responsibility Principle
- ✅ DRY (Don't Repeat Yourself)
- ✅ Error handling at every layer
- ✅ Type safety throughout
- ✅ Consistent patterns
- ✅ Reusable code
- ✅ User-friendly messages
- ✅ Loading states
- ✅ Optimistic updates (via TanStack Query)

## 📖 Documentation

- **Service**: See inline JSDoc comments
- **Handlers**: See inline JSDoc comments
- **Mock API**: See `mock-api/README.md`
- **Usage**: See examples above

---

**Status**: ✅ Complete and ready for use  
**Next**: Complete remaining Phase 2 views and components
