import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ClipboardCheck,
  Clock,
  ExternalLink,
  GraduationCap,
  Hammer,
  Lightbulb,
  ListChecks,
  Map,
  Sparkles,
  TrendingUp,
  type LucideIcon,
} from 'lucide-react'
import {
  type LearningResource,
  type LearningRoadmap,
  type ResourceType,
  getLearningRoadmap,
  markResourceCompleted,
  markResourceIncomplete,
} from '../../api/endpoints/learning'
import { listCareers, type Career } from '../../api/endpoints/careers'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../auth/AuthContext'
import {
  Alert,
  Badge,
  type BadgeTone,
  Button,
  Card,
  ProgressBar,
  Select,
  Spinner,
  StatCard,
} from '../../components/ui'
import { cn } from '../../utils/cn'

const TYPE_LABELS: Record<ResourceType, string> = {
  COURSE: 'Course',
  VIDEO: 'Video',
  DOCUMENTATION: 'Documentation',
  PRACTICE: 'Practice',
  PROJECT: 'Project',
  QUIZ: 'Quiz',
}

const STEP_ICONS: Record<string, LucideIcon> = {
  topic: Lightbulb,
  resource: BookOpen,
  practice: Hammer,
  assessment: ClipboardCheck,
  improvement: TrendingUp,
}

const GAP_TONE: Record<string, BadgeTone> = {
  HIGH: 'red',
  MEDIUM: 'amber',
  LOW: 'brand',
}

function formatDuration(minutes: number): string {
  if (minutes >= 60) {
    const h = Math.round(minutes / 60)
    return `${h} hr${h > 1 ? 's' : ''}`
  }
  return `${minutes} min`
}

export function LearningRoadmapPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const careers = useApi(() => listCareers(), [])
  const [careerId, setCareerId] = useState<number | null>(null)
  const activeCareerId = careerId ?? careers.data?.[0]?.id ?? null

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Personalized Learning Roadmap</h2>
        <p className="mt-1 text-sm text-slate-500">
          {user?.full_name ?? user?.username}, every skill gap becomes a concrete plan — the
          roadmap below is generated from your real skill data and this career's requirements.
        </p>
      </div>

      {careers.loading ? (
        <Spinner />
      ) : careers.error ? (
        <Alert tone="error">{careers.error}</Alert>
      ) : !careers.data || careers.data.length === 0 ? (
        <Card>
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <Map className="h-10 w-10 text-slate-300" aria-hidden="true" />
            <div>
              <p className="font-medium text-slate-800">No careers published yet</p>
              <p className="mt-1 text-sm text-slate-500">
                Pick a target career from the Skill Gap Analysis to unlock your roadmap.
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
          {activeCareerId && (
            <RoadmapPanel key={activeCareerId} careerId={activeCareerId} navigateToQuiz={(id) => navigate(`/student/assessments?open=${id}`)} />
          )}
        </>
      )}
    </div>
  )
}

function RoadmapPanel({
  careerId,
  navigateToQuiz,
}: {
  careerId: number
  navigateToQuiz: (id: number) => void
}) {
  const { data, loading, error, refresh } = useApi(
    () => getLearningRoadmap(careerId),
    [careerId],
  )
  const [busyId, setBusyId] = useState<number | null>(null)
  const [toggleError, setToggleError] = useState<string | null>(null)

  if (loading) return <Spinner />
  if (error) {
    return (
      <div className="space-y-4">
        <Alert tone="error">{error}</Alert>
        <button
          type="button"
          onClick={refresh}
          className="text-sm font-medium text-brand-700 hover:text-brand-800"
        >
          Try again
        </button>
      </div>
    )
  }
  if (!data) return null

  const toggle = async (resource: LearningResource) => {
    setBusyId(resource.id)
    setToggleError(null)
    try {
      if (resource.completed) {
        await markResourceIncomplete(resource.id)
      } else {
        await markResourceCompleted(resource.id)
      }
      refresh()
    } catch (e) {
      const message =
        (e as { detail?: string; message?: string })?.detail ??
        (e as { message?: string })?.message ??
        'Could not update progress.'
      setToggleError(message)
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="space-y-6">
      <Summary progress={data.progress} readiness={data.readiness_percentage} />
      {data.roadmap.length === 0 ? (
        <AllClearCard careerTitle={data.career.title} />
      ) : (
        <>
          <PriorityStrip data={data} />
          {toggleError && <Alert tone="error">{toggleError}</Alert>}
          {data.roadmap.map((entry) => (
            <SkillRoadmapCard
              key={entry.skill.id}
              entry={entry}
              careerTitle={data.career.title}
              busyId={busyId}
              onToggle={toggle}
              navigateToQuiz={navigateToQuiz}
            />
          ))}
        </>
      )}

      {data.feedback_roadmap && data.feedback_roadmap.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center gap-2 border-t border-slate-200 pt-6">
            <Sparkles className="h-4 w-4 text-brand-700" aria-hidden="true" />
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              From application feedback
            </h3>
            <p className="text-xs text-slate-400">
              Skills you accepted after a rejection — still open gaps.
            </p>
          </div>
          {data.feedback_roadmap.map((entry) => (
            <SkillRoadmapCard
              key={`fb-${entry.source.feedback_id}-${entry.skill.id}`}
              entry={entry}
              careerTitle={`${entry.source.opportunity} · ${entry.source.company}`}
              busyId={busyId}
              onToggle={toggle}
              navigateToQuiz={navigateToQuiz}
            />
          ))}
        </section>
      )}
    </div>
  )
}

