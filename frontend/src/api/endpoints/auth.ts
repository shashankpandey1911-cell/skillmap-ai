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
  detail?: string
  /** Present only when email verification is disabled (local demos). */
  access?: string
  refresh?: string
}

export interface VerifyEmailResponse {
  detail: string
  status: 'verified' | 'already_verified' | 'expired' | 'invalid'
}

export async function login(email: string, password: string): Promise<User> {
  const data = await post<LoginResponse>('/auth/login', { email, password })
  storeTokens(data.access, data.refresh)
  return data.user
}

export async function register(payload: RegisterPayload): Promise<User | null> {
  const data = await post<RegisterResponse>('/auth/register', payload)
  if (data.access && data.refresh) {
    // Verification disabled: sign in immediately (legacy behaviour).
    storeTokens(data.access, data.refresh)
    return data.user
  }
  // Verification required: tokens withheld until the email link is used.
  return null
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

/** Consumes the emailed verification link (uid + token). */
export async function verifyEmail(uidb64: string, token: string): Promise<VerifyEmailResponse> {
  return post<VerifyEmailResponse>('/auth/verify-email', { uidb64, token })
}

/** Emails a fresh verification link. Safe to call for unknown emails. */
export async function resendVerification(email: string): Promise<void> {
  await post<{ detail: string }>('/auth/resend-verification', { email })
}
