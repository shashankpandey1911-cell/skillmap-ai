import { isAxiosError } from 'axios'
import type { ApiError } from '../types'

/** First readable message from a DRF error payload, or a fallback. */
export function extractApiError(err: unknown, fallback = 'Something went wrong. Please try again.'): string {
  if (isAxiosError<ApiError>(err) && err.response?.data) {
    const data = err.response.data
    if (typeof data.detail === 'string') return data.detail
    const nonField = data.non_field_errors
    if (Array.isArray(nonField) && typeof nonField[0] === 'string') return nonField[0]
    for (const value of Object.values(data)) {
      if (typeof value === 'string') return value
      if (Array.isArray(value) && typeof value[0] === 'string') return value[0]
    }
  }
  return err instanceof Error ? err.message : fallback
}

/** Per-field DRF errors: {college: "This field is required."} */
export function extractFieldErrors(err: unknown): Record<string, string> {
  if (!isAxiosError<ApiError>(err) || !err.response?.data) return {}
  const out: Record<string, string> = {}
  for (const [key, value] of Object.entries(err.response.data)) {
    if (key === 'detail' || key === 'non_field_errors') continue
    if (Array.isArray(value) && typeof value[0] === 'string') out[key] = value[0]
    else if (typeof value === 'string') out[key] = value
  }
  return out
}