function Summary({
  progress,
  readiness,
}: {
  progress: LearningRoadmap['progress']
  readiness: number
}) {
  return (
    <>
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Learning progress"
          value={`${progress.progress_percentage}%`}
          icon={TrendingUp}
          sub="Of recommended resources completed"
        />
        <StatCard
          label="Completed resources"
          value={progress.completed_resources}
          icon={CheckCircle2}
          sub={`of ${progress.total_resources} recommended`}
        />
        <StatCard
          label="Remaining resources"
          value={progress.remaining_resources}
          icon={ListChecks}
          sub={progress.remaining_resources === 0 ? 'Roadmap complete — nice work!' : 'Still to finish'}
        />
      </div>

      <Card title="Roadmap progress" subtitle="Ticking this off updates your skill journey">
        <div className="flex items-center gap-4">
          <ProgressBar
            value={progress.progress_percentage}
            tone={
              progress.progress_percentage >= 70
                ? 'green'
                : progress.progress_percentage >= 40
                  ? 'brand'
                  : 'amber'
            }
            className="h-3 flex-1"
          />
          <span className="w-14 text-right text-lg font-bold text-slate-900">
            {progress.progress_percentage}%
          </span>
        </div>
        <p className="mt-3 text-sm text-slate-600">
          Career readiness for this target:{' '}
          <strong className="font-semibold text-slate-900">{Math.round(readiness)}%</strong> —
          complete the resources below, then retake each skill's assessment to raise your score
          and shrink the gaps.
        </p>
      </Card>
    </>
  )
}

function AllClearCard({ careerTitle }: { careerTitle: string }) {
  return (
    <Card>
      <div className="flex flex-col items-center gap-3 py-8 text-center">
        <CheckCircle2 className="h-10 w-10 text-emerald-500" aria-hidden="true" />
        <div>
          <p className="font-medium text-slate-800">No skill gaps for {careerTitle}</p>
          <p className="mt-1 text-sm text-slate-500">
            You already meet every requirement. Explore another career or push further with
            advanced assessments.
          </p>
        </div>
      </div>
    </Card>
  )
}

function PriorityStrip({ data }: { data: LearningRoadmap }) {
  return (
    <Card title="Priority skills" subtitle="Ordered by gap severity — start from the top">
      <ul className="flex flex-wrap gap-2">
        {data.priority_skills.map((skill) => (
          <li key={skill.skill_id}>
            <Badge tone={GAP_TONE[skill.gap_class] ?? 'slate'} className="gap-1.5 px-2.5 py-1">
              <AlertTriangle className="h-3 w-3" aria-hidden="true" />
              {skill.skill_name}
              <span className="opacity-70">· {Math.round(skill.gap_percentage)}% gap</span>
            </Badge>
          </li>
        ))}
      </ul>
    </Card>
  )
}

