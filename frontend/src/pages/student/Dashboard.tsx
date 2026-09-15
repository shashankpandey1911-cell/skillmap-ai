import { Link } from 'react-router-dom'
import {
  Briefcase,
  Calendar,
  CheckCircle2,
  GraduationCap,
  Target,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  BookOpen,
  Send,
  MapPin,
} from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import { useAuth } from '../../auth/AuthContext'
import { dashboardSummary } from '../../api/endpoints/students'
import { useApi } from '../../hooks/useApi'
import { Alert, Badge, Card, ProgressBar, Spinner, StatCard } from '../../components/ui'

const STATUS_COLORS: Record<string, string> = {
  APPLIED: '#3b82f6',
  SUBMITTED: '#6366f1',
  UNDER_REVIEW: '#f59e0b',
  SHORTLISTED: '#10b981',
  INTERVIEW: '#8b5cf6',
  SELECTED: '#22c55e',
  REJECTED: '#ef4444',
}

function CareerReadinessGauge({ value }: { value: number }) {
  const color = value >= 70 ? '#22c55e' : value >= 40 ? '#f59e0b' : '#ef4444'
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#e2e8f0" strokeWidth="8" />
          <circle
            cx="50" cy="50" r="40" fill="none" stroke={color} strokeWidth="8"
            strokeDasharray={`${value * 2.51} 251`} strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-slate-900">{value}%</span>
        </div>
      </div>
      <p className="mt-2 text-sm text-slate-500">Career Readiness</p>
    </div>
  )
}

