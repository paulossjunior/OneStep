<template>
  <v-app-bar elevation="2" color="primary">
    <v-app-bar-nav-icon @click="$emit('toggle-sidebar')"></v-app-bar-nav-icon>

    <v-toolbar-title class="font-weight-bold">
      <v-icon icon="mdi-rocket-launch" class="mr-2"></v-icon>
      OneStep
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <!-- Search -->
    <v-text-field
      v-model="searchQuery"
      prepend-inner-icon="mdi-magnify"
      placeholder="Search..."
      variant="solo"
      density="compact"
      hide-details
      single-line
      class="mr-4 d-none d-md-flex"
      style="max-width: 400px"
    ></v-text-field>

    <!-- Notifications -->
    <v-btn icon="mdi-bell-outline" class="mr-2"></v-btn>

    <!-- Theme Toggle -->
    <v-btn
      :icon="theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
      @click="toggleTheme"
      class="mr-2"
    ></v-btn>

    <!-- Language Selector -->
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn icon="mdi-translate" v-bind="props" class="mr-2"></v-btn>
      </template>
      <v-list>
        <v-list-item
          v-for="lang in availableLocales"
          :key="lang.code"
          :value="lang.code"
          @click="changeLocale(lang.code)"
        >
          <v-list-item-title>{{ lang.name }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <!-- User Menu -->
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn icon v-bind="props">
          <v-avatar color="secondary" size="36">
            <span class="text-h6">{{ userInitials }}</span>
          </v-avatar>
        </v-btn>
      </template>
      <v-list>
        <v-list-item>
          <v-list-item-title class="font-weight-bold">
            {{ currentUser?.first_name }} {{ currentUser?.last_name }}
          </v-list-item-title>
          <v-list-item-subtitle>{{ currentUser?.email }}</v-list-item-subtitle>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item prepend-icon="mdi-account" to="/profile">
          <v-list-item-title>{{ $t('common.profile') }}</v-list-item-title>
        </v-list-item>
        <v-list-item prepend-icon="mdi-cog" to="/settings">
          <v-list-item-title>{{ $t('common.settings') }}</v-list-item-title>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item prepend-icon="mdi-logout" @click="handleLogout">
          <v-list-item-title>{{ $t('auth.logout') }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useTheme } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { useAuth } from '@/core/composables/useAuth';

defineEmits<{
  'toggle-sidebar': [];
}>();

const router = useRouter();
const theme = useTheme();
const { locale } = useI18n();
const { currentUser, logout } = useAuth();

const searchQuery = ref('');

const availableLocales = [
  { code: 'en', name: 'English' },
  { code: 'pt-BR', name: 'Português (BR)' },
];

const userInitials = computed(() => {
  if (!currentUser.value) return '?';
  const first = currentUser.value.first_name?.[0] || '';
  const last = currentUser.value.last_name?.[0] || '';
  return (first + last).toUpperCase() || currentUser.value.username[0].toUpperCase();
});

const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark';
  localStorage.setItem('theme', theme.global.name.value);
};

const changeLocale = (code: string) => {
  locale.value = code;
  localStorage.setItem('locale', code);
};

const handleLogout = async () => {
  await logout();
  router.push('/login');
};
</script>
