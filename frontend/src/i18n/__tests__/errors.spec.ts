import { describe, expect, it } from 'vitest'

import { ApiError } from '../../api/client'
import { catalog } from '../fa'
import { messageForError } from '../errors'

describe('Persian error messages', () => {
  it.each([
    'invalid_credentials',
    'duplicate_email',
    'unauthorized',
    'invalid_token',
  ])('maps backend code %s to its Persian message', (code) => {
    const error = new ApiError(400, 'English backend message', code)
    const expected = catalog[`errors.${code}` as keyof typeof catalog]

    expect(messageForError(error)).toBe(expected)
  })

  it('uses the Persian fallback for an unknown error code', () => {
    const error = new ApiError(500, 'Unknown backend failure', 'something_new')
    expect(messageForError(error)).toBe(catalog['errors.fallback'])
  })

  it('uses the Persian fallback for non-ApiError failures', () => {
    expect(messageForError(new Error('network down'))).toBe(catalog['errors.fallback'])
  })

  it('never returns the English backend message', () => {
    const error = new ApiError(401, 'Invalid email or password', 'invalid_credentials')
    expect(messageForError(error)).not.toContain('Invalid')
  })
})
