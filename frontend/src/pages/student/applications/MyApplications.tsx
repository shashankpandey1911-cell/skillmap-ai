import { useState } from 'react'
import {
  CalendarDays,
  Check,
  CheckCircle2,
  MapPin,
  Pencil,
  Send,
  StickyNote,
  X,
  XCircle,
} from 'lucide-react'
import {
  APPLICATION_STATUSES,
  APPLICATION_STATUS_LABELS,
  STATUS_STAGES,
  type ApplicationRecord,
  type ApplicationStatus,
} from '../../../api/endpoints/applications'
import { updateApplicationNotes } from '../../../api/endpoints/applications'
import { listMyApplications } from '../../../api/endpoints/applications'
import { useApi } from '../../../hooks/useApi'
import { useAuth } from '../../../auth/AuthContext'
import { Alert, Badge, Button, Card, Spinner, Textarea } from '../../../components/ui'
import { cn } from '../../../utils/cn'
import { deadlineMeta, formatDate } from '../opportunities/helpers'
import { TypeBadge } from '../opportunities/TypeBadge'

type Filter = ApplicationStatus | 'ALL'

const STATUS_TONES: Record<ApplicationStatus, 'brand' | 'green' | 'amber' | 'red' | 'slate'> = {
  APPLIED: 'slate',
  SUBMITTED: 'brand',
  UNDER_REVIEW: 'brand',
  SHORTLISTED: 'green',
  INTERVIEW: 'amber',
  SELECTED: 'green',
  REJECTED: 'red',
}

