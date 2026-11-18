import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../api/client'

const { registerMock } = vi.hoisted(() => ({ registerMock: vi.fn() }))

vi.mock('../../stores/auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: false,
    login: vi.fn(),
    logout: vi.fn(),
    register: registerMock,
  }),
}))

import RegisterView from '../RegisterView.vue'

function mountView() {
  return mount(RegisterView, {
    global: { stubs: { RouterLink: true } },
  })
}

describe('RegisterView', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders email, password, and role fields with labels', () => {
    const wrapper = mountView()

    expect(wrapper.find('label[for="email"]').exists()).toBe(true)
    expect(wrapper.find('label[for="password"]').exists()).toBe(true)
    expect(wrapper.find('label[for="role"]').exists()).toBe(true)
    expect((wrapper.find('#role').element as HTMLSelectElement).value).toBe('buyer')
  })

  it('submits email, password, and selected role', async () => {
    registerMock.mockResolvedValue({ access_token: 'a', refresh_token: 'r' })
    const wrapper = mountView()

    await wrapper.find('#email').setValue('seller@example.com')
    await wrapper.find('#password').setValue('s3curePass!')
    await wrapper.find('#role').setValue('seller')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(registerMock).toHaveBeenCalledWith({
      email: 'seller@example.com',
      password: 's3curePass!',
      role: 'seller',
    })
  })

  it('shows the duplicate-email error returned by the backend', async () => {
    registerMock.mockRejectedValue(
      new ApiError(409, 'An account with this email already exists', 'duplicate_email'),
    )
    const wrapper = mountView()

    await wrapper.find('#email').setValue('buyer@example.com')
    await wrapper.find('#password').setValue('s3curePass!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('[role="alert"]').text()).toBe(
      'An account with this email already exists',
    )
  })
})
