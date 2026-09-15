import { useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Target,
  TrendingUp,
} from 'lucide-react'
import {
  type Career,
  type GapAnalysis,
  type GapClass,
  type Priority,
  getGapAnalysis,
  listCareers,
} from '../../api/endpoints/careers'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../auth/AuthContext'
import {
  Alert,
  Badge,
  type BadgeTone,
  Card,
  ProgressBar,
  Select,
  Spinner,
  StatCard,
} from '../../components/ui'
import { cn } from '../../utils/cn'

function gapTone(gapClass: GapClass): BadgeTone {
  if (gapClass === 'NONE') return 'green'
  if (gapClass === 'LOW') return 'brand'
  if (gapClass === 'MEDIUM') return 'amber'
  return 'red'
}

function priorityTone(priority: Priority): BadgeTone {
  if (priority === 'NONE') return 'slate'
  if (priority === 'LOW') return 'brand'
  if (priority === 'MEDIUM') return 'amber'
  return 'red'
}

function readinessTone(value: number): 'green' | 'brand' | 'amber' | 'red' {
  if (value >= 70) return 'green'
  if (value >= 50) return 'brand'
  if (value >= 30) return 'amber'
  return 'red'
}

const GAP_LABELS: Record<GapClass, string> = {
  NONE: 'No gap',
  LOW: 'Low gap',
  MEDIUM: 'Medium gap',
  HIGH: 'High gap',
}

export function SkillGapPage() {
  const { user } = useAuth()
  const careers = useApi(() => listCareers(), [])
  const [careerId, setCareerId] = useState<number | null>(null)
  const activeCareerId = careerId ?? careers.data?.[0]?.id ?? null

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Skill Gap Analysis</h2>
        <p className="mt-1 text-sm text-slate-500">
          {user?.full_name ?? user?.username}, see how close you are to your target
          career — gaps are calculated live from your skills and the career's
          requirements.
        </p>
      </div>

      {careers.loading ? (
        <Spinner />
      ) : careers.error ? (
        <Alert tone="error">{careers.error}</Alert>
      ) : !careers.data || careers.data.length === 0 ? (
        <Card>
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <Target className="h-10 w-10 text-slate-300" aria-hidden="true" />
            <div>
              <p className="font-medium text-slate-800">No careers published yet</p>
              <p className="mt-1 text-sm text-slate-500">
                The admin defines career paths and their required skills here.
              </p>
            </div>
          </div>
        </Card>
      ) : (
        <>
          <div className="max-w-md">
            <Select
              label="Target career"
              value={String(activeCareerId ?? '')}
              onChange={(e) => setCareerId(Number(e.target.value))}
              options={careers.data.map((career: Career) => ({
                value: String(career.id),
                label: career.title,
              }))}
            />
          </div>
          {activeCareerId && <GapPanel key={activeCareerId} careerId={activeCareerId} />}
        </>
      )}
    </div>
  )
}

function GapPanel({ careerId }: { careerId: number }) {
  const { data, loading, error, refresh } = useApi(
    () => getGapAnalysis(careerId),
    [careerId],
  )

  if (loading) return <Spinner />
  if (error) {
    return (
      <div className="space-y-4">
        <Alert tone="error">{error}</Alert>
        <ButtonRetry onClick={refresh} />
      </div>
    )
  }
  if (!data) return null

  return (
    <div className="space-y-6">
      <SummaryCards analysis={data} />
      <GapBreakdown analysis={data} />
    </div>
  )
}

function ButtonRetry({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-sm font-medium text-brand-700 hover:text-brand-800"
    >
      Try again
    </button>
  )
}

