import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { loginMock, registerMock } = vi.hoisted(() => ({
  loginMock: vi.fn(),
  registerMock: vi.fn(),
}))

vi.mock('../../api/auth', () => ({
  authApi: {
    login: loginMock,
    register: registerMock,
  },
}))

import { useAuthStore } from '../auth'

const tokenResult = {
  access_token: 'access-token',
  refresh_token: 'refresh-token',
  token_type: 'bearer',
  expires_in: 1800,
  refresh_expires_in: 604800,
}

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('stores both tokens on login and marks the user authenticated', async () => {
    loginMock.mockResolvedValue(tokenResult)
    const store = useAuthStore()

    await store.login({ email: 'buyer@example.com', password: 's3curePass!' })

    expect(loginMock).toHaveBeenCalledWith({
      email: 'buyer@example.com',
      password: 's3curePass!',
    })
    expect(store.accessToken).toBe('access-token')
    expect(store.refreshToken).toBe('refresh-token')
    expect(store.isAuthenticated).toBe(true)
    expect(localStorage.getItem('marketplace_access_token')).toBe('access-token')
    expect(localStorage.getItem('marketplace_refresh_token')).toBe('refresh-token')
  })

  it('registers and then logs the new user in', async () => {
    registerMock.mockResolvedValue({ id: 'u-1', email: 'seller@example.com', role: 'seller' })
    loginMock.mockResolvedValue(tokenResult)
    const store = useAuthStore()

    await store.register({
      email: 'seller@example.com',
      password: 's3curePass!',
      role: 'seller',
    })

    expect(registerMock).toHaveBeenCalledWith({
      email: 'seller@example.com',
      password: 's3curePass!',
      role: 'seller',
    })
    expect(loginMock).toHaveBeenCalledWith({
      email: 'seller@example.com',
      password: 's3curePass!',
    })
    expect(store.isAuthenticated).toBe(true)
  })

  it('clears tokens and authentication state on logout', async () => {
    loginMock.mockResolvedValue(tokenResult)
    const store = useAuthStore()
    await store.login({ email: 'buyer@example.com', password: 's3curePass!' })

    store.logout()

    expect(store.accessToken).toBeNull()
    expect(store.refreshToken).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('marketplace_access_token')).toBeNull()
    expect(localStorage.getItem('marketplace_refresh_token')).toBeNull()
  })
})
