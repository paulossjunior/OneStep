import { createI18n } from 'vue-i18n';
import en from '@/locales/en.json';
import ptBR from '@/locales/pt-BR.json';

const savedLocale = localStorage.getItem('locale') || 'pt-BR';

export default createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    'pt-BR': ptBR,
  },
});
