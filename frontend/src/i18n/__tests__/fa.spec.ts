import { describe, expect, it } from 'vitest'

import { catalog, t } from '../fa'

describe('Persian catalog', () => {
  it('has a non-empty value for every key', () => {
    for (const [key, value] of Object.entries(catalog)) {
      expect(value, key).toBeTruthy()
    }
  })

  it('contains no English UI strings', () => {
    for (const [key, value] of Object.entries(catalog)) {
      expect(value, key).not.toMatch(/[A-Za-z]{3,}/)
    }
  })

  it('returns the catalog value through t()', () => {
    expect(t('login.title')).toBe(catalog['login.title'])
    expect(t('register.submit')).toBe(catalog['register.submit'])
  })
})
