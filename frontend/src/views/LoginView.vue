<script setup lang="ts">
import { ref } from 'vue'
import { ApiError } from '../api/client'
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
    error.value =
      cause instanceof ApiError ? cause.message : 'Unable to sign in. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card" aria-labelledby="login-title">
      <h1 id="login-title">Sign in</h1>
      <p class="subtitle">Mobile Accessories Marketplace</p>

      <form @submit.prevent="submit" novalidate>
        <div class="field">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <p v-if="auth.isAuthenticated" class="success" role="status">
        You are signed in.
      </p>
      <p class="switch">
        New here? <RouterLink to="/register">Create an account</RouterLink>
      </p>
    </section>
  </main>
</template>
