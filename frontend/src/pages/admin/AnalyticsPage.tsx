import { useState, useEffect } from 'react'
import {
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, Tooltip, Legend,
} from 'recharts'
import { getAnalytics, type AdminAnalytics } from '../../api/endpoints/admin'
import { Alert, Card, Spinner, StatCard } from '../../components/ui'
import {
  Users, Briefcase, ClipboardList, Target,
  GraduationCap, BookOpen,
} from 'lucide-react'

const ROLE_COLORS: Record<string, string> = {
  STUDENT: '#3B82F6',
  PROFESSOR: '#8B5CF6',
  ADMIN: '#F59E0B',
}

const STATUS_COLORS: Record<string, string> = {
  APPLIED: '#3B82F6',
  SUBMITTED: '#6366F1',
  UNDER_REVIEW: '#F59E0B',
  SHORTLISTED: '#8B5CF6',
  INTERVIEW: '#F97316',
  SELECTED: '#10B981',
  REJECTED: '#EF4444',
}

export function AnalyticsPage() {
  const [data, setData] = useState<AdminAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getAnalytics()
      .then(setData)
      .catch(() => setError('Failed to load analytics'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spinner />
  if (error) return <Alert tone="error">{error}</Alert>
  if (!data) return null

  const roleData = data.users_by_role.map((r) => ({
    name: r.role,
    value: r.count,
  }))

  const statusData = data.applications_by_status.map((s) => ({
    name: s.status.replace('_', ' '),
    value: s.count,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Platform Analytics</h2>
        <p className="text-sm text-gray-500 mt-1">Overview of platform usage and metrics</p>
      </div>

      {/* Top Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Users" value={data.total_users} icon={Users} sub="All roles" />
        <StatCard label="Students" value={data.total_students} icon={GraduationCap} sub="Career profiles" />
        <StatCard label="Opportunities" value={data.total_opportunities} icon={Briefcase} sub={`${data.active_opportunities} active`} />
        <StatCard label="Applications" value={data.total_applications} icon={ClipboardList} sub={`${data.selected_students} selected`} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Skills" value={data.total_skills} icon={Target} sub="In catalog" />
        <StatCard label="Careers" value={data.total_careers} icon={Target} sub="Career paths" />
        <StatCard label="Assessments" value={data.total_assessments} icon={ClipboardList} sub={`${data.published_assessments} published`} />
        <StatCard label="Resources" value={data.total_learning_resources} icon={BookOpen} sub="Learning items" />
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Users by Role Pie */}
        <Card title="Users by Role">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={roleData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {roleData.map((entry) => (
                  <Cell key={entry.name} fill={ROLE_COLORS[entry.name] ?? '#94A3B8'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Applications by Status Pie */}
        <Card title="Applications by Status">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {statusData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS[entry.name.toUpperCase().replace(' ', '_')] ?? '#94A3B8'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Popular Skills Bar Chart */}
      {data.popular_skills.length > 0 && (
        <Card title="Popular Skills (by student count)">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.popular_skills}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="student_count" name="Students" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Popular Careers Bar Chart */}
      {data.popular_careers.length > 0 && (
        <Card title="Popular Careers (by requirement count)">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.popular_careers}>
              <XAxis dataKey="title" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="req_count" name="Requirements" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Common Skill Gaps */}
      {data.common_skill_gaps.length > 0 && (
        <Card title="Common Skill Gaps">
          <div className="space-y-3">
            {data.common_skill_gaps.map((gap, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-slate-900">{gap.skill}</p>
                  <p className="text-xs text-gray-500">{gap.category}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-red-600">
                    Required by {gap.required_by} · Have {gap.students_have}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
