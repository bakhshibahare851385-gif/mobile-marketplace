<script setup lang="ts">
import { ref } from 'vue'
import { ApiError } from '../api/client'
import type { Role } from '../api/auth'
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
    error.value =
      cause instanceof ApiError
        ? cause.message
        : 'Unable to create your account. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card" aria-labelledby="register-title">
      <h1 id="register-title">Create an account</h1>
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
            autocomplete="new-password"
            minlength="8"
            maxlength="72"
            required
          />
          <small>Use between 8 and 72 characters.</small>
        </div>

        <div class="field">
          <label for="role">I am a</label>
          <select id="role" v-model="role">
            <option value="buyer">Buyer — browse and buy accessories</option>
            <option value="seller">Seller — showcase my products</option>
          </select>
        </div>

        <p v-if="error" class="error" role="alert">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Creating account…' : 'Create account' }}
        </button>
      </form>

      <p v-if="auth.isAuthenticated" class="success" role="status">
        Your account is ready and you are signed in.
      </p>
      <p class="switch">
        Already registered? <RouterLink to="/login">Sign in</RouterLink>
      </p>
    </section>
  </main>
</template>
