import { useCallback, useEffect, useRef, useState } from 'react'
import type { ApiError } from '../types'

interface UseApiResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refresh: () => void
}

/** Fetch-on-mount hook with loading/error state and a manual refresh. */
export function useApi<T>(fetcher: () => Promise<T>, deps: unknown[] = []): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetcherRef
      .current()
      .then((d) => {
        if (!cancelled) {
          setData(d)
          setError(null)
        }
      })
      .catch((e: ApiError & { message?: string }) => {
        if (!cancelled) {
          setError(e?.detail ?? e?.message ?? 'Something went wrong.')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick])

  const refresh = useCallback(() => setTick((t) => t + 1), [])

  return { data, loading, error, refresh }
}