import { ClipboardList, MessageSquare, UserCircle2, Users } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { dashboardSummary } from '../../api/endpoints/professors'
import { useApi } from '../../hooks/useApi'
import { Alert, Card, ProgressBar, Spinner, StatCard } from '../../components/ui'

export function ProfessorDashboard() {
  const { user } = useAuth()
  const { data, loading, error } = useApi(dashboardSummary)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">
          Welcome, {user?.full_name ?? user?.username}
        </h2>
        <p className="mt-1 text-sm text-slate-500">Your students' career readiness at a glance.</p>
      </div>

      {loading && <Spinner />}
      {error && <Alert tone="error">{error}</Alert>}
      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Students" value={data.total_students} icon={Users} sub="Registered students" />
            <StatCard
              label="Profiles created"
              value={data.students_with_profiles}
              icon={UserCircle2}
              sub="Digital career profiles"
            />
            <StatCard
              label="Avg. profile completeness"
              value={`${data.avg_profile_completeness}%`}
              icon={ClipboardList}
              sub="Across all students"
            />
            <StatCard
              label="Guidance given"
              value={data.feedback_given}
              icon={MessageSquare}
              sub="Feedback notes"
            />
          </div>

          <Card
            title="Cohort profile completeness"
            subtitle="How complete your students' career profiles are on average"
          >
            <ProgressBar value={data.avg_profile_completeness} />
            <p className="mt-2 text-sm text-slate-500">
              Encourage students to complete their profiles so gap analysis and career
              matches are accurate.
            </p>
          </Card>
        </>
      )}
    </div>
  )
}