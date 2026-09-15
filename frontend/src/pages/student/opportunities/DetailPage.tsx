import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ExternalLink,
  GraduationCap,
  MapPin,
  Send,
  Sparkles,
  Wallet,
  XCircle,
} from 'lucide-react'
import {
  APPLICATION_STATUS_LABELS,
  applyToOpportunity,
  type ApplicationStatus,
  type MyApplicationSummary,
} from '../../../api/endpoints/applications'
import { getOpportunity } from '../../../api/endpoints/opportunities'
import { useApi } from '../../../hooks/useApi'
import { Alert, Badge, Button, Card, ProgressBar, Spinner } from '../../../components/ui'
import { cn } from '../../../utils/cn'
import { BreakdownRows } from './Breakdown'
import { deadlineMeta, formatDate, matchTone } from './helpers'
import { TypeBadge } from './TypeBadge'

export function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>()
  const opportunityId = Number(id)

  const { data, loading, error, refresh } = useApi(
    () => getOpportunity(opportunityId),
    [opportunityId],
  )

  // Apply state: starts from the payload (my_application), updated locally
  // on a successful apply so the hero switches to the tracking CTA instantly.
  const [localApp, setLocalApp] = useState<MyApplicationSummary | null>(null)
  const [applying, setApplying] = useState(false)
  const [applyError, setApplyError] = useState<string | null>(null)
  const currentApp = data?.my_application ?? localApp

  const handleApply = async () => {
    setApplying(true)
    setApplyError(null)
    try {
      const record = await applyToOpportunity(opportunityId)
      setLocalApp({ id: record.id, status: record.status, applied_at: record.applied_at })
      refresh()
    } catch (e) {
      const message = e as { detail?: string; message?: string }
      setApplyError(message?.detail ?? message?.message ?? 'Could not apply right now.')
    } finally {
      setApplying(false)
    }
  }

  const statusLabel = (s: string) =>
    APPLICATION_STATUS_LABELS[s as ApplicationStatus] ?? s

  if (loading) return <Spinner label="Loading opportunity…" />
  if (error || !data) {
    return (
      <Alert tone="error">
        {error ?? 'This opportunity is no longer open.'}
        <div className="mt-2">
          <Link to="/student/opportunities" className="font-medium underline">
            Back to opportunities
          </Link>
        </div>
      </Alert>
    )
  }

  const deadline = deadlineMeta(data.deadline)
  const match = data.match_percentage
  const missingSkills = data.requirements
    .filter((r) => !r.met && r.min_level > 0)
    .map((r) => r.skill.name)
  const metSkills = data.requirements.filter((r) => r.met).map((r) => r.skill.name)

  return (
    <div className="space-y-6">
      <Link
        to="/student/opportunities"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-800 hover:underline"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        All opportunities
      </Link>

      {/* Hero */}
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <TypeBadge type={data.opportunity_type} />
              {data.is_remote && <Badge tone="green">Remote friendly</Badge>}
              {deadline.tone !== 'slate' && data.deadline && (
                <Badge tone={deadline.tone}>{deadline.label}</Badge>
              )}
            </div>
            <h2 className="mt-2 text-2xl font-semibold text-slate-900">{data.title}</h2>
            <p className="text-sm font-medium text-slate-500">{data.company}</p>
          </div>
          <div className="flex shrink-0 flex-col items-stretch gap-2.5 sm:w-72 sm:items-end">
            {currentApp ? (
              <div className="flex flex-col items-start gap-2 sm:items-end">
                <Badge tone="green" className="gap-1.5 px-3 py-1 text-sm">
                  <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                  Applied · {statusLabel(currentApp.status)}
                </Badge>
                <Link
                  to="/student/applications"
                  className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-brand-700 px-5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-brand-800"
                >
                  Track application
                </Link>
                <p className="text-xs text-slate-400">
                  Live status updates appear on My Applications.
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-start gap-2 sm:items-end">
                <Button size="lg" onClick={handleApply} loading={applying}>
                  <Send className="h-4 w-4" aria-hidden="true" />
                  Apply now
                </Button>
                <p className="text-xs text-slate-400">
                  We&apos;ll track this application and its status for you.
                </p>
              </div>
            )}

            {applyError && <Alert tone="error">{applyError}</Alert>}

            {data.application_link && (
              <a
                href={data.application_link}
                target="_blank"
                rel="noreferrer noopener"
                className="inline-flex items-center justify-center gap-1.5 self-start rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 sm:self-auto"
              >
                <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
                Visit the company portal
              </a>
            )}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 border-t border-slate-100 pt-4 text-sm text-slate-600">
          {data.location && (
            <span className="inline-flex items-center gap-1.5">
              <MapPin className="h-4 w-4 text-slate-400" aria-hidden="true" />
              {data.location}
            </span>
          )}
          {data.deadline && (
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays className="h-4 w-4 text-slate-400" aria-hidden="true" />
              Deadline {formatDate(data.deadline)}
            </span>
          )}
          {data.compensation && (
            <span className="inline-flex items-center gap-1.5">
              <Wallet className="h-4 w-4 text-slate-400" aria-hidden="true" />
              {data.compensation}
            </span>
          )}
          {!data.deadline && (
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays className="h-4 w-4 text-slate-400" aria-hidden="true" />
              Open-ended application
            </span>
          )}
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left column */}
        <div className="space-y-6 lg:col-span-2">
          <Card title="About the role">
            <p className="whitespace-pre-line text-sm leading-relaxed text-slate-700">
              {data.description || 'No description provided yet.'}
            </p>
          </Card>

          {data.eligibility && (
            <Card title="Who can apply" subtitle="Eligibility criteria">
              <div className="flex items-start gap-2.5">
                <GraduationCap
                  className="mt-0.5 h-5 w-5 shrink-0 text-brand-600"
                  aria-hidden="true"
                />
                <p className="whitespace-pre-line text-sm leading-relaxed text-slate-700">
                  {data.eligibility}
                </p>
              </div>
            </Card>
          )}

          {data.requirements.length > 0 && (
            <Card
              title="Required skills"
              subtitle="Your current level vs. the posting's requirement"
            >
              <ul className="space-y-4">
                {data.requirements.map((req) => {
                  const has = req.my_level > 0
                  const shortBy = Math.max(0, req.min_level - req.my_level)
                  return (
                    <li key={req.id} className="flex items-center gap-3">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-baseline justify-between gap-2">
                          <span className="text-sm font-medium text-slate-800">
                            {req.skill.name}
                          </span>
                          <span className="text-xs text-slate-500">
                            Needs {req.min_level}%
                          </span>
                        </div>
                        <div className="mt-1.5 flex items-center gap-2">
                          <div className="flex-1">
                            <ProgressBar value={req.my_level} tone={req.met ? 'green' : 'brand'} />
                          </div>
                          <span className="w-14 shrink-0 text-right text-xs text-slate-500">
                            {has ? `${Math.round(req.my_level)}%` : 'Not added'}
                          </span>
                        </div>
                      </div>
                      {req.met ? (
                        <Badge tone="green" className="shrink-0 gap-1">
                          <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
                          Met
                        </Badge>
                      ) : (
                        <Badge tone="amber" className="shrink-0">
                          Needs {shortBy}% more
                        </Badge>
                      )}
                    </li>
                  )
                })}
              </ul>
              {missingSkills.length > 0 && (
                <p className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500">
                  Missing {missingSkills.join(', ')}? Add them to your profile and retake the{' '}
                  <Link
                    to="/student/skills"
                    className="font-medium text-brand-700 hover:underline"
                  >
                    skill assessments
                  </Link>{' '}
                  to raise your match.
                </p>
              )}
            </Card>
          )}
        </div>

        {/* Right column */}
        <div className="space-y-6">
          <Card
            title="Your skills match"
            subtitle="Based on the skills on your profile"
            className="lg:sticky lg:top-20"
          >
            {match === null ? (
              <div className="space-y-3">
                <p className="text-sm text-slate-600">
                  This opportunity doesn&apos;t list specific skills, so there&apos;s no
                  match score to compute — apply if the work interests you.
                </p>
              </div>
            ) : (
              <>
                <div className="flex items-baseline gap-3">
                  <span
                    className={cn(
                      'text-4xl font-bold',
                      match >= 60 ? 'text-emerald-600' : match >= 40 ? 'text-amber-600' : 'text-slate-700',
                    )}
                  >
                    {Math.round(match)}%
                  </span>
                  <Badge tone={matchTone(match)}>
                    {match >= 80 ? 'Strong fit' : match >= 60 ? 'Good fit' : match >= 40 ? 'Moderate' : 'Low'}
                  </Badge>
                </div>
                <ProgressBar value={match} tone={matchTone(match)} className="mt-2 h-2.5" />
                <p className="mt-2 text-xs text-slate-500">
                  {data.matched_requirements} of {data.total_requirements} required skills
                  met.
                </p>

                {data.explanation && (
                  <p className="mt-3 text-sm leading-relaxed text-slate-600">
                    {data.explanation}
                  </p>
                )}
                <div className="mt-3">
                  <BreakdownRows breakdown={data.breakdown} />
                </div>
                {data.recommended_next_steps.length > 0 && (
                  <ul className="mt-3 space-y-1.5 border-t border-slate-100 pt-3">
                    {data.recommended_next_steps.map((step) => (
                      <li key={step} className="flex items-start gap-2 text-xs text-slate-500">
                        <ArrowRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-600" aria-hidden="true" />
                        {step}
                      </li>
                    ))}
                  </ul>
                )}

                <div className="mt-4 space-y-3">
                  {metSkills.length > 0 && (
                    <div>
                      <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
                        Matching skills
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {metSkills.map((name) => (
                          <Badge key={name} tone="green" className="gap-1">
                            <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
                            {name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {missingSkills.length > 0 && (
                    <div>
                      <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
                        Missing skills
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {missingSkills.map((name) => (
                          <Badge key={name} tone="amber" className="gap-1">
                            <XCircle className="h-3 w-3" aria-hidden="true" />
                            {name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {metSkills.length === 0 && missingSkills.length === 0 && (
                    <p className="text-sm text-slate-500">
                      Add the skills above to your profile to see how you measure up.
                    </p>
                  )}
                </div>
              </>
            )}

            <div className="mt-4 flex items-start gap-2 border-t border-slate-100 pt-3 text-xs text-slate-400">
              <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
              <p>
                The match is a skills-based estimate from your profile — it never
                guarantees selection.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
