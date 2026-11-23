<script setup lang="ts">
import { ref } from 'vue'
import type { Role } from '../api/auth'
import { messageForError } from '../i18n/errors'
import { t } from '../i18n/fa'
import { useAuthStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const role = ref<Role>('buyer')
const error = ref('')
const loading = ref(false)
const auth = useAuthStore()

async function submit(): Promise<void> {
  error.value = ''
  loading.value = true
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      role: role.value,
    })
  } catch (cause) {
    error.value = messageForError(cause)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page" dir="rtl">
    <section class="auth-card" aria-labelledby="register-title">
      <h1 id="register-title">{{ t('register.title') }}</h1>
      <p class="subtitle">{{ t('register.subtitle') }}</p>

      <form @submit.prevent="submit" novalidate>
        <div class="field">
          <label for="email">{{ t('register.email') }}</label>
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
          <label for="password">{{ t('register.password') }}</label>
          <input
            id="password"
            v-model="password"
            dir="ltr"
            type="password"
            autocomplete="new-password"
            minlength="8"
            maxlength="72"
            required
          />
          <small>{{ t('register.passwordHint') }}</small>
        </div>

        <div class="field">
          <label for="role">{{ t('register.role') }}</label>
          <select id="role" v-model="role">
            <option value="buyer">{{ t('register.roleBuyer') }}</option>
            <option value="seller">{{ t('register.roleSeller') }}</option>
          </select>
        </div>

        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? t('register.submitting') : t('register.submit') }}
        </button>
      </form>

      <p v-if="auth.isAuthenticated" class="success" role="status">
        {{ t('register.success') }}
      </p>
      <p class="switch">
        {{ t('register.switchPrompt') }}
        <RouterLink to="/login">{{ t('register.switchLink') }}</RouterLink>
      </p>
    </section>
  </main>
</template>
