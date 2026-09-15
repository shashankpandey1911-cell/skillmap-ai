import { ShieldCheck, UserCircle2, Users, GraduationCap, Briefcase, Target, BookOpen } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { dashboardSummary } from '../../api/endpoints/admin'
import { useApi } from '../../hooks/useApi'
import { Alert, Card, Spinner, StatCard } from '../../components/ui'

export function AdminDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { data, loading, error } = useApi(dashboardSummary)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">
          Welcome, {user?.full_name ?? user?.username}
        </h2>
        <p className="mt-1 text-sm text-slate-500">Platform health and user overview.</p>
      </div>

      {loading && <Spinner />}
      {error && <Alert tone="error">{error}</Alert>}
      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Total users" value={data.total_users} icon={Users} sub="All roles" />
            <StatCard label="Students" value={data.students} icon={UserCircle2} sub="Career profiles" />
            <StatCard
              label="Professors"
              value={data.professors}
              icon={GraduationCap}
              sub="Guidance team"
            />
            <StatCard label="Admins" value={data.admins} icon={ShieldCheck} sub="Platform access" />
          </div>

          <Card title="Quick Actions" subtitle="Jump to an admin section">
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {[
                { label: 'Manage Users', path: '/admin/users', icon: Users },
                { label: 'Manage Skills', path: '/admin/skills', icon: GraduationCap },
                { label: 'Manage Careers', path: '/admin/careers', icon: Target },
                { label: 'Manage Assessments', path: '/admin/assessments', icon: GraduationCap },
                { label: 'Manage Opportunities', path: '/admin/opportunities', icon: Briefcase },
                { label: 'Manage Resources', path: '/admin/resources', icon: BookOpen },
              ].map((item) => (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 text-left transition-colors"
                >
                  <item.icon className="h-5 w-5 text-blue-600 shrink-0" />
                  <span className="text-sm font-medium text-slate-700">{item.label}</span>
                </button>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  )
}