import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { NotificationBell } from '../../components/notifications/NotificationBell'
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  Target,
  ClipboardList,
  Briefcase,
  BookOpen,
  BarChart3,
  Bell,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../../auth/AuthContext'

const NAV_ITEMS = [
  { path: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/users', label: 'Users', icon: Users },
  { path: '/admin/skills', label: 'Skills', icon: GraduationCap },
  { path: '/admin/careers', label: 'Careers', icon: Target },
  { path: '/admin/assessments', label: 'Assessments', icon: ClipboardList },
  { path: '/admin/opportunities', label: 'Opportunities', icon: Briefcase },
  { path: '/admin/resources', label: 'Learning Resources', icon: BookOpen },
  { path: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/admin/notifications', label: 'Notifications', icon: Bell },
]

export function AdminLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:z-auto`}
      >
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <span className="text-lg font-bold text-slate-900">SkillMap AI</span>
          <button className="lg:hidden" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <div className="px-4 py-3 border-b border-gray-100">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Admin Panel</p>
          <p className="text-sm font-medium text-slate-700 truncate">
            {user?.full_name ?? user?.username}
          </p>
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = location.pathname === item.path
            return (
              <button
                key={item.path}
                onClick={() => {
                  navigate(item.path)
                  setSidebarOpen(false)
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                  ${active
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
              >
                <item.icon className="w-4.5 h-4.5 flex-shrink-0" />
                {item.label}
              </button>
            )
          })}
        </nav>
        <div className="px-3 py-4 border-t border-gray-200">
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          >
            <LogOut className="w-4.5 h-4.5" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="flex items-center h-16 px-6 bg-white border-b border-gray-200">
          <button className="lg:hidden mr-4" onClick={() => setSidebarOpen(true)}>
            <Menu className="w-5 h-5 text-gray-500" />
          </button>
          <h1 className="text-lg font-semibold text-slate-900 flex-1">
            {NAV_ITEMS.find((i) => i.path === location.pathname)?.label ?? 'Admin'}
          </h1>
          <NotificationBell />
        </header>
        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
