import { post } from './client'

export type Role = 'buyer' | 'seller'

export interface RegisterPayload {
  email: string
  password: string
  role: Role
}

export interface RegisterResult {
  id: string
  email: string
  role: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface TokenResult {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  refresh_expires_in: number
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    post<RegisterResult>('/auth/register', payload),
  login: (payload: LoginPayload) => post<TokenResult>('/auth/login', payload),
}
