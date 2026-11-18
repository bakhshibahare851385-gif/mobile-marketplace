import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  authApi,
  type LoginPayload,
  type RegisterPayload,
  type TokenResult,
} from '../api/auth'

const ACCESS_KEY = 'marketplace_access_token'
const REFRESH_KEY = 'marketplace_refresh_token'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_KEY))
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_KEY))
  const isAuthenticated = computed(() => accessToken.value !== null)

  function setTokens(access: string, refresh: string): void {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  }

  function clearTokens(): void {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }

  async function login(payload: LoginPayload): Promise<TokenResult> {
    const result = await authApi.login(payload)
    setTokens(result.access_token, result.refresh_token)
    return result
  }

  async function register(payload: RegisterPayload): Promise<TokenResult> {
    await authApi.register(payload)
    return login({ email: payload.email, password: payload.password })
  }

  function logout(): void {
    clearTokens()
  }

  return {
    accessToken,
    refreshToken,
    isAuthenticated,
    login,
    register,
    logout,
  }
})
