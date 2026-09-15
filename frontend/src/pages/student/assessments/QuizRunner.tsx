import { useEffect, useState, type ReactNode } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  ChevronLeft,
  Lightbulb,
  RotateCcw,
  Trophy,
  XCircle,
} from 'lucide-react'
import {
  type AssessmentInfo,
  type AssessmentQuestion,
  type AssessmentResultRecord,
  startAssessment,
  submitAssessment,
} from '../../../api/endpoints/assessments'
import { Alert, Badge, Button, Card, ProgressBar, Spinner } from '../../../components/ui'
import { useAuth } from '../../../auth/AuthContext'
import { extractApiError } from '../../../utils/errors'
import { cn } from '../../../utils/cn'

type Phase = 'loading' | 'quiz' | 'submitting' | 'result'

export function QuizRunner({
  assessment,
  onExit,
}: {
  assessment: AssessmentInfo
  onExit: () => void
}) {
  const { user } = useAuth()
  const [phase, setPhase] = useState<Phase>('loading')
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([])
  const [attemptId, setAttemptId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [index, setIndex] = useState(0)
  const [choices, setChoices] = useState<Record<number, number>>({})
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [result, setResult] = useState<AssessmentResultRecord | null>(null)

  useEffect(() => {
    let alive = true
    startAssessment(assessment.id)
      .then((started) => {
        if (!alive) return
        setQuestions(started.questions)
        setAttemptId(started.attempt.id)
        setPhase('quiz')
      })
      .catch((err) => {
        if (alive) setError(extractApiError(err, 'Could not start the assessment.'))
      })
    return () => {
      alive = false
    }
  }, [assessment.id])

  const total = questions.length
  const current = questions[index]
  const answeredCount = Object.keys(choices).length
  const unanswered = questions
    .filter((q) => choices[q.id] === undefined)
    .map((q) => q.order + 1)

  const select = (questionId: number, optionId: number) =>
    setChoices((prev) => ({ ...prev, [questionId]: optionId }))

  const handleSubmit = async () => {
    if (attemptId === null || total === 0) return
    if (unanswered.length > 0) {
      const preview = unanswered.slice(0, 4).join(', ')
      setSubmitError(
        `Answer all ${total} questions before submitting (${
          unanswered.length
        } remaining: ${preview}${unanswered.length > 4 ? '…' : ''}).`,
      )
      return
    }
    setSubmitError(null)
    setPhase('submitting')
    try {
      const answers = questions.map((q) => ({
        question_id: q.id,
        option_id: choices[q.id],
      }))
      const record = await submitAssessment(assessment.id, attemptId, answers)
      setResult(record)
      setPhase('result')
    } catch (err) {
      setPhase('quiz')
      setSubmitError(extractApiError(err, 'Could not submit the assessment.'))
    }
  }

  const retake = () => {
    setResult(null)
    setChoices({})
    setIndex(0)
    setSubmitError(null)
    setPhase('loading')
    startAssessment(assessment.id)
      .then((started) => {
        setQuestions(started.questions)
        setAttemptId(started.attempt.id)
        setPhase('quiz')
      })
      .catch((err) => setError(extractApiError(err, 'Could not start the assessment.')))
  }

  if (error) {
    return (
      <Card>
        <Alert tone="error" className="mb-4">
          {error}
        </Alert>
        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onExit}>
            Back to assessments
          </Button>
          <Button onClick={() => window.location.reload()}>Try again</Button>
        </div>
      </Card>
    )
  }

  if (phase === 'loading' || (phase === 'quiz' && !current)) {
    return (
      <Card className="flex flex-col items-center gap-3 py-10">
        <Spinner label="Preparing your assessment…" />
        <p className="text-sm text-slate-500">{assessment.title}</p>
      </Card>
    )
  }

  if (phase === 'result' && result) {
    return (
      <ResultView
        result={result}
        studentName={user?.full_name ?? user?.username ?? ''}
        onRetake={retake}
        onExit={onExit}
      />
    )
  }

  return (
    <Card className="px-6 py-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onExit}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50"
            aria-label="Quit assessment"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <div>
            <h3 className="text-base font-semibold text-slate-900">{assessment.title}</h3>
            <p className="text-xs text-slate-500">
              Question {index + 1} of {total} · {answeredCount}/{total} answered
            </p>
          </div>
        </div>
        <Badge tone={assessment.skill.category === 'Programming' ? 'brand' : 'slate'}>
          {assessment.skill.name}
        </Badge>
      </div>

      <div className="mt-4">
        <ProgressBar value={(answeredCount / total) * 100} tone="brand" />
      </div>

      {submitError && (
        <Alert tone="error" className="mt-4">
          {submitError}
        </Alert>
      )}

      {/* Question */}
      <div key={current.id} className="mt-6">
        <p className="text-lg font-medium text-slate-900">{current.text}</p>
        <div className="mt-4 space-y-2">
          {current.options.map((option) => {
            const selected = choices[current.id] === option.id
            return (
              <button
                key={option.id}
                type="button"
                onClick={() => select(current.id, option.id)}
                className={cn(
                  'flex w-full items-center gap-3 rounded-lg border px-4 py-3 text-left text-sm transition-colors',
                  selected
                    ? 'border-brand-600 bg-brand-50 ring-1 ring-brand-600'
                    : 'border-slate-200 bg-white hover:border-brand-300 hover:bg-brand-50/40',
                )}
                aria-pressed={selected}
              >
                <span
                  className={cn(
                    'flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[10px] font-bold',
                    selected
                      ? 'border-brand-600 bg-brand-600 text-white'
                      : 'border-slate-300 text-slate-400',
                  )}
                >
                  {selected ? '✓' : String.fromCharCode(65 + option.order)}
                </span>
                <span className={selected ? 'font-medium text-brand-900' : 'text-slate-700'}>
                  {option.text}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
        <Button variant="ghost" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index === 0}>
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Previous
        </Button>
        {index < total - 1 ? (
          <Button onClick={() => setIndex((i) => Math.min(total - 1, i + 1))} disabled={choices[current.id] === undefined}>
            Next
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} loading={phase === 'submitting'}>
            Submit assessment
          </Button>
        )}
      </div>
    </Card>
  )
}

function ResultView({
  result,
  studentName,
  onRetake,
  onExit,
}: {
  result: AssessmentResultRecord
  studentName: string
  onRetake: () => void
  onExit: () => void
}) {
  const { score, correct_count, total_questions, review, improvement_suggestions } = result
  const pass = score >= 70
  const tone = score >= 85 ? 'green' : score >= 60 ? 'brand' : score >= 40 ? 'amber' : 'red'

  return (
    <div className="space-y-6">
      <Card
        className="overflow-hidden"
        title={
          <span className="flex items-center gap-2">
            <Trophy
              className={cn('h-4 w-4', score >= 70 ? 'text-amber-500' : 'text-slate-400')}
              aria-hidden="true"
            />
            {score >= 70 ? 'Assessment passed!' : 'Assessment complete'}
          </span>
        }
        subtitle={`${studentName} · ${result.assessment.skill.name}`}
      >
        <div className="flex flex-col items-center gap-6 py-2 sm:flex-row sm:justify-center">
          <div className="text-center">
            <p className="text-5xl font-bold tracking-tight text-slate-900">
              {Math.round(score)}
              <span className="text-2xl text-slate-400">%</span>
            </p>
            <p className="mt-2 text-sm text-slate-500">
              {correct_count} correct · {total_questions} questions
            </p>
            <div className="mt-3 flex justify-center">
              <Badge tone={pass ? 'green' : 'amber'}>
                {pass ? `Great — ${score >= 85 ? 'expert level' : 'keep it up'}` : 'Room to grow'}
              </Badge>
            </div>
          </div>
          <ProgressBar value={score} tone={tone} className="h-3 w-full max-w-xs" />
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <MiniStat label="Your score" value={`${Math.round(score)}%`} />
          <MiniStat label="Correct" value={`${correct_count}/${total_questions}`} />
          <MiniStat label="Answered" value="100%" />
        </div>
      </Card>

      {improvement_suggestions.length > 0 && (
        <Card title="Improvement suggestions" subtitle="Based on your answers">
          <ul className="space-y-2">
            {improvement_suggestions.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" aria-hidden="true" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Card
        title="Answer review"
        subtitle="See what you got right and what to revise"
      >
        <ol className="space-y-3">
          {review.map((item) => (
            <li
              key={item.question_id}
              className={cn(
                'rounded-lg border px-4 py-3',
                item.is_correct ? 'border-emerald-100 bg-emerald-50/40' : 'border-red-100 bg-red-50/40',
              )}
            >
              <div className="flex items-start gap-2">
                {item.is_correct ? (
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" aria-hidden="true" />
                ) : (
                  <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" aria-hidden="true" />
                )}
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-800">{item.question_text}</p>
                  <div className="mt-1 space-y-0.5 text-xs">
                    {item.is_correct ? (
                      <p className="text-emerald-700">
                        Your answer: <strong>{item.selected_option_text}</strong> ✓
                      </p>
                    ) : (
                      <>
                        <p className="text-red-600">
                          Your answer: {item.selected_option_text ?? '(none)'}
                        </p>
                        <p className="text-emerald-700">
                          Correct answer: <strong>{item.correct_option_text}</strong>
                        </p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </Card>

      <div className="flex flex-wrap justify-end gap-3">
        <Button variant="outline" onClick={onExit}>
          Back to assessments
        </Button>
        <Button onClick={onRetake}>
          <RotateCcw className="h-4 w-4" aria-hidden="true" />
          Retake assessment
        </Button>
      </div>
    </div>
  )
}

function MiniStat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg bg-slate-50 px-4 py-3 text-center">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-900">{value}</p>
    </div>
  )
}