function SkillRoadmapCard({
  entry,
  careerTitle,
  busyId,
  onToggle,
  navigateToQuiz,
}: {
  entry: LearningRoadmap['roadmap'][number]
  careerTitle: string
  busyId: number | null
  onToggle: (resource: LearningResource) => void
  navigateToQuiz: (id: number) => void
}) {
  const { skill, gap } = entry
  const gapTone = GAP_TONE[gap.gap_class] ?? 'slate'
  const met = gap.gap_class === 'NONE'

  return (
    <Card
      title={
        <span className="flex flex-wrap items-center gap-2">
          <GraduationCap className="h-4 w-4 text-brand-700" aria-hidden="true" />
          {skill.name}
          <Badge tone="slate" className="capitalize">
            {skill.category}
          </Badge>
        </span>
      }
      subtitle={
        <span className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="capitalize text-slate-500">{careerTitle}</span>
          <span className="text-slate-300">·</span>
          <span className="text-slate-500">
            You: {Math.round(gap.current_level)}% · Target: {gap.required_level}%
          </span>
          <span className="text-slate-300">·</span>
          <Badge tone={gapTone}>
            {met ? 'No gap' : `${Math.round(gap.gap_percentage)}% ${gap.gap_class.toLowerCase()} gap`}
          </Badge>
        </span>
      }
    >
      <div className="flex items-start gap-2 rounded-lg bg-slate-50 px-3 py-2.5">
        <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" aria-hidden="true" />
        <p className="text-sm text-slate-700">{entry.recommended_action}</p>
      </div>

      <ol className="mt-4 space-y-4">
        {entry.steps.map((step, index) => {
          const Icon = STEP_ICONS[step.key] ?? Map
          const stepIndex = index + 1
          return (
            <li key={step.key} className="flex gap-3">
              <div className="flex flex-col items-center">
                <span
                  className={cn(
                    'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold',
                    step.key === 'improvement'
                      ? 'bg-emerald-100 text-emerald-700'
                      : step.key === 'topic'
                        ? 'bg-slate-100 text-slate-600'
                        : 'bg-brand-50 text-brand-700',
                  )}
                >
                  {step.key === 'improvement' ? <Icon className="h-4 w-4" aria-hidden="true" /> : stepIndex}
                </span>
                {stepIndex < entry.steps.length && (
                  <span className="w-px flex-1 bg-slate-200" aria-hidden="true" />
                )}
              </div>

              <div className="min-w-0 flex-1 pb-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h4 className="text-sm font-semibold text-slate-900">{step.title}</h4>
                  {step.platform_assessment && (
                    <Badge tone="brand" className="gap-1">
                      <ClipboardCheck className="h-3 w-3" aria-hidden="true" />
                      {step.platform_assessment.question_count} questions
                    </Badge>
                  )}
                </div>

                {step.description && (
                  <p className="mt-1 text-sm text-slate-600">{step.description}</p>
                )}

                {step.items.length > 0 && (
                  <ul className="mt-2 space-y-2">
                    {step.items.map((item) => (
                      <ResourceRow
                        key={item.id}
                        item={item}
                        busy={busyId === item.id}
                        onToggle={() => onToggle(item)}
                      />
                    ))}
                  </ul>
                )}

                {step.platform_assessment && (
                  <div className="mt-2 flex items-center gap-3 rounded-lg border border-brand-100 bg-brand-50/60 px-3 py-2.5">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-brand-900">
                        {step.platform_assessment.title}
                      </p>
                      <p className="text-xs text-brand-700/80">
                        {step.platform_assessment.my_last_score !== null
                          ? `Your last score: ${Math.round(step.platform_assessment.my_last_score)}%`
                          : 'Not attempted yet'}
                      </p>
                    </div>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => navigateToQuiz(step.platform_assessment!.id)}
                    >
                      Take assessment
                      <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                    </Button>
                  </div>
                )}
              </div>
            </li>
          )
        })}
      </ol>
    </Card>
  )
}

function ResourceRow({
  item,
  busy,
  onToggle,
}: {
  item: LearningResource
  busy: boolean
  onToggle: () => void
}) {
  return (
    <li
      className={cn(
        'flex items-start gap-3 rounded-lg border px-3 py-2.5 transition-colors',
        item.completed ? 'border-emerald-200 bg-emerald-50/60' : 'border-slate-200 bg-white',
      )}
    >
      <button
        type="button"
        onClick={onToggle}
        disabled={busy}
        aria-pressed={item.completed}
        className={cn(
          'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border transition-colors',
          item.completed
            ? 'border-emerald-500 bg-emerald-500 text-white'
            : 'border-slate-300 bg-white text-transparent hover:border-brand-400',
          busy && 'opacity-50',
        )}
      >
        <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
      </button>

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p
            className={cn(
              'text-sm font-medium',
              item.completed ? 'text-slate-500 line-through' : 'text-slate-800',
            )}
          >
            {item.title}
          </p>
          <Badge tone={item.type === 'QUIZ' ? 'amber' : 'slate'}>
            {TYPE_LABELS[item.type]}
          </Badge>
          <Badge tone="slate" className="capitalize">
            {item.level.toLowerCase()}
          </Badge>
          <Badge tone="slate" className="gap-1">
            <Clock className="h-3 w-3" aria-hidden="true" />
            {formatDuration(item.estimated_duration_minutes)}
          </Badge>
        </div>
        {item.description && (
          <p className="mt-0.5 text-xs text-slate-500">{item.description}</p>
        )}
        {item.url && (
          <a
            href={item.url}
            target="_blank"
            rel="noreferrer noopener"
            className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-brand-700 hover:text-brand-800"
          >
            Open resource
            <ExternalLink className="h-3 w-3" aria-hidden="true" />
          </a>
        )}
      </div>
    </li>
  )
}
