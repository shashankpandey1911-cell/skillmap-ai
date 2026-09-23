import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowRight,
  Award,
  BookOpen,
  CalendarDays,
  Check,
  CheckCircle2,
  ExternalLink,
  Lightbulb,
  MapPin,
  Pencil,
  Send,
  Sparkles,
  StickyNote,
  ThumbsDown,
  ThumbsUp,
  X,
  XCircle,
} from 'lucide-react'
import {
  FEEDBACK_KIND_LABELS,
  FEEDBACK_STATUS_LABELS,
  type ApplicationFeedback,
  type FeedbackGap,
  type FeedbackKind,
  type FeedbackStatus,
  acceptFeedback,
  dismissFeedback,
  listFeedback,
  updateFeedbackNotes,
} from '../../api/endpoints/feedback'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../auth/AuthContext'
import {
  Alert,
  Badge,
  type BadgeTone,
  Button,
  Card,
  ProgressBar,
  Spinner,
  Textarea,
} from '../../components/ui'
import { cn } from '../../utils/cn'
import { formatDate } from './opportunities/helpers'
import { TypeBadge } from './opportunities/TypeBadge'

type KindFilter = FeedbackKind | 'ALL'
type StatusFilter = FeedbackStatus | 'ALL'

const GAP_TONE: Record<string, BadgeTone> = {
  HIGH: 'red',
  MEDIUM: 'amber',
  LOW: 'brand',
}

const STATUS_TONE: Record<FeedbackStatus, BadgeTone> = {
  PENDING: 'amber',
  ACCEPTED: 'green',
  DISMISSED: 'slate',
}