function SummaryCards({ analysis }: { analysis: GapAnalysis }) {
  const tone = readinessTone(analysis.readiness_percentage)
  const gapsToClose =
    analysis.summary.low + analysis.summary.medium + analysis.summary.high
  const highPriority = analysis.gaps.filter((g) => g.priority === 'HIGH').length

  return (
    <>
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Career readiness"
          value={`${Math.round(analysis.readiness_percentage)}%`}
          icon={TrendingUp}
          sub="Average of current vs required levels"
        />
        <StatCard
          label="Skills to close"
          value={gapsToClose}
          icon={Target}
          sub={`of ${analysis.summary.total} required skills`}
        />
        <StatCard
          label="High-priority gaps"
          value={highPriority}
          icon={AlertTriangle}
          sub={highPriority === 0 ? 'Nothing critical pending' : 'Focus on these first'}
        />
      </div>

      <Card
        title="Overall readiness"
        subtitle={`${analysis.career.title} · ${analysis.career.category}`}
      >
        <div className="flex items-center gap-4">
          <ProgressBar
            value={analysis.readiness_percentage}
            tone={tone}
            className="h-3 flex-1"
          />
          <span className="w-14 text-right text-lg font-bold text-slate-900">
            {Math.round(analysis.readiness_percentage)}%
          </span>
        </div>
        <p className="mt-3 text-sm text-slate-600">
          {analysis.readiness_percentage >= 70
            ? 'You are in strong shape for this career. Maintain your strengths and polish the remaining gaps.'
            : analysis.readiness_percentage >= 40
              ? 'A solid foundation — close the highest-priority gaps first to move the needle.'
              : 'There is meaningful work ahead. Start with the high-priority gaps below.'}
        </p>
      </Card>
    </>
  )
}

function GapBreakdown({ analysis }: { analysis: GapAnalysis }) {
  return (
    <Card
      title="Skill-by-skill breakdown"
      subtitle="Current vs required level, gap size and what to do about it"
    >
      {analysis.gaps.length === 0 ? (
        <p className="py-4 text-center text-sm text-slate-500">
          This career has no skill requirements yet.
        </p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {analysis.gaps.map((gap) => {
            const met = gap.gap_class === 'NONE'
            return (
              <li key={gap.skill_id} className="py-4 first:pt-0 last:pb-0">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
                  <div className="min-w-0 lg:w-72">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="text-sm font-semibold text-slate-900">
                        {gap.skill_name}
                      </p>
                      {!met && (
                        <Badge tone={gapTone(gap.gap_class)}>
                          {GAP_LABELS[gap.gap_class]}
                        </Badge>
                      )}
                      {met && (
                        <Badge tone="green" className="gap-1">
                          <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
                          No gap
                        </Badge>
                      )}
                      <Badge tone="slate" className="capitalize">
                        {gap.category}
                      </Badge>
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      {gap.current_level === 0 && !met
                        ? 'Not on your profile yet'
                        : `Importance: ${gap.importance.toLowerCase()}`}
                    </p>
                  </div>

                  <div className="flex-1 space-y-2">
                    <LevelRow
                      label="Current"
                      value={gap.current_level}
                      tone={met ? 'green' : 'brand'}
                      hint={gap.current_level === 0 && !met ? 'Add this skill' : undefined}
                    />
                    <LevelRow label="Required" value={gap.required_level} tone="slate" />
                  </div>

                  <div className="flex items-center gap-4 lg:w-48 lg:justify-end lg:gap-6">
                    <div className="text-right">
                      <p className="text-xs text-slate-500">Gap</p>
                      <p
                        className={cn(
                          'text-lg font-bold',
                          met
                            ? 'text-emerald-600'
                            : gap.gap_class === 'LOW'
                              ? 'text-brand-700'
                              : gap.gap_class === 'MEDIUM'
                                ? 'text-amber-600'
                                : 'text-red-600',
                        )}
                      >
                        {met ? '—' : `${Math.round(gap.gap_percentage)}%`}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500">Priority</p>
                      <Badge tone={priorityTone(gap.priority)}>
                        {gap.priority === 'NONE' ? 'Met' : gap.priority}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="mt-3 flex items-start gap-2 rounded-lg bg-slate-50 px-3 py-2.5">
                  <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" aria-hidden="true" />
                  <p className="text-sm text-slate-700">{gap.recommended_action}</p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </Card>
  )
}

function LevelRow({
  label,
  value,
  tone,
  hint,
}: {
  label: string
  value: number
  tone: 'brand' | 'green' | 'slate'
  hint?: string
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-16 shrink-0 text-xs text-slate-500">{label}</span>
      <ProgressBar value={value} tone={tone} className="flex-1" />
      <span className="w-12 shrink-0 text-right text-xs font-medium text-slate-700">
        {Math.round(value)}%
      </span>
      {hint && (
        <span className="hidden w-24 shrink-0 text-right text-xs text-slate-400 sm:block">
          <ArrowRight className="mr-1 inline h-3 w-3" aria-hidden="true" />
          {hint}
        </span>
      )}
    </div>
  )
}