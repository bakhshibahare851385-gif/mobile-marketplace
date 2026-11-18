const API_BASE = '/api/v1'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly code?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    let code: string | undefined
    try {
      const payload = await response.json()
      code = payload?.error?.code
      message = payload?.error?.message ?? payload?.detail ?? message
    } catch {
      // Non-JSON error body — keep the generic message.
    }
    throw new ApiError(response.status, message, code)
  }

  return (await response.json()) as T
}
