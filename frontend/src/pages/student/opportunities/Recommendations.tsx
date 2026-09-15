import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowRight,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  MapPin,
  Sparkles,
  Wallet,
} from 'lucide-react'
import {
  getOpportunityRecommendations,
  type OpportunitySummary,
} from '../../../api/endpoints/opportunities'
import { useApi } from '../../../hooks/useApi'
import { Alert, Badge, Card, ProgressBar, Spinner } from '../../../components/ui'
import { cn } from '../../../utils/cn'
import { BreakdownRows } from './Breakdown'
import { deadlineMeta, formatDate, matchTone } from './helpers'
import { TypeBadge } from './TypeBadge'

/** Match quality bar for the "Recommended for you" rail. */
const RECOMMENDED_MIN = 60
/** A posting counts as "closing soon" within this many days. */
const CLOSING_SOON_DAYS = 14

type RailKey = 'recommended' | 'highest' | 'closing' | 'recent'

const RAILS: { key: RailKey; label: string }[] = [
  { key: 'recommended', label: 'Recommended for you' },
  { key: 'highest', label: 'Highest match' },
  { key: 'closing', label: 'Closing soon' },
  { key: 'recent', label: 'Recently added' },
]

function daysUntil(deadline: string): number {
  return Math.ceil(
    (new Date(`${deadline}T00:00:00`).getTime() - Date.now()) / (24 * 60 * 60 * 1000),
  )
}

export function OpportunityMatchesPage() {
  const { data, loading, error } = useApi(getOpportunityRecommendations)
  const [rail, setRail] = useState<RailKey>('recommended')

  const items = useMemo(() => {
    const all = data?.items ?? []
    const recommended = all
      .filter((o) => o.match_percentage !== null && o.match_percentage >= RECOMMENDED_MIN)
      .sort((a, b) => (b.match_percentage ?? 0) - (a.match_percentage ?? 0))
    const highest = [...all].sort(
      (a, b) => (b.match_percentage ?? 0) - (a.match_percentage ?? 0),
    )
    const closing = all
      .filter((o) => o.deadline && daysUntil(o.deadline) <= CLOSING_SOON_DAYS)
      .sort((a, b) => (a.deadline ?? '').localeCompare(b.deadline ?? ''))
    const recent = [...all].sort((a, b) => b.created_at.localeCompare(a.created_at))
    return { recommended, highest, closing, recent }
  }, [data])

  const visible: OpportunitySummary[] = items[rail]
  const count = visible.length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Opportunity Matches</h2>
        <p className="mt-1 text-sm text-slate-500">
          Open roles ranked from your skills, assessment scores, background and
          projects — with the reasoning behind every score.
        </p>
      </div>

      {loading ? (
        <Spinner label="Ranking opportunities for you…" />
      ) : error ? (
        <Alert tone="error">{error}</Alert>
      ) : (
        <>
          <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="Match rails">
            {RAILS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                role="tab"
                aria-selected={rail === key}
                onClick={() => setRail(key)}
                className={cn(
                  'inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors',
                  rail === key
                    ? 'border-brand-700 bg-brand-700 text-white'
                    : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50',
                )}
              >
                {label}
                <span
                  className={cn(
                    'rounded-full px-1.5 py-0.5 text-xs font-semibold',
                    rail === key ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500',
                  )}
                >
                  {items[key].length}
                </span>
              </button>
            ))}
          </div>

          {count === 0 ? (
            <Card>
              <div className="flex flex-col items-center gap-3 py-10 text-center">
                <Sparkles className="h-10 w-10 text-slate-300" aria-hidden="true" />
                <div>
                  <p className="font-medium text-slate-800">Nothing in this rail yet</p>
                  <p className="mt-1 max-w-md text-sm text-slate-500">
                    {rail === 'recommended'
                      ? 'No postings pass your 60% fit bar yet. Add missing skills, take their assessments, and update your interests to surface better matches — or check Highest match.'
                      : rail === 'closing'
                        ? 'No open postings close in the next two weeks right now.'
                        : 'There are no open postings right now.'}
                  </p>
                </div>
              </div>
            </Card>
          ) : (
            <>
              <p className="text-sm text-slate-500">
                Showing {count} {count === 1 ? 'posting' : 'postings'} — sorted by match
                score.
              </p>
              <div className="space-y-4">
                {visible.map((opportunity, index) => (
                  <MatchCard
                    key={opportunity.id}
                    opportunity={opportunity}
                    topPick={rail === 'recommended' && index === 0}
                  />
                ))}
              </div>
            </>
          )}

          {data && (
            <Alert tone="info" className="max-w-3xl">
              {data.disclaimer}
            </Alert>
          )}
        </>
      )}
    </div>
  )
}

function MatchCard({
  opportunity,
  topPick,
}: {
  opportunity: OpportunitySummary
  topPick?: boolean
}) {
  const match = opportunity.match_percentage
  const breakdown = opportunity.breakdown
  const deadline = deadlineMeta(opportunity.deadline)

  return (
    <Card className={cn(topPick && 'border-brand-300 ring-1 ring-brand-200')}>
      {topPick && (
        <div className="-mx-5 -mt-4 mb-3 flex items-center gap-1.5 border-b border-brand-100 bg-brand-50 px-5 py-1.5 text-xs font-semibold text-brand-800">
          <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
          Best match for your profile right now
        </div>
      )}
      <div className="flex flex-col gap-4 lg:flex-row">
        {/* Left: posting + why it matches */}
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                {opportunity.company}
              </p>
              <Link
                to={`/student/opportunities/${opportunity.id}`}
                className="mt-0.5 block text-base font-semibold text-slate-900 hover:text-brand-700 hover:underline"
              >
                {opportunity.title}
              </Link>
            </div>
            <TypeBadge type={opportunity.opportunity_type} />
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-slate-500">
            {opportunity.location && (
              <span className="inline-flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                {opportunity.location}
              </span>
            )}
            {opportunity.is_remote && <Badge tone="green">Remote friendly</Badge>}
            <span className="inline-flex items-center gap-1">
              <CalendarDays className="h-3.5 w-3.5" aria-hidden="true" />
              {opportunity.deadline ? (
                <>
                  {formatDate(opportunity.deadline)}
                  <Badge tone={deadline.tone} className="ml-1">
                    {deadline.label}
                  </Badge>
                </>
              ) : (
                <Badge tone="slate">Open-ended</Badge>
              )}
            </span>
            {opportunity.compensation && (
              <span className="inline-flex items-center gap-1">
                <Wallet className="h-3.5 w-3.5" aria-hidden="true" />
                {opportunity.compensation}
              </span>
            )}
          </div>

          {opportunity.explanation && (
            <p className="mt-3 text-sm leading-relaxed text-slate-600">
              {opportunity.explanation}
            </p>
          )}

          <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2">
            {opportunity.matching_skills.length > 0 && (
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Matching skills
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {opportunity.matching_skills.map((name) => (
                    <Badge key={name} tone="green" className="gap-1">
                      <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
                      {name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {opportunity.missing_skills.length > 0 && (
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Skill gaps
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {opportunity.missing_skills.map((name) => (
                    <Badge key={name} tone="amber" className="gap-1">
                      <AlertTriangle className="h-3 w-3" aria-hidden="true" />
                      {name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {opportunity.recommended_next_steps.length > 0 && (
            <ul className="mt-3 space-y-1.5">
              {opportunity.recommended_next_steps.map((step) => (
                <li key={step} className="flex items-start gap-2 text-xs text-slate-500">
                  <ArrowRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-600" aria-hidden="true" />
                  {step}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Right: score + signal breakdown */}
        <div className="w-full shrink-0 lg:w-64">
          <div className="flex items-baseline gap-2">
            <span
              className={cn(
                'text-3xl font-bold',
                match === null
                  ? 'text-slate-500'
                  : match >= 60
                    ? 'text-emerald-600'
                    : match >= 40
                      ? 'text-amber-600'
                      : 'text-slate-700',
              )}
            >
              {match === null ? '—' : `${Math.round(match)}%`}
            </span>
            <Badge tone={matchTone(match)}>
              {match === null
                ? 'No skills listed'
                : match >= 80
                  ? 'Strong'
                  : match >= 60
                    ? 'Good fit'
                    : match >= 40
                      ? 'Moderate'
                      : 'Low'}
            </Badge>
          </div>
          <ProgressBar
            value={match ?? 0}
            tone={matchTone(match)}
            className="mt-2"
          />

          {breakdown && (
            <div className="mt-4 border-t border-slate-100 pt-3">
              <BreakdownRows breakdown={breakdown} />
            </div>
          )}

          <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
            <span className="text-xs text-slate-500">
              {opportunity.matched_requirements}/{opportunity.total_requirements} skills met
            </span>
            <Link
              to={`/student/opportunities/${opportunity.id}`}
              className="inline-flex items-center gap-0.5 text-sm font-medium text-brand-700 hover:text-brand-800 hover:underline"
            >
              View
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </div>
      </div>
    </Card>
  )
}

