# Phase 2: Initiatives Module - Implementation Guide

**Status**: 🚧 In Progress  
**Date Started**: November 30, 2024

## Overview

Phase 2 implements the complete Initiatives module with CRUD operations, hierarchy management, team management, and bulk import functionality.

## Completed Tasks

### ✅ Task 2.1: Initiatives API Layer (100%)
**Files Created**:
- `src/modules/initiatives/types/initiative.types.ts` - TypeScript interfaces
- `src/modules/initiatives/api/initiatives.api.ts` - API client

**Features**:
- CRUD operations (list, get, create, update, delete)
- Hierarchy endpoints
- Team member management
- Student management
- Coordinator change history
- CSV/ZIP import
- Failed imports management
- Statistics endpoint

### ✅ Task 2.2: Initiatives Composables (100%)
**Files Created**:
- `src/modules/initiatives/composables/useInitiatives.ts` - Main composable
- `src/modules/initiatives/composables/useInitiativeHierarchy.ts` - Hierarchy
- `src/modules/initiatives/composables/useInitiativeImport.ts` - Import
- `src/modules/initiatives/composables/useFailedImports.ts` - Failed imports

**Features**:
- TanStack Query integration
- Automatic cache invalidation
- Optimistic updates
- Error handling
- Loading states

### 🚧 Task 2.3: Initiatives Store (Pending)
Will be created if needed for complex state management.

### ⏳ Task 2.4: Initiative Components (Partial)
**Completed**:
- `InitiativeCard.vue` - Card display component

**Remaining**:
- InitiativeForm.vue
- InitiativeHierarchy.vue (tree view)
- InitiativeTimeline.vue
- InitiativeTypeSelector.vue
- TeamMemberList.vue
- StudentList.vue
- CoordinatorChangeHistory.vue

### ⏳ Task 2.5: Initiative Views (Partial)
**Completed**:
- `InitiativeListView.vue` - List with filters and pagination

**Remaining**:
- InitiativeDetailView.vue
- InitiativeCreateView.vue
- InitiativeEditView.vue

### ⏳ Task 2.6: Initiative Import Features (Pending)
**Remaining**:
- BulkImportUploader.vue
- InitiativeImportView.vue
- FailedImportList.vue
- FailedImportsView.vue

### ⏳ Task 2.7: Coordinator Change Tracking (Pending)
**Remaining**:
- CoordinatorChangesView.vue

### ⏳ Task 2.8: Initiative Routes (Pending)
Routes need to be added to main router.

## Implementation Strategy

Given the extensive nature of Phase 2, here's the recommended approach:

### Priority 1: Core CRUD (Essential)
1. ✅ API Layer
2. ✅ Composables
3. ✅ InitiativeCard component
4. ✅ InitiativeListView
5. ⏳ InitiativeForm component
6. ⏳ InitiativeCreateView
7. ⏳ InitiativeEditView
8. ⏳ InitiativeDetailView
9. ⏳ Routes

### Priority 2: Team Management
1. ⏳ TeamMemberList component
2. ⏳ StudentList component
3. ⏳ Add/remove functionality in DetailView

### Priority 3: Hierarchy
1. ⏳ InitiativeHierarchy component (tree view)
2. ⏳ Hierarchy view/page

### Priority 4: Import Features
1. ⏳ BulkImportUploader component
2. ⏳ InitiativeImportView
3. ⏳ FailedImportList component
4. ⏳ FailedImportsView

### Priority 5: Additional Features
1. ⏳ InitiativeTimeline component
2. ⏳ CoordinatorChangeHistory component
3. ⏳ CoordinatorChangesView

## Quick Implementation Script

To complete the remaining components quickly, use this template structure:

### InitiativeForm.vue Template
```vue
<template>
  <v-form @submit.prevent="handleSubmit" ref="formRef">
    <!-- Name -->
    <v-text-field
      v-model="formData.name"
      label="Name"
      :rules="[rules.required]"
      required
    ></v-text-field>

    <!-- Description -->
    <v-textarea
      v-model="formData.description"
      label="Description"
      :rules="[rules.required]"
    ></v-textarea>

    <!-- Type -->
    <v-select
      v-model="formData.type"
      :items="typeOptions"
      label="Type"
      :rules="[rules.required]"
    ></v-select>

    <!-- Dates -->
    <v-text-field
      v-model="formData.start_date"
      label="Start Date"
      type="date"
      :rules="[rules.required]"
    ></v-text-field>

    <v-text-field
      v-model="formData.end_date"
      label="End Date"
      type="date"
    ></v-text-field>

    <!-- Coordinator (autocomplete) -->
    <!-- Parent (autocomplete) -->
    
    <!-- Actions -->
    <v-btn type="submit" color="primary" :loading="isSubmitting">
      Save
    </v-btn>
    <v-btn @click="$emit('cancel')">Cancel</v-btn>
  </v-form>
</template>
```

