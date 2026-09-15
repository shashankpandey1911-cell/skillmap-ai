import { Navigate, useLocation } from 'react-router-dom'
import { Spinner } from '../components/ui/Spinner'
import { useAuth } from './AuthContext'
import type { Role } from '../types'

/** Default landing path for each role (also the fallback when a user hits
 *  a page they are not allowed to see). */
// oxlint-disable-next-line react/only-export-components
export const roleHome: Record<Role, string> = {
  STUDENT: '/student/dashboard',
  PROFESSOR: '/professor/dashboard',
  ADMIN: '/admin/dashboard',
}

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner label="Loading…" />
      </div>
    )
  }
  if (!user) {
    return <Navigate to="/auth/login" replace state={{ from: location.pathname }} />
  }
  return children
}

/** Restricts a subtree to one role; redirects elsewhere otherwise. */
export function RequireRole({ role, children }: { role: Role; children: React.ReactNode }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/auth/login" replace />
  if (user.role !== role) return <Navigate to={roleHome[user.role]} replace />
  return children
}