import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../api/client'

const { loginMock } = vi.hoisted(() => ({ loginMock: vi.fn() }))

vi.mock('../../stores/auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: false,
    login: loginMock,
    logout: vi.fn(),
    register: vi.fn(),
  }),
}))

import LoginView from '../LoginView.vue'

function mountView() {
  return mount(LoginView, {
    global: { stubs: { RouterLink: true } },
  })
}

describe('LoginView', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders labeled email and password fields', () => {
    const wrapper = mountView()

    expect(wrapper.find('label[for="email"]').exists()).toBe(true)
    expect(wrapper.find('label[for="password"]').exists()).toBe(true)
    expect(wrapper.find('#email').attributes('type')).toBe('email')
    expect(wrapper.find('#password').attributes('type')).toBe('password')
  })

  it('submits the entered credentials to the auth store', async () => {
    loginMock.mockResolvedValue({ access_token: 'a', refresh_token: 'r' })
    const wrapper = mountView()

    await wrapper.find('#email').setValue('buyer@example.com')
    await wrapper.find('#password').setValue('s3curePass!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(loginMock).toHaveBeenCalledWith({
      email: 'buyer@example.com',
      password: 's3curePass!',
    })
  })

  it('shows the backend error message when credentials are rejected', async () => {
    loginMock.mockRejectedValue(new ApiError(401, 'Invalid email or password'))
    const wrapper = mountView()

    await wrapper.find('#email').setValue('buyer@example.com')
    await wrapper.find('#password').setValue('wrong')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('[role="alert"]').text()).toBe('Invalid email or password')
  })
})
