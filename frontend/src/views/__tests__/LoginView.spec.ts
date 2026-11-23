import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../api/client'
import { catalog } from '../../i18n/fa'

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

const RouterLinkStub = defineComponent({
  setup(_props, { slots }) {
    return () => h('a', {}, slots.default?.())
  },
})

function mountView() {
  return mount(LoginView, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
}

describe('LoginView (fa-IR)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders Persian text with an RTL container', () => {
    const wrapper = mountView()

    expect(wrapper.find('h1').text()).toBe(catalog['login.title'])
    expect(wrapper.find('.subtitle').text()).toBe(catalog['login.subtitle'])
    expect(wrapper.find('label[for="email"]').text()).toBe(catalog['login.email'])
    expect(wrapper.find('label[for="password"]').text()).toBe(catalog['login.password'])
    expect(wrapper.find('button').text()).toBe(catalog['login.submit'])
    expect(wrapper.find('.switch').text()).toContain(catalog['login.switchLink'])
    expect(wrapper.find('.auth-page').attributes('dir')).toBe('rtl')
  })

  it('keeps credential inputs left-to-right', () => {
    const wrapper = mountView()

    expect(wrapper.find('#email').attributes('dir')).toBe('ltr')
    expect(wrapper.find('#password').attributes('dir')).toBe('ltr')
  })

  it('submits the entered credentials to the auth store unchanged', async () => {
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

  it('shows the Persian message for invalid credentials', async () => {
    loginMock.mockRejectedValue(
      new ApiError(401, 'Invalid email or password', 'invalid_credentials'),
    )
    const wrapper = mountView()

    await wrapper.find('#email').setValue('buyer@example.com')
    await wrapper.find('#password').setValue('wrong')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('[role="alert"]').text()).toBe(
      catalog['errors.invalid_credentials'],
    )
  })
})