export function CareerImprovementPage() {
  const { user } = useAuth()
  const { data, loading, error, refresh } = useApi(listFeedback)
  const [kindFilter, setKindFilter] = useState<KindFilter>('ALL')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL')

  const all = data ?? []
  const kindCounts: Record<KindFilter, number> = {
    ALL: all.length,
    REJECTED: 0,
    SELECTED: 0,
  }
  const statusCounts: Record<StatusFilter, number> = {
    ALL: all.length,
    PENDING: 0,
    ACCEPTED: 0,
    DISMISSED: 0,
  }
  for (const fb of all) {
    kindCounts[fb.kind] += 1
    statusCounts[fb.status] += 1
  }

  let visible = all
  if (kindFilter !== 'ALL') visible = visible.filter((fb) => fb.kind === kindFilter)
  if (statusFilter !== 'ALL') visible = visible.filter((fb) => fb.status === statusFilter)

  const rejected = visible.filter((fb) => fb.kind === 'REJECTED')
  const selected = visible.filter((fb) => fb.kind === 'SELECTED')

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Career Improvement</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-500">
          {user?.full_name ?? user?.username}, every application decision teaches you
          something. Rejections are turned into concrete skill gaps and learning
          recommendations — accept them to add the work to your roadmap. Selections are
          recorded as achievements. Nothing is changed on your profile without your say-so.
        </p>
      </div>

      {loading ? (
        <Spinner label="Loading your career feedback…" />
      ) : error ? (
        <Alert tone="error">{error}</Alert>
      ) : all.length === 0 ? (
        <Card>
          <div className="flex flex-col items-center gap-3 py-10 text-center">
            <Award className="h-10 w-10 text-slate-300" aria-hidden="true" />
            <div>
              <p className="font-medium text-slate-800">No decisions to show yet</p>
              <p className="mt-1 max-w-md text-sm text-slate-500">
                Once an application reaches a decision — selected or rejected — the outcome
                and any skill gaps will appear here.
              </p>
            </div>
          </div>
        </Card>
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-2">
            <FilterPill
              label="All"
              count={kindCounts.ALL}
              active={kindFilter === 'ALL'}
              onClick={() => setKindFilter('ALL')}
            />
            <FilterPill
              label={FEEDBACK_KIND_LABELS.REJECTED}
              count={kindCounts.REJECTED}
              active={kindFilter === 'REJECTED'}
              onClick={() => setKindFilter(kindFilter === 'REJECTED' ? 'ALL' : 'REJECTED')}
            />
            <FilterPill
              label="Achievements"
              count={kindCounts.SELECTED}
              active={kindFilter === 'SELECTED'}
              onClick={() => setKindFilter(kindFilter === 'SELECTED' ? 'ALL' : 'SELECTED')}
            />
            {kindFilter !== 'SELECTED' && (
              <div className="ml-auto flex flex-wrap items-center gap-2">
                <FilterPill
                  label="Pending"
                  count={statusCounts.PENDING}
                  active={statusFilter === 'PENDING'}
                  onClick={() => setStatusFilter(statusFilter === 'PENDING' ? 'ALL' : 'PENDING')}
                  tone="amber"
                />
                <FilterPill
                  label="Accepted"
                  count={statusCounts.ACCEPTED}
                  active={statusFilter === 'ACCEPTED'}
                  onClick={() => setStatusFilter(statusFilter === 'ACCEPTED' ? 'ALL' : 'ACCEPTED')}
                  tone="green"
                />
                <FilterPill
                  label="Dismissed"
                  count={statusCounts.DISMISSED}
                  active={statusFilter === 'DISMISSED'}
                  onClick={() => setStatusFilter(statusFilter === 'DISMISSED' ? 'ALL' : 'DISMISSED')}
                />
              </div>
            )}
          </div>

          {visible.length === 0 ? (
            <Card>
              <div className="flex flex-col items-center gap-3 py-10 text-center">
                <AlertTriangle className="h-10 w-10 text-slate-300" aria-hidden="true" />
                <p className="font-medium text-slate-800">Nothing matches those filters</p>
                <p className="text-sm text-slate-500">Try a different combination.</p>
              </div>
            </Card>
          ) : (
            <div className="space-y-5">
              {rejected.map((fb) => (
                <RejectionCard key={fb.id} feedback={fb} onChanged={refresh} />
              ))}
              {selected.map((fb) => (
                <AchievementCard key={fb.id} feedback={fb} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function FilterPill({
  label,
  count,
  active,
  onClick,
  tone = 'slate',
}: {
  label: string
  count: number
  active: boolean
  onClick: () => void
  tone?: BadgeTone
}) {
  const activeTone: Record<BadgeTone, string> = {
    brand: 'border-brand-700 bg-brand-700 text-white',
    green: 'border-emerald-700 bg-emerald-700 text-white',
    amber: 'border-amber-600 bg-amber-600 text-white',
    red: 'border-red-700 bg-red-700 text-white',
    slate: 'border-slate-700 bg-slate-700 text-white',
    purple: 'border-purple-700 bg-purple-700 text-white',
  }
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors',
        active
          ? activeTone[tone]
          : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50',
      )}
    >
      {label}
      <span
        className={cn(
          'rounded-full px-1.5 text-[11px] font-semibold',
          active ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500',
        )}
      >
        {count}
      </span>
    </button>
  )
}

function RejectionCard({
  feedback,
  onChanged,
}: {
  feedback: ApplicationFeedback
  onChanged: () => void
}) {
  const opportunity = feedback.opportunity
  const pending = feedback.status === 'PENDING'
  const [busy, setBusy] = useState<'accept' | 'dismiss' | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const act = async (fn: (id: number) => Promise<ApplicationFeedback>, kind: 'accept' | 'dismiss') => {
    setBusy(kind)
    setActionError(null)
    try {
      await fn(feedback.id)
      onChanged()
    } catch (e) {
      const message =
        (e as { detail?: string; message?: string })?.detail ??
        (e as { message?: string })?.message ??
        'Could not update this feedback.'
      setActionError(message)
    } finally {
      setBusy(null)
    }
  }

  return (
    <Card className="border-red-200">
      <div className="flex flex-col gap-5 lg:flex-row">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                {opportunity.company}
              </p>
              <h3 className="mt-0.5 flex flex-wrap items-center gap-2 text-base font-semibold text-slate-900">
                {opportunity.title}
                <TypeBadge type={opportunity.opportunity_type} />
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <Badge tone="red" className="gap-1">
                <XCircle className="h-3 w-3" aria-hidden="true" />
                {FEEDBACK_KIND_LABELS[feedback.kind]}
              </Badge>
              <Badge tone={STATUS_TONE[feedback.status]}>
                {FEEDBACK_STATUS_LABELS[feedback.status]}
              </Badge>
            </div>
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-500">
            <span>Decided {formatDate(feedback.updated_at.slice(0, 10))}</span>
            {opportunity.location && (
              <span className="inline-flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                {opportunity.location}
              </span>
            )}
            <span className="inline-flex items-center gap-1">
              <CalendarDays className="h-3.5 w-3.5" aria-hidden="true" />
              Deadline {formatDate(opportunity.deadline ?? '')}
            </span>
          </div>

          <p className="mt-3 text-sm text-slate-700">{feedback.summary}</p>

          {feedback.gaps.length > 0 && (
            <div className="mt-4 space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Main skill gaps
              </p>
              {feedback.gaps.map((gap) => (
                <GapRow key={gap.id} gap={gap} />
              ))}
            </div>
          )}

          {feedback.status === 'ACCEPTED' && (
            <Link
              to="/student/learning"
              className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-800"
            >
              <Sparkles className="h-4 w-4" aria-hidden="true" />
              These skills are on your learning roadmap — open it to track progress
              <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
            </Link>
          )}

          <NotesEditor feedback={feedback} onSaved={onChanged} />
        </div>

        <div className="w-full shrink-0 lg:w-72">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Recommended next steps
            </p>
            <ul className="mt-3 space-y-3">
              {feedback.gaps.length === 0 ? (
                <li className="text-sm text-slate-600">
                  Keep building projects and applying — your profile already meets this
                  posting's listed skills.
                </li>
              ) : (
                feedback.gaps.slice(0, 3).map((gap) => (
                  <li key={gap.id} className="text-sm">
                    <p className="font-medium text-slate-800">{gap.skill_name}</p>
                    {gap.recommendations.slice(0, 2).map((rec, i) => (
                      <p key={i} className="mt-1 flex items-start gap-1.5 text-xs text-slate-600">
                        <BookOpen className="mt-0.5 h-3 w-3 shrink-0 text-brand-600" aria-hidden="true" />
                        {rec.url ? (
                          <a
                            href={rec.url}
                            target="_blank"
                            rel="noreferrer noopener"
                            className="inline-flex items-center gap-1 font-medium text-brand-700 hover:text-brand-800"
                          >
                            {rec.title}
                            <ExternalLink className="h-3 w-3" aria-hidden="true" />
                          </a>
                        ) : (
                          <span>{rec.title}</span>
                        )}
                      </p>
                    ))}
                  </li>
                ))
              )}
            </ul>

            {pending && (
              <div className="mt-4 flex flex-col gap-2 border-t border-slate-200 pt-3">
                {actionError && <p className="text-xs text-red-600">{actionError}</p>}
                <Button
                  size="sm"
                  loading={busy === 'accept'}
                  onClick={() => act((id) => acceptFeedback(id), 'accept')}
                >
                  <ThumbsUp className="h-3.5 w-3.5" aria-hidden="true" />
                  Accept — add to my roadmap
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  loading={busy === 'dismiss'}
                  onClick={() => act((id) => dismissFeedback(id), 'dismiss')}
                >
                  <ThumbsDown className="h-3.5 w-3.5" aria-hidden="true" />
                  Dismiss
                </Button>
                <p className="text-[11px] text-slate-400">
                  Accepting only adds these skills to your learning roadmap — your profile
                  and skill scores are never changed automatically.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}

function GapRow({ gap }: { gap: FeedbackGap }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-900">{gap.skill_name}</span>
          <Badge tone={GAP_TONE[gap.gap_class] ?? 'slate'}>
            {gap.gap_class} · {Math.round(gap.gap_percentage)}% gap
          </Badge>
        </div>
        <span className="text-xs text-slate-500">
          You: {Math.round(gap.current_level)}% · Required: {gap.required_level}%
        </span>
      </div>
      <ProgressBar
        value={Math.min(100, (gap.current_level / Math.max(1, gap.required_level)) * 100)}
        className="mt-2 h-1.5"
        tone="amber"
      />
      <p className="mt-2 flex items-start gap-1.5 text-xs text-slate-600">
        <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-600" aria-hidden="true" />
        {gap.recommended_action}
      </p>
      {gap.recommendations.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-2">
          {gap.recommendations.map((rec, i) => (
            <li key={i}>
              {rec.url ? (
                <a
                  href={rec.url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="inline-flex items-center gap-1 rounded-full border border-brand-200 bg-brand-50 px-2.5 py-1 text-[11px] font-medium text-brand-800 hover:bg-brand-100"
                >
                  {rec.title}
                  <ExternalLink className="h-3 w-3" aria-hidden="true" />
                </a>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-slate-700">
                  {rec.title}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function AchievementCard({ feedback }: { feedback: ApplicationFeedback }) {
  const opportunity = feedback.opportunity
  return (
    <Card className="border-emerald-300">
      <div className="flex items-start gap-4">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
          <Award className="h-6 w-6" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="green" className="gap-1">
              <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
              {FEEDBACK_KIND_LABELS[feedback.kind]}
            </Badge>
            <Badge tone="slate">{formatDate(feedback.created_at.slice(0, 10))}</Badge>
          </div>
          <h3 className="mt-2 text-base font-semibold text-slate-900">
            {opportunity.title}
            <span className="font-normal text-slate-500"> · {opportunity.company}</span>
          </h3>
          <p className="mt-1 text-sm text-slate-700">{feedback.summary}</p>
          {opportunity.compensation && (
            <p className="mt-2 inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700">
              <Check className="h-3.5 w-3.5" aria-hidden="true" />
              {opportunity.compensation}
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}

function NotesEditor({
  feedback,
  onSaved,
}: {
  feedback: ApplicationFeedback
  onSaved: () => void
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(feedback.notes)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  const startEdit = () => {
    setDraft(feedback.notes)
    setSaveError(null)
    setEditing(true)
  }

  const save = async () => {
    setSaving(true)
    setSaveError(null)
    try {
      await updateFeedbackNotes(feedback.id, draft)
      setEditing(false)
      onSaved()
    } catch (e) {
      const message = (e as { detail?: string; message?: string })
      setSaveError(message?.detail ?? message?.message ?? 'Could not save your note.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mt-4 border-t border-slate-100 pt-3">
      {editing ? (
        <div className="space-y-2">
          <label
            htmlFor={`fb-notes-${feedback.id}`}
            className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400"
          >
            <StickyNote className="h-3.5 w-3.5" aria-hidden="true" />
            Your notes
          </label>
          <Textarea
            id={`fb-notes-${feedback.id}`}
            rows={3}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="e.g. Focus on DSA for 3 weeks, then retry this posting next semester…"
          />
          {saveError && <p className="text-xs text-red-600">{saveError}</p>}
          <div className="flex items-center gap-2">
            <Button size="sm" onClick={save} loading={saving}>
              <Send className="h-3.5 w-3.5" aria-hidden="true" />
              Save note
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
              <X className="h-3.5 w-3.5" aria-hidden="true" />
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-2 text-sm text-slate-600">
            <StickyNote className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" aria-hidden="true" />
            {feedback.notes ? (
              <p className="whitespace-pre-line text-slate-600">{feedback.notes}</p>
            ) : (
              <span className="italic text-slate-400">No notes yet.</span>
            )}
          </div>
          <Button size="sm" variant="outline" onClick={startEdit}>
            <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
            {feedback.notes ? 'Edit' : 'Add note'}
          </Button>
        </div>
      )}
    </div>
  )
}
