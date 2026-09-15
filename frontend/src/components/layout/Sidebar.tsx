import { NavLink } from 'react-router-dom'
import { Compass, X } from 'lucide-react'
import { navItems, type RouteMeta } from '../../router/routes'
import { useAuth } from '../../auth/AuthContext'
import { cn } from '../../utils/cn'

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { user } = useAuth()
  if (!user) return null
  const items: RouteMeta[] = navItems(user.role)

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-navy-950/50 backdrop-blur-sm lg:hidden animate-fade-in"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex w-64 flex-col transition-transform duration-300 ease-out lg:translate-x-0',
          'gradient-navy text-white',
          open ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-white/10 px-5">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 backdrop-blur-sm">
              <Compass className="h-5 w-5 text-brand-300" aria-hidden="true" />
            </span>
            <div>
              <span className="text-base font-bold tracking-tight">
                SkillMap
              </span>
              <span className="text-brand-300 font-bold"> AI</span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl p-2 text-white/50 hover:bg-white/10 hover:text-white transition-colors lg:hidden"
            aria-label="Close navigation"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* User info */}
        <div className="border-b border-white/10 px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-sm font-semibold backdrop-blur-sm">
              {(user.first_name?.[0] ?? user.username[0] ?? '?').toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-white truncate">
                {user.full_name || user.first_name || user.username}
              </p>
              <p className="text-xs text-white/50 capitalize">{user.role.toLowerCase()}</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4" aria-label="Main navigation">
          {items.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-white/15 text-white shadow-sm backdrop-blur-sm'
                      : 'text-white/60 hover:bg-white/10 hover:text-white',
                  )
                }
              >
                {Icon && <Icon className="h-4.5 w-4.5 shrink-0" aria-hidden="true" />}
                <span>{item.title}</span>
              </NavLink>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-white/10 px-5 py-4">
          <p className="text-xs text-white/30 text-center">
            Built for Smart India Hackathon
          </p>
        </div>
      </aside>
    </>
  )
}
