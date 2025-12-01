import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { authGuard, guestGuard } from '@/core/guards/auth.guard';
import { useAuthStore } from '@/core/stores/auth.store';

// Layouts
import DefaultLayout from '@/core/layouts/DefaultLayout.vue';
import AuthLayout from '@/core/layouts/AuthLayout.vue';

const routes: RouteRecordRaw[] = [
  // Auth routes
  {
    path: '/login',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('@/modules/auth/views/LoginView.vue'),
        beforeEnter: guestGuard,
        meta: {
          title: 'Login',
        },
      },
    ],
  },

  // Main app routes
  {
    path: '/',
    component: DefaultLayout,
    beforeEnter: authGuard,
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/modules/dashboard/views/DashboardView.vue'),
        meta: {
          title: 'Dashboard',
          breadcrumbs: [{ text: 'Dashboard', disabled: true }],
        },
      },

      // Initiatives routes
      {
        path: 'initiatives',
        name: 'initiatives',
        component: () => import('@/modules/initiatives/views/InitiativeListView.vue'),
        meta: {
          title: 'Initiatives',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Initiatives', disabled: true },
          ],
        },
      },
      {
        path: 'initiatives/create',
        name: 'initiatives-create',
        component: () => import('@/modules/initiatives/views/InitiativeCreateView.vue'),
        meta: {
          title: 'Create Initiative',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Initiatives', to: '/initiatives' },
            { text: 'Create', disabled: true },
          ],
          requiredPermission: 'initiatives.add_initiative',
        },
      },
      {
        path: 'initiatives/import',
        name: 'initiatives-import',
        component: () => import('@/modules/initiatives/views/InitiativeImportView.vue'),
        meta: {
          title: 'Import Initiatives',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Initiatives', to: '/initiatives' },
            { text: 'Import', disabled: true },
          ],
          requiredPermission: 'initiatives.add_initiative',
        },
      },
      {
        path: 'initiatives/failed-imports',
        name: 'initiatives-failed-imports',
        component: () => import('@/modules/initiatives/views/FailedImportsView.vue'),
        meta: {
          title: 'Failed Imports',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Initiatives', to: '/initiatives' },
            { text: 'Failed Imports', disabled: true },
          ],
          requiredPermission: 'initiatives.add_initiative',
        },
      },
      {
        path: 'initiatives/:id',
        name: 'initiatives-detail',
        component: () => import('@/modules/initiatives/views/InitiativeDetailView.vue'),
        meta: {
          title: 'Initiative Details',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Initiatives', to: '/initiatives' },
            { text: 'Details', disabled: true },
          ],
        },
      },
      {
        path: 'initiatives/:id/edit',
        name: 'initiatives-edit',
        component: () => import('@/modules/initiatives/views/InitiativeEditView.vue'),
        meta: {
          title: 'Edit Initiative',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Initiatives', to: '/initiatives' },
            { text: 'Edit', disabled: true },
          ],
          requiredPermission: 'initiatives.change_initiative',
        },
      },

      // Scholarships routes (will be added in Phase 3)
      {
        path: 'scholarships',
        name: 'scholarships',
        component: () => import('@/modules/scholarships/views/ScholarshipListView.vue'),
        meta: {
          title: 'Scholarships',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Scholarships', disabled: true },
          ],
        },
      },

      // People routes (will be added in Phase 4)
      {
        path: 'people',
        name: 'people',
        component: () => import('@/modules/people/views/PeopleListView.vue'),
        meta: {
          title: 'People',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'People', disabled: true },
          ],
        },
      },

      // Profile
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/modules/profile/views/ProfileView.vue'),
        meta: {
          title: 'Profile',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Profile', disabled: true },
          ],
        },
      },

      // Settings
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/modules/settings/views/SettingsView.vue'),
        meta: {
          title: 'Settings',
          breadcrumbs: [
            { text: 'Dashboard', to: '/' },
            { text: 'Settings', disabled: true },
          ],
        },
      },
    ],
  },

  // Error pages
  {
    path: '/forbidden',
    name: 'forbidden',
    component: () => import('@/modules/errors/views/ForbiddenView.vue'),
    meta: {
      title: '403 - Forbidden',
    },
  },

  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/modules/errors/views/NotFoundView.vue'),
    meta: {
      title: '404 - Not Found',
    },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// Global navigation guards
router.beforeEach((to, from, next) => {
  // Update document title
  const title = to.meta.title as string;
  document.title = title ? `${title} | OneStep` : 'OneStep';

  // Initialize auth if needed
  const authStore = useAuthStore();
  if (!authStore.user && authStore.accessToken) {
    authStore.initializeAuth();
  }

  next();
});

export default router;
