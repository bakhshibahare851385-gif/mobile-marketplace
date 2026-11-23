import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '../../api/client'
import { catalog } from '../../i18n/fa'

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

const RouterLinkStub = defineComponent({
  setup(_props, { slots }) {
    return () => h('a', {}, slots.default?.())
  },
})

function mountView() {
  return mount(RegisterView, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
}

describe('RegisterView (fa-IR)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders Persian text with an RTL container', () => {
    const wrapper = mountView()

    expect(wrapper.find('h1').text()).toBe(catalog['register.title'])
    expect(wrapper.find('label[for="email"]').text()).toBe(catalog['register.email'])
    expect(wrapper.find('label[for="password"]').text()).toBe(catalog['register.password'])
    expect(wrapper.find('label[for="role"]').text()).toBe(catalog['register.role'])
    expect(wrapper.find('button').text()).toBe(catalog['register.submit'])
    expect(wrapper.find('small').text()).toBe(catalog['register.passwordHint'])
    expect(wrapper.find('.switch').text()).toContain(catalog['register.switchLink'])
    expect(wrapper.find('.auth-page').attributes('dir')).toBe('rtl')
  })

  it('shows Persian role labels while keeping backend values', () => {
    const wrapper = mountView()
    const options = wrapper.findAll('#role option')

    expect(options).toHaveLength(2)
    expect(options[0].text()).toBe(catalog['register.roleBuyer'])
    expect(options[0].attributes('value')).toBe('buyer')
    expect(options[1].text()).toBe(catalog['register.roleSeller'])
    expect(options[1].attributes('value')).toBe('seller')
  })

  it('keeps credential inputs left-to-right', () => {
    const wrapper = mountView()

    expect(wrapper.find('#email').attributes('dir')).toBe('ltr')
    expect(wrapper.find('#password').attributes('dir')).toBe('ltr')
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

  it('shows the Persian duplicate-email message', async () => {
    registerMock.mockRejectedValue(
      new ApiError(409, 'An account with this email already exists', 'duplicate_email'),
    )
    const wrapper = mountView()

    await wrapper.find('#email').setValue('buyer@example.com')
    await wrapper.find('#password').setValue('s3curePass!')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('[role="alert"]').text()).toBe(
      catalog['errors.duplicate_email'],
    )
  })
})
