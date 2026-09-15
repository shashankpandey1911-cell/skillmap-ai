import { get, post, storeTokens } from '../client'
import type { User } from '../../types'

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface RegisterPayload {
  full_name: string
  email: string
  password: string
  role: 'STUDENT' | 'PROFESSOR'
  college?: string
  course?: string
  year?: number | null
}

export interface RegisterResponse {
  user: User
  access: string
  refresh: string
}

export async function login(email: string, password: string): Promise<User> {
  const data = await post<LoginResponse>('/auth/login', { email, password })
  storeTokens(data.access, data.refresh)
  return data.user
}

export async function register(payload: RegisterPayload): Promise<User> {
  const data = await post<RegisterResponse>('/auth/register', payload)
  storeTokens(data.access, data.refresh)
  return data.user
}

export async function me(): Promise<User> {
  return get<User>('/auth/me')
}

/** Blacklists the refresh token server-side. */
export async function logout(refresh: string): Promise<void> {
  await post<{ detail: string }>('/auth/logout', { refresh })
}

export async function forgotPassword(email: string): Promise<void> {
  await post<{ detail: string }>('/auth/forgot-password', { email })
}

export async function resetPassword(uidb64: string, token: string, password: string): Promise<void> {
  await post<{ detail: string }>('/auth/reset-password', { uidb64, token, password })
}