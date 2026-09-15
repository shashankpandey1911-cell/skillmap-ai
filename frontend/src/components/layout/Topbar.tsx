import { useNavigate } from 'react-router-dom'
import { LogOut, Menu } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { Badge } from '../ui/Badge'
import { NotificationBell } from '../notifications/NotificationBell'
import type { RouteMeta } from '../../router/routes'


export function Topbar({
  meta,
  onOpenSidebar,
}: {
  meta?: RouteMeta
  onOpenSidebar: () => void
}) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/auth/login', { replace: true })
  }

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-gray-100 bg-white/80 px-4 backdrop-blur-md sm:px-6">
      {/* Mobile menu button */}
      <button
        type="button"
        onClick={onOpenSidebar}
        className="rounded-xl p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors lg:hidden"
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Page title */}
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-base font-semibold text-gray-900 sm:text-lg">
          {meta?.title ?? 'SkillMap AI'}
        </h1>
        {meta && (
          <p className="hidden truncate text-xs text-gray-500 sm:block">
            {meta.description}
          </p>
        )}
      </div>

      {/* Right side */}
      {user && (
        <div className="flex items-center gap-3">
          <NotificationBell />

          {/* User avatar + info */}
          <div className="hidden items-center gap-3 sm:flex">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {user.first_name || user.username}
              </p>
              <Badge tone="brand" className="mt-0.5 normal-case">
                {user.role.toLowerCase()}
              </Badge>
            </div>
            <div
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-600 text-sm font-bold text-white shadow-sm"
              aria-hidden="true"
            >
              {(user.first_name?.[0] ?? user.username[0] ?? '?').toUpperCase()}
            </div>
          </div>

          {/* Logout button */}
          <button
            type="button"
            onClick={handleLogout}
            className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200"
          >
            <LogOut className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      )}
    </header>
  )
}
