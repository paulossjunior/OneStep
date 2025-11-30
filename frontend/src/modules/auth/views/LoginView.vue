<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8" rounded="lg">
          <v-card-title class="text-h4 text-center py-6 bg-primary">
            <v-icon icon="mdi-login" size="large" class="mr-2"></v-icon>
            {{ $t('auth.login') }}
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form @submit.prevent="handleLogin" ref="formRef">
              <v-text-field
                v-model="credentials.username"
                :label="$t('auth.username')"
                :rules="[rules.required]"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                class="mb-3"
                :disabled="isLoading"
              ></v-text-field>

              <v-text-field
                v-model="credentials.password"
                :label="$t('auth.password')"
                :rules="[rules.required]"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                variant="outlined"
                class="mb-3"
                :disabled="isLoading"
              ></v-text-field>

              <v-alert
                v-if="errorMessage"
                type="error"
                variant="tonal"
                class="mb-4"
                closable
                @click:close="errorMessage = ''"
              >
                {{ errorMessage }}
              </v-alert>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="isLoading"
                :disabled="isLoading"
              >
                {{ $t('auth.signIn') }}
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from '@/core/composables/useAuth';
import { useI18n } from 'vue-i18n';
import type { LoginCredentials } from '@/core/types/auth.types';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const { login, isLoading } = useAuth();

const formRef = ref();
const showPassword = ref(false);
const errorMessage = ref('');

const credentials = reactive<LoginCredentials>({
  username: '',
  password: '',
});

const rules = {
  required: (value: string) => !!value || t('validation.required'),
};

const handleLogin = async () => {
  const { valid } = await formRef.value.validate();
  
  if (!valid) {
    return;
  }

  errorMessage.value = '';

  try {
    await login(credentials);
    
    // Redirect to intended page or dashboard
    const redirect = route.query.redirect as string || '/';
    router.push(redirect);
  } catch (error: any) {
    errorMessage.value = error.message || t('auth.loginFailed');
  }
};
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
