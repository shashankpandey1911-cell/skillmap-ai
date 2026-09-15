import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Award,
  BarChart3,
  BookOpenCheck,
  CheckCircle2,
  ChevronDown,
  ClipboardCheck,
  Clock,
  Play,
  RotateCcw,
  Trophy,
  XCircle,
  type LucideIcon,
} from 'lucide-react'
import {
  type AssessmentInfo,
  type AssessmentResultRecord,
  DIFFICULTY_LABELS,
  listAssessments,
  listMyResults,
} from '../../api/endpoints/assessments'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../auth/AuthContext'
import { Alert, Badge, Button, Card, ProgressBar, Spinner, StatCard } from '../../components/ui'
import { cn } from '../../utils/cn'
import { QuizRunner } from './assessments/QuizRunner'

const DIFFICULTY_ICONS: Record<string, LucideIcon> = {
  BEGINNER: BarChart3,
  INTERMEDIATE: BarChart3,
  ADVANCED: Award,
  EXPERT: Trophy,
}

function toneForScore(score: number): 'brand' | 'green' | 'amber' | 'red' {
  if (score >= 85) return 'green'
  if (score >= 60) return 'brand'
  if (score >= 40) return 'amber'
  return 'red'
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function MyAssessmentsPage() {
  const { user } = useAuth()
  const fetchAll = useMemo(
    () => async () => {
      const [assessments, results] = await Promise.all([listAssessments(), listMyResults()])
      return { assessments, results }
    },
    [],
  )
  const { data, loading, error, refresh } = useApi(fetchAll)
  const [manualActive, setManualActive] = useState<AssessmentInfo | null>(null)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()

  const results = data?.results ?? []
  const assessments = data?.assessments ?? []

  // Deep link: /student/assessments?open=<id> auto-starts that assessment
  // (used by the Learning Roadmap's "Take assessment" step). Derived state
  // (no effect): once the param is cleared the quiz closes again.
  const requestedOpen = searchParams.get('open')
  const deepLinked =
    requestedOpen && data
      ? (data.assessments.find((a) => String(a.id) === requestedOpen) ?? null)
      : null
  const active = manualActive ?? deepLinked

  const closeQuiz = () => {
    if (requestedOpen) setSearchParams({}, { replace: true })
    setManualActive(null)
  }
  const avgScore = results.length
    ? Math.round(results.reduce((sum, r) => sum + r.score, 0) / results.length)
    : 0

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Skill Assessments</h2>
        <p className="mt-1 text-sm text-slate-500">
          {user?.full_name ?? user?.username}, prove your skills with timed quizzes — every
          score updates your skill record automatically.
        </p>
      </div>

      {loading ? (
        <Spinner />
      ) : error ? (
        <Alert tone="error">{error}</Alert>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard label="Assessments available" value={assessments.length} icon={ClipboardCheck} sub="Published by the admin" />
            <StatCard label="Completed" value={results.length} icon={BookOpenCheck} sub="Submitted attempts" />
            <StatCard label="Average score" value={`${avgScore}%`} icon={Award} sub="Across your attempts" />
          </div>

          {assessments.length === 0 ? (
            <Card>
              <div className="flex flex-col items-center gap-3 py-8 text-center">
                <BookOpenCheck className="h-10 w-10 text-slate-300" aria-hidden="true" />
                <div>
                  <p className="font-medium text-slate-800">No assessments published yet</p>
                  <p className="mt-1 text-sm text-slate-500">
                    The admin publishes skill assessments here as they go live.
                  </p>
                </div>
              </div>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {assessments.map((assessment) => {
                const DifficultyIcon = DIFFICULTY_ICONS[assessment.difficulty] ?? BarChart3
                const attempted = assessment.my_attempts > 0
                return (
                  <Card
                    key={assessment.id}
                    className="flex flex-col"
                    title={assessment.title}
                    subtitle={
                      <span className="flex flex-wrap items-center gap-x-2">
                        <span className="font-medium text-brand-700">{assessment.skill.name}</span>
                        <span className="text-slate-400">·</span>
                        <span className="capitalize text-slate-500">{assessment.skill.category}</span>
                      </span>
                    }
                    actions={
                      assessment.my_last_score !== null ? (
                        <Badge tone={toneForScore(assessment.my_last_score)}>
                          Last {Math.round(assessment.my_last_score)}%
                        </Badge>
                      ) : undefined
                    }
                  >
                    <p className="min-h-10 text-sm text-slate-600">{assessment.description}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                      <Badge tone="slate" className="gap-1">
                        <DifficultyIcon className="h-3 w-3" aria-hidden="true" />
                        {DIFFICULTY_LABELS[assessment.difficulty]}
                      </Badge>
                      <Badge tone="slate" className="gap-1">
                        <Clock className="h-3 w-3" aria-hidden="true" />
                        {assessment.duration_minutes} min
                      </Badge>
                      <Badge tone="slate" className="gap-1">
                        <BookOpenCheck className="h-3 w-3" aria-hidden="true" />
                        {assessment.question_count} questions
                      </Badge>
                      {attempted && (
                        <Badge tone="brand">
                          Taken {assessment.my_attempts}×
                        </Badge>
                      )}
                    </div>
                    <div className="mt-4 flex justify-end border-t border-slate-100 pt-4">
                      <Button
                        onClick={() => setManualActive(assessment)}
                        disabled={assessment.question_count === 0}
                      >
                        {assessment.my_last_score !== null ? (
                          <>
                            <RotateCcw className="h-4 w-4" aria-hidden="true" />
                            Retake
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4" aria-hidden="true" />
                            Start assessment
                          </>
                        )}
                      </Button>
                    </div>
                  </Card>
                )
              })}
            </div>
          )}

          {/* History */}
          <Card
            title="Attempt history"
            subtitle={results.length ? 'Your past results — expand to review answers' : undefined}
          >
            {results.length === 0 ? (
              <p className="py-4 text-center text-sm text-slate-500">
                Nothing here yet. Take your first assessment to build your history.
              </p>
            ) : (
              <ul className="space-y-3">
                {results.map((record) => (
                  <HistoryRow
                    key={record.id}
                    record={record}
                    open={expanded === record.id}
                    onToggle={() => setExpanded(expanded === record.id ? null : record.id)}
                  />
                ))}
              </ul>
            )}
          </Card>
        </>
      )}

      {active && (
        <QuizRunner
          key={active.id}
          assessment={active}
          onExit={() => {
            closeQuiz()
            refresh()
          }}
        />
      )}
    </div>
  )
}