function ApplicationsPieChart({ data }: { data: Record<string, number> }) {
  const chartData = Object.entries(data).map(([status, count]) => ({ name: status, value: count }))
  if (chartData.length === 0) return <p className="text-sm text-slate-500 text-center py-4">No applications yet</p>
  return (
    <ResponsiveContainer width="100%" height={180}>
      <PieChart>            <Pie data={chartData} cx="50%" cy="50%" outerRadius={60} dataKey="value" label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
          {chartData.map((entry) => (
            <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || '#94a3b8'} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  )
}

function SkillsBarChart({ skills }: { skills: { name: string; proficiency: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={skills} layout="vertical" margin={{ left: 60 }}>
        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={80} />
        <Tooltip />
        <Bar dataKey="proficiency" fill="#3b82f6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

function daysUntil(dateStr: string | null): string | null {
  if (!dateStr) return null
  const diff = Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000)
  if (diff < 0) return 'Past'
  if (diff === 0) return 'Today'
  if (diff === 1) return 'Tomorrow'
  return `${diff} days`
}

export function StudentDashboard() {
  const { user } = useAuth()
  const { data, loading, error } = useApi(dashboardSummary)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">
          Welcome back, {user?.full_name ?? user?.username}
        </h2>
        <p className="mt-1 text-sm text-slate-500">Your career readiness at a glance.</p>
      </div>

      {loading && <Spinner />}
      {error && <Alert tone="error">{error}</Alert>}

      {data && (
        <>
          {/* Pending feedback banner */}
          {data.feedback_pending_count > 0 && (
            <Alert tone="info" className="gap-3">
              <div className="flex w-full items-center justify-between gap-3">
                <span className="inline-flex items-center gap-2">
                  <Sparkles className="h-4 w-4 shrink-0" aria-hidden="true" />
                  {data.feedback_pending_count === 1
                    ? 'One rejected application has improvement feedback — review and accept it onto your roadmap.'
                    : `${data.feedback_pending_count} rejected applications have improvement feedback.`}
                </span>
                <Link
                  to="/student/improvement"
                  className="shrink-0 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold text-brand-800 hover:bg-white"
                >
                  Review feedback
                </Link>
              </div>
            </Alert>
          )}

          {/* Stats row */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <StatCard
              label="Career Readiness"
              value={`${data.career_readiness}%`}
              icon={Target}
              sub="Overall score"
            />
            <StatCard
              label="Top Skills"
              value={data.skills_count}
              icon={GraduationCap}
              sub="Self-rated + assessed"
            />
            <StatCard
              label="Skill Gaps"
              value={data.skill_gaps_count}
              icon={AlertTriangle}
              sub="Need improvement"
            />
            <StatCard
              label="Applications"
              value={data.applications_count}
              icon={Send}
              sub="Jobs & internships"
            />
            <StatCard
              label="Interviews"
              value={data.applications_by_status?.INTERVIEW || 0}
              icon={Briefcase}
              sub="In progress"
            />
          </div>

          {/* Main content grid */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Left column */}
            <div className="lg:col-span-2 space-y-6">
              {/* Career Readiness + Top Skills */}
              <div className="grid gap-4 sm:grid-cols-2">
                <Card title="Career Readiness" subtitle="How ready you are for your target career">
                  <div className="flex items-center justify-center py-4">
                    <CareerReadinessGauge value={data.career_readiness} />
                  </div>
                  {data.top_career_match && (
                    <div className="mt-4 p-3 bg-slate-50 rounded-lg">
                      <p className="text-sm font-medium text-slate-700">
                        Best match: <span className="text-brand-700">{data.top_career_match.title}</span>
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        {data.top_career_match.match_percentage}% match • {data.top_career_match.matching_skills.join(', ')}
                      </p>
                    </div>
                  )}
                </Card>

                <Card title="Top Skills" subtitle="Your strongest skills by proficiency">
                  {data.top_skills.length > 0 ? (
                    <SkillsBarChart skills={data.top_skills} />
                  ) : (
                    <p className="text-sm text-slate-500 text-center py-8">Add skills to see your profile</p>
                  )}
                </Card>
              </div>

              {/* Applications by Status */}
              <Card title="Applications Overview" subtitle="Status breakdown of your applications">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <ApplicationsPieChart data={data.applications_by_status || {}} />
                  </div>
                  <div className="space-y-2">
                    {Object.entries(data.applications_by_status || {}).map(([status, count]) => (
                      <div key={status} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: STATUS_COLORS[status] || '#94a3b8' }} />
                          <span className="text-slate-600">{status.replace('_', ' ')}</span>
                        </div>
                        <span className="font-medium text-slate-900">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>

              {/* Recommended Opportunities */}
              <Card
                title="Recommended Opportunities"
                subtitle="Best matches based on your skills"
                actions={
                  <Link to="/student/opportunities" className="text-sm text-brand-600 hover:text-brand-700">
                    View all →
                  </Link>
                }
              >
                {data.top_opportunities.length > 0 ? (
                  <div className="space-y-3">
                    {data.top_opportunities.map((opp) => (
                      <Link
                        key={opp.id}
                        to={`/student/opportunities/${opp.id}`}
                        className="flex items-center justify-between p-3 rounded-lg border border-slate-200 hover:border-brand-300 hover:bg-brand-50/50 transition-colors"
                      >
                        <div>
                          <p className="font-medium text-slate-900">{opp.title}</p>
                          <p className="text-sm text-slate-500">{opp.company}</p>
                        </div>
                        <Badge tone={opp.match_percentage >= 70 ? 'green' : opp.match_percentage >= 40 ? 'amber' : 'red'}>
                          {opp.match_percentage}%
                        </Badge>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 text-center py-4">No matching opportunities found</p>
                )}
              </Card>
            </div>

            {/* Right column */}
            <div className="space-y-6">
              {/* Profile Completeness */}
              <Card title="Profile Completeness" subtitle="Complete your profile for better matches">
                <div className="flex items-center gap-4">
                  <div className="relative w-16 h-16">
                    <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                      <circle cx="50" cy="50" r="40" fill="none" stroke="#e2e8f0" strokeWidth="8" />
                      <circle
                        cx="50" cy="50" r="40" fill="none" stroke="#3b82f6" strokeWidth="8"
                        strokeDasharray={`${data.profile_completeness * 2.51} 251`} strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-slate-900">{data.profile_completeness}%</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <ProgressBar value={data.profile_completeness} />
                    <p className="mt-2 text-xs text-slate-500">
                      {data.profile_completeness < 50 ? 'Add more details to unlock better matches' : 'Great progress!'}
                    </p>
                  </div>
                </div>
              </Card>

              {/* Learning Progress */}
              <Card title="Learning Progress" subtitle="Track your skill development">
                <div className="flex items-center gap-4">
                  <div className="relative w-16 h-16">
                    <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                      <circle cx="50" cy="50" r="40" fill="none" stroke="#e2e8f0" strokeWidth="8" />
                      <circle
                        cx="50" cy="50" r="40" fill="none" stroke="#8b5cf6" strokeWidth="8"
                        strokeDasharray={`${data.learning_progress * 2.51} 251`} strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-slate-900">{data.learning_progress}%</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-slate-600">
                      <span className="font-medium text-slate-900">{data.completed_resources}</span> of {data.total_resources} resources completed
                    </p>
                    <Link to="/student/learning" className="text-sm text-brand-600 hover:text-brand-700 mt-2 inline-block">
                      View roadmap →
                    </Link>
                  </div>
                </div>
              </Card>

              {/* Upcoming Deadlines */}
              <Card title="Upcoming Deadlines" subtitle="Don't miss these opportunities">
                {data.upcoming_deadlines.length > 0 ? (
                  <div className="space-y-3">
                    {data.upcoming_deadlines.map((item) => {
                      const days = daysUntil(item.deadline)
                      return (
                        <Link
                          key={item.id}
                          to={`/student/opportunities/${item.id}`}
                          className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                          <div className="min-w-0">
                            <p className="text-sm font-medium text-slate-900 truncate">{item.title}</p>
                            <p className="text-xs text-slate-500">{item.company}</p>
                          </div>
                          {days && (
                            <Badge tone={days === 'Today' || days === 'Tomorrow' || days === 'Past' ? 'red' : 'amber'}>
                              <Calendar className="h-3 w-3 mr-1" />
                              {days}
                            </Badge>
                          )}
                        </Link>
                      )
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 text-center py-4">No upcoming deadlines</p>
                )}
              </Card>

              {/* Recent Achievements */}
              <Card
                title="Career Achievements"
                subtitle="Selections recorded"
                actions={
                  <Link to="/student/improvement" className="text-sm text-brand-600 hover:text-brand-700">
                    View all →
                  </Link>
                }
              >
                {data.recent_achievements.length > 0 ? (
                  <div className="space-y-3">
                    {data.recent_achievements.map((ach) => (
                      <div key={ach.feedback_id} className="flex items-start gap-3 p-2 rounded-lg bg-emerald-50">
                        <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">{ach.title}</p>
                          <p className="text-xs text-slate-500">{ach.company} • {new Date(ach.achieved_at).toLocaleDateString()}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 text-center py-4">No achievements yet</p>
                )}
              </Card>

              {/* Quick Links */}
              <Card title="Quick Actions">
                <div className="grid grid-cols-2 gap-2">
                  <Link to="/student/improvement" className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 text-sm text-slate-700">
                    <TrendingUp className="h-4 w-4 text-brand-600" /> Career Improvement
                  </Link>
                  <Link to="/student/opportunity-matches" className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 text-sm text-slate-700">
                    <MapPin className="h-4 w-4 text-brand-600" /> Opportunity Matches
                  </Link>
                  <Link to="/student/assessments" className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 text-sm text-slate-700">
                    <BookOpen className="h-4 w-4 text-brand-600" /> Take Assessment
                  </Link>
                  <Link to="/student/careers" className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 text-sm text-slate-700">
                    <Target className="h-4 w-4 text-brand-600" /> Explore Careers
                  </Link>
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