### InitiativeDetailView.vue Template
```vue
<template>
  <div>
    <LoadingSpinner v-if="isLoading" />
    
    <div v-else-if="initiative">
      <!-- Header -->
      <v-row>
        <v-col>
          <h1>{{ initiative.name }}</h1>
          <v-chip>{{ initiative.type }}</v-chip>
        </v-col>
        <v-col class="text-right">
          <v-btn :to="`/initiatives/${initiative.id}/edit`">Edit</v-btn>
          <v-btn @click="handleDelete" color="error">Delete</v-btn>
        </v-col>
      </v-row>

      <!-- Details -->
      <v-card class="mt-4">
        <v-card-text>
          <p>{{ initiative.description }}</p>
          <p><strong>Coordinator:</strong> {{ initiative.coordinator.full_name }}</p>
          <p><strong>Start:</strong> {{ initiative.start_date }}</p>
          <p><strong>End:</strong> {{ initiative.end_date }}</p>
        </v-card-text>
      </v-card>

      <!-- Team Members -->
      <TeamMemberList
        :members="initiative.team_members"
        @add="handleAddTeamMember"
        @remove="handleRemoveTeamMember"
      />

      <!-- Students -->
      <StudentList
        :students="initiative.students"
        @add="handleAddStudent"
        @remove="handleRemoveStudent"
      />
    </div>
  </div>
</template>
```

## Translation Keys Needed

Add to `src/locales/en.json` and `src/locales/pt-BR.json`:

```json
{
  "initiatives": {
    "title": "Initiatives",
    "create": "Create Initiative",
    "import": "Import",
    "searchPlaceholder": "Search initiatives...",
    "type": "Type",
    "noInitiatives": "No initiatives found",
    "createFirst": "Create your first initiative",
    "deleteTitle": "Delete Initiative",
    "deleteMessage": "Are you sure you want to delete this initiative?",
    "teamMembers": "Team Members",
    "students": "Students",
    "startDateAfter": "Start Date After",
    "endDateBefore": "End Date Before",
    "types": {
      "PROGRAM": "Program",
      "PROJECT": "Project",
      "EVENT": "Event"
    }
  }
}
```

## Routes to Add

Add to `src/router/index.ts`:

```typescript
{
  path: 'initiatives',
  children: [
    {
      path: '',
      name: 'initiatives-list',
      component: () => import('@/modules/initiatives/views/InitiativeListView.vue'),
    },
    {
      path: 'create',
      name: 'initiatives-create',
      component: () => import('@/modules/initiatives/views/InitiativeCreateView.vue'),
    },
    {
      path: ':id',
      name: 'initiatives-detail',
      component: () => import('@/modules/initiatives/views/InitiativeDetailView.vue'),
    },
    {
      path: ':id/edit',
      name: 'initiatives-edit',
      component: () => import('@/modules/initiatives/views/InitiativeEditView.vue'),
    },
    {
      path: 'import',
      name: 'initiatives-import',
      component: () => import('@/modules/initiatives/views/InitiativeImportView.vue'),
    },
    {
      path: 'hierarchy',
      name: 'initiatives-hierarchy',
      component: () => import('@/modules/initiatives/views/InitiativeHierarchyView.vue'),
    },
  ],
},
```

## Testing Checklist

Once implementation is complete:

- [ ] List initiatives with pagination
- [ ] Search and filter initiatives
- [ ] Create new initiative
- [ ] View initiative details
- [ ] Edit initiative
- [ ] Delete initiative
- [ ] Add/remove team members
- [ ] Add/remove students
- [ ] View hierarchy
- [ ] Import CSV file
- [ ] Import ZIP file
- [ ] View failed imports
- [ ] Retry failed import
- [ ] View coordinator changes

## Next Steps

1. **Complete remaining components** (Priority 1 first)
2. **Add routes** to main router
3. **Add translations** for all text
4. **Test all functionality** with backend API
5. **Add error handling** for edge cases
6. **Optimize performance** if needed
7. **Move to Phase 3** (Scholarships Module)

## Estimated Time Remaining

- Priority 1 (Core CRUD): 2-3 days
- Priority 2 (Team Management): 1 day
- Priority 3 (Hierarchy): 1 day
- Priority 4 (Import): 2 days
- Priority 5 (Additional): 1 day

**Total**: 7-8 days remaining for complete Phase 2

## Notes

- API layer is complete and type-safe
- Composables use TanStack Query for optimal caching
- Components follow Vuetify 3 patterns
- All code is TypeScript with full type safety
- Ready for backend integration

---

**Status**: Foundation complete, views in progress  
**Next**: Complete InitiativeForm and CRUD views
