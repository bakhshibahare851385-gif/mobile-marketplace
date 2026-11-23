/** Translate backend error codes into Persian without parsing English text. */
import { ApiError } from '../api/client'
import { catalog, type MessageKey } from './fa'

const codeToKey: Record<string, MessageKey> = {
  invalid_credentials: 'errors.invalid_credentials',
  duplicate_email: 'errors.duplicate_email',
  unauthorized: 'errors.unauthorized',
  invalid_token: 'errors.invalid_token',
}

export function messageForError(error: unknown): string {
  if (error instanceof ApiError && error.code && error.code in codeToKey) {
    return catalog[codeToKey[error.code]]
  }
  return catalog['errors.fallback']
}
