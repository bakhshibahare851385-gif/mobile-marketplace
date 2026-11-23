<script setup lang="ts">
import { ref } from 'vue'
import { messageForError } from '../i18n/errors'
import { t } from '../i18n/fa'
import { useAuthStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const auth = useAuthStore()

async function submit(): Promise<void> {
  error.value = ''
  loading.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
  } catch (cause) {
    error.value = messageForError(cause)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page" dir="rtl">
    <section class="auth-card" aria-labelledby="login-title">
      <h1 id="login-title">{{ t('login.title') }}</h1>
      <p class="subtitle">{{ t('login.subtitle') }}</p>

      <form @submit.prevent="submit" novalidate>
        <div class="field">
          <label for="email">{{ t('login.email') }}</label>
          <input
            id="email"
            v-model="email"
            dir="ltr"
            type="email"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label for="password">{{ t('login.password') }}</label>
          <input
            id="password"
            v-model="password"
            dir="ltr"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? t('login.submitting') : t('login.submit') }}
        </button>
      </form>

      <p v-if="auth.isAuthenticated" class="success" role="status">
        {{ t('login.success') }}
      </p>
      <p class="switch">
        {{ t('login.switchPrompt') }}
        <RouterLink to="/register">{{ t('login.switchLink') }}</RouterLink>
      </p>
    </section>
  </main>
</template>
