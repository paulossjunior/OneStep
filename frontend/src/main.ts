import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { VueQueryPlugin } from '@tanstack/vue-query';
import router from './router';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';
import App from './App.vue';

// Import styles
import './assets/styles/main.css';

const app = createApp(App);

// Install plugins
app.use(createPinia());
app.use(router);
app.use(vuetify);
app.use(i18n);
app.use(VueQueryPlugin, {
  queryClientConfig: {
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes (renamed from cacheTime)
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  },
});

app.mount('#app');