function HistoryRow({
  record,
  open,
  onToggle,
}: {
  record: AssessmentResultRecord
  open: boolean
  onToggle: () => void
}) {
  return (
    <li className="rounded-lg border border-slate-200">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center gap-4 px-4 py-3 text-left"
        aria-expanded={open}
      >
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-slate-900">
            {record.assessment.title}
          </p>
          <p className="text-xs text-slate-500">
            {record.assessment.skill.name} · {formatDate(record.submitted_at)} ·{' '}
            {record.correct_count}/{record.total_questions} correct
          </p>
        </div>
        <div className="w-24 shrink-0">
          <ProgressBar value={record.score} tone={toneForScore(record.score)} />
        </div>
        <span className="w-12 shrink-0 text-right text-sm font-semibold text-slate-800">
          {Math.round(record.score)}%
        </span>
        <ChevronDown
          className={cn('h-4 w-4 shrink-0 text-slate-400 transition-transform', open && 'rotate-180')}
          aria-hidden="true"
        />
      </button>
      {open && (
        <ol className="space-y-2 border-t border-slate-100 px-4 py-3">
          {record.review.map((item) => (
            <li key={item.question_id} className="flex items-start gap-2 text-sm">
              {item.is_correct ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" aria-hidden="true" />
              ) : (
                <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" aria-hidden="true" />
              )}
              <span className="min-w-0">
                <span className="text-slate-700">{item.question_text}</span>{' '}
                {!item.is_correct && (
                  <span className="text-slate-500">
                    → correct answer:{' '}
                    <strong className="font-medium text-emerald-700">{item.correct_option_text}</strong>
                  </span>
                )}
              </span>
            </li>
          ))}
        </ol>
      )}
    </li>
  )
}
