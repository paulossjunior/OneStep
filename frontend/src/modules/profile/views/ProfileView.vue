<template>
  <div>
    <h1 class="text-h3 mb-4">Profile</h1>
    <v-card>
      <v-card-text>
        <p><strong>Name:</strong> {{ currentUser?.first_name }} {{ currentUser?.last_name }}</p>
        <p><strong>Email:</strong> {{ currentUser?.email }}</p>
        <p><strong>Username:</strong> {{ currentUser?.username }}</p>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '@/core/composables/useAuth';

const { currentUser } = useAuth();
</script>
