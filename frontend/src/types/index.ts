/**
 * Types shared across the app. These mirror the Django models/serializers
 * so a backend rename fails the build instead of breaking at runtime.
 */

export type Role = 'STUDENT' | 'PROFESSOR' | 'ADMIN'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  first_name: string
  last_name: string
  role: Role
  phone?: string
  avatar?: string | null
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

/** DRF-style error payloads. */
export interface ApiError {
  detail?: string
  [key: string]: unknown
}