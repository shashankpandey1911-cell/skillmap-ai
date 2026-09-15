import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  login as apiLogin,
  logout as apiLogout,
  me as fetchMe,
  register as apiRegister,
} from '../api/endpoints/auth'
import { clearTokens, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '../api/client'
import type { User } from '../types'

interface AuthContextValue {
  user: User | null
  /** True while restoring the session on first load. */
  loading: boolean
  login: (username: string, password: string) => Promise<User>
  register: (payload: Parameters<typeof apiRegister>[0]) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState<boolean>(() => Boolean(localStorage.getItem(ACCESS_TOKEN_KEY)))

  // Restore the session: if we hold a token, ask the API who we are.
  useEffect(() => {
    if (!localStorage.getItem(ACCESS_TOKEN_KEY)) return
    let cancelled = false
    fetchMe()
      .then((u) => {
        if (!cancelled) setUser(u)
      })
      .catch(() => {
        // 401s are handled by the interceptor; other failures just mean
        // "not logged in yet" from the app's perspective.
        if (!cancelled) setUser(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const u = await apiLogin(username, password)
    setUser(u)
    return u
  }, [])

  const register = useCallback(async (payload: Parameters<typeof apiRegister>[0]) => {
    const u = await apiRegister(payload)
    setUser(u)
    return u
  }, [])

  const logout = useCallback(() => {
    // Best-effort server-side blacklist, then drop the local session.
    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (refresh) {
      apiLogout(refresh).catch(() => undefined)
    }
    clearTokens()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// oxlint-disable-next-line react/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an <AuthProvider>')
  }
  return ctx
}