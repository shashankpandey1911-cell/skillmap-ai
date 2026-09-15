import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import { Users, Target, AlertTriangle, TrendingUp, Award } from 'lucide-react'
import { getAnalytics, type ProfessorAnalytics } from '../../api/endpoints/professors'
import { Card, Spinner, StatCard } from '../../components/ui'

const COLORS = ['#22c55e', '#f59e0b', '#ef4444']

export function ProfessorAnalytics() {
  const [data, setData] = useState<ProfessorAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true)
      try {
        const result = await getAnalytics()
        setData(result)
      } catch (err: any) {
        setError(err.message || 'Failed to load analytics')
      } finally {
        setLoading(false)
      }
    }
    fetchAnalytics()
  }, [])

  if (loading) return <Spinner />
  if (error) return <div className="text-red-600">{error}</div>
  if (!data) return null

  const readinessData = [
    { name: 'High', value: data.readiness_distribution.high },
    { name: 'Medium', value: data.readiness_distribution.medium },
    { name: 'Low', value: data.readiness_distribution.low },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Analytics</h2>
        <p className="mt-1 text-sm text-slate-500">
          Cohort overview and student performance analytics.
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Students"
          value={data.total_students}
          icon={Users}
          sub="Registered students"
        />
        <StatCard
          label="Career Ready"
          value={data.career_ready_students}
          icon={Target}
          sub={`${data.total_students > 0 ? Math.round(data.career_ready_students / data.total_students * 100) : 0}% of cohort`}
        />
        <StatCard
          label="With Skill Gaps"
          value={data.students_with_gaps}
          icon={AlertTriangle}
          sub="Need improvement"
        />
        <StatCard
          label="Avg Assessment"
          value={`${data.avg_assessment_score}%`}
          icon={TrendingUp}
          sub="Across all attempts"
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Readiness Distribution */}
        <Card title="Career Readiness Distribution" subtitle="How students score against career requirements">
          <div className="flex items-center justify-center py-4">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={readinessData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {readinessData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Students by Year */}
        <Card title="Students by Year" subtitle="Distribution across academic years">
          <div className="py-4">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data.students_by_year}>
                <XAxis dataKey="year" label={{ value: 'Year', position: 'bottom', offset: -5 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Students" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Popular Career Goals */}
      <Card title="Popular Career Goals" subtitle="Most common career aspirations">
        {data.popular_career_goals.length > 0 ? (
          <div className="space-y-3">
            {data.popular_career_goals.map((goal, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 capitalize">{goal.goal}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-brand-600 h-2 rounded-full"
                      style={{ width: `${(goal.count / data.total_students) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-slate-500 w-8 text-right">{goal.count}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500 text-center py-4">No career goals recorded yet</p>
        )}
      </Card>

      {/* Common Skill Gaps */}
      <Card title="Common Skill Gaps" subtitle="Skills most students need to improve">
        {data.common_skill_gaps.length > 0 ? (
          <div className="space-y-3">
            {data.common_skill_gaps.map((gap, i) => (
              <div key={i} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900">{gap.skill}</p>
                  <p className="text-xs text-slate-500">
                    {gap.affected_students} student{gap.affected_students !== 1 ? 's' : ''} affected
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-red-600">{gap.avg_gap}% avg gap</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Award className="h-12 w-12 mx-auto text-emerald-500" />
            <p className="mt-2 text-slate-500">No significant skill gaps across the cohort</p>
          </div>
        )}
      </Card>
    </div>
  )
}