export function MyApplicationsPage() {
  const { user } = useAuth()
  const { data, loading, error, refresh } = useApi(listMyApplications)
  const [filter, setFilter] = useState<Filter>('ALL')
  const [search, setSearch] = useState('')

  const all = data ?? []
  const counts = { ALL: all.length } as Record<Filter, number>
  for (const s of APPLICATION_STATUSES) counts[s] = 0
  for (const app of all) counts[app.status] += 1

  let visible = all
  if (filter !== 'ALL') visible = visible.filter((a) => a.status === filter)
  const term = search.trim().toLowerCase()
  if (term) {
    visible = visible.filter(
      (a) =>
        a.opportunity.title.toLowerCase().includes(term) ||
        a.opportunity.company.toLowerCase().includes(term),
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">My Applications</h2>
        <p className="mt-1 text-sm text-slate-500">
          {user?.full_name ?? user?.username}, track every application as it moves
          through the pipeline — add notes and keep an eye on deadlines.
        </p>
      </div>

      {loading ? (
        <Spinner label="Loading your applications…" />
      ) : error ? (
        <Alert tone="error">{error}</Alert>
      ) : (
        <>
          <div className="flex flex-wrap items-center gap-2">
            <StatusPill
              label="All"
              count={counts.ALL}
              active={filter === 'ALL'}
              onClick={() => setFilter('ALL')}
            />
            {APPLICATION_STATUSES.map((s) => (
              <StatusPill
                key={s}
                label={APPLICATION_STATUS_LABELS[s]}
                count={counts[s]}
                active={filter === s}
                onClick={() => setFilter(filter === s ? 'ALL' : s)}
              />
            ))}
            <label className="relative ml-auto">
              <span className="sr-only">Search applications</span>
              <input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by company or role…"
                className="h-9 w-56 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-2 focus:outline-brand-500/30"
              />
            </label>
          </div>

          {visible.length === 0 ? (
            <Card>
              <div className="flex flex-col items-center gap-3 py-10 text-center">
                <StickyNote className="h-10 w-10 text-slate-300" aria-hidden="true" />
                <div>
                  <p className="font-medium text-slate-800">
                    {all.length === 0 ? 'No applications yet' : 'Nothing matches'}
                  </p>
                  <p className="mt-1 max-w-md text-sm text-slate-500">
                    {all.length === 0
                      ? 'Head to Opportunities, open a posting you like, and press Apply — every application you make will be tracked here.'
                      : 'Try a different status filter or search term.'}
                  </p>
                </div>
              </div>
            </Card>
          ) : (
            <div className="space-y-5">
              {visible.map((application) => (
                <ApplicationCard
                  key={application.id}
                  application={application}
                  onSaved={refresh}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function StatusPill({
  label,
  count,
  active,
  onClick,
}: {
  label: string
  count: number
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors',
        active
          ? 'border-brand-700 bg-brand-700 text-white'
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

function ApplicationCard({
  application,
  onSaved,
}: {
  application: ApplicationRecord
  onSaved: () => void
}) {
  const status = application.status
  const deadline = deadlineMeta(application.opportunity.deadline)
  const rejected = status === 'REJECTED'
  const selected = status === 'SELECTED'
  const reach =
    status === 'REJECTED' ? -1 : Math.max(0, STATUS_STAGES.indexOf(status))

  return (
    <Card
      className={cn(
        selected && 'border-emerald-300',
        rejected && 'border-red-200',
      )}
    >
      <div className="flex flex-col gap-5 lg:flex-row">
        {/* Left: posting info */}
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                {application.opportunity.company}
              </p>
              <h3 className="mt-0.5 text-base font-semibold text-slate-900">
                {application.opportunity.title}
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <TypeBadge type={application.opportunity.opportunity_type} />
              <Badge tone={STATUS_TONES[status]} className="gap-1">
                {selected || rejected ? (
                  <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
                ) : null}
                {APPLICATION_STATUS_LABELS[status]}
              </Badge>
            </div>
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-500">
            <span>
              Applied {formatDate(application.applied_at.slice(0, 10))}
            </span>
            {application.opportunity.location && (
              <span className="inline-flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                {application.opportunity.location}
              </span>
            )}
            <span className="inline-flex items-center gap-1">
              <CalendarDays className="h-3.5 w-3.5" aria-hidden="true" />
              {application.opportunity.deadline ? (
                <>
                  Deadline {formatDate(application.opportunity.deadline)}
                  <Badge tone={deadline.tone} className="ml-1">
                    {deadline.label}
                  </Badge>
                </>
              ) : (
                <Badge tone="slate">Open-ended</Badge>
              )}
            </span>
            {application.interview_date && (
              <Badge tone="amber" className="gap-1">
                <CalendarDays className="h-3 w-3" aria-hidden="true" />
                Interview on {formatDate(application.interview_date)}
              </Badge>
            )}
          </div>

          {rejected && (
            <p className="mt-3 inline-flex items-center gap-1.5 text-xs font-medium text-red-600">
              <XCircle className="h-3.5 w-3.5" aria-hidden="true" />
              This application was closed — you were not selected this time.
            </p>
          )}
          {selected && (
            <p className="mt-3 inline-flex items-center gap-1.5 text-xs font-medium text-emerald-700">
              <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
              Congratulations — you were selected! 🎉
            </p>
          )}

          <NotesEditor application={application} onSaved={onSaved} />
        </div>

        {/* Right: the pipeline timeline */}
        <div className="w-full shrink-0 lg:w-64">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Application timeline
          </p>
          <ol className="space-y-0">
            {STATUS_STAGES.map((stage, index) => {
              const done = index < reach
              const current = index === reach && !rejected
              return (
                <li key={stage} className="relative flex gap-2.5 pb-4 last:pb-0">
                  {index < STATUS_STAGES.length - 1 && (
                    <span
                      aria-hidden="true"
                      className={cn(
                        'absolute left-[11px] top-5 h-full w-0.5',
                        done ? 'bg-brand-500' : 'bg-slate-200',
                      )}
                    />
                  )}
                  <span
                    className={cn(
                      'z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2',
                      done && 'border-brand-600 bg-brand-600 text-white',
                      current && 'border-brand-600 bg-white text-brand-700',
                      !done && !current && 'border-slate-200 bg-white text-slate-300',
                    )}
                  >
                    {done ? (
                      <Check className="h-3.5 w-3.5" aria-hidden="true" />
                    ) : (
                      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
                    )}
                  </span>
                  <span
                    className={cn(
                      'pt-0.5 text-xs',
                      done && 'font-medium text-slate-700',
                      current && 'font-semibold text-brand-700',
                      !done && !current && 'text-slate-400',
                    )}
                  >
                    {APPLICATION_STATUS_LABELS[stage]}
                    {current && (
                      <span className="ml-1.5 rounded-full bg-brand-50 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-brand-700">
                        Current
                      </span>
                    )}
                  </span>
                </li>
              )
            })}
          </ol>
          {rejected && (
            <p className="mt-3 flex items-start gap-1.5 text-xs text-red-600">
              <XCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
              Outcome: not selected
            </p>
          )}
        </div>
      </div>
    </Card>
  )
}

function NotesEditor({
  application,
  onSaved,
}: {
  application: ApplicationRecord
  onSaved: () => void
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(application.notes)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  const startEdit = () => {
    setDraft(application.notes)
    setSaveError(null)
    setEditing(true)
  }

  const save = async () => {
    setSaving(true)
    setSaveError(null)
    try {
      await updateApplicationNotes(application.id, draft)
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
            htmlFor={`notes-${application.id}`}
            className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400"
          >
            <StickyNote className="h-3.5 w-3.5" aria-hidden="true" />
            Your notes
          </label>
          <Textarea
            id={`notes-${application.id}`}
            rows={3}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="e.g. Sent a follow-up on Monday; recruiter said the team is reviewing…"
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
            {application.notes ? (
              <p className="whitespace-pre-line text-slate-600">{application.notes}</p>
            ) : (
              <span className="italic text-slate-400">No notes yet.</span>
            )}
          </div>
          <Button size="sm" variant="outline" onClick={startEdit}>
            <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
            {application.notes ? 'Edit' : 'Add note'}
          </Button>
        </div>
      )}
    </div>
  )
}
