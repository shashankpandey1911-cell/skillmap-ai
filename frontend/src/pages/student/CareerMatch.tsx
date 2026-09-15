import { useState } from 'react'
import {
  CheckCircle2,
  Compass,
  Info,
  Lightbulb,
  ListChecks,
  TrendingUp,
  XCircle,
} from 'lucide-react'
import { type CareerMatch, getCareerMatches } from '../../api/endpoints/careers'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../auth/AuthContext'
import { Alert, Badge, Card, ProgressBar, Spinner, StatCard } from '../../components/ui'
import { cn } from '../../utils/cn'

function matchTone(value: number): 'green' | 'brand' | 'amber' | 'red' {
  if (value >= 70) return 'green'
  if (value >= 50) return 'brand'
  if (value >= 30) return 'amber'
  return 'red'
}

const TONE_TEXT: Record<'green' | 'brand' | 'amber' | 'red', string> = {
  green: 'text-emerald-600',
  brand: 'text-brand-700',
  amber: 'text-amber-600',
  red: 'text-red-600',
}

export function CareerMatchPage() {
  const { user } = useAuth()
  const { data, loading, error, refresh } = useApi(() => getCareerMatches(), [])
  const [expanded, setExpanded] = useState<number | null>(null)

  const matches = data?.matches ?? []
  const topMatch = matches[0]
  const strongMatches = matches.filter((m) => m.match_percentage >= 70).length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Career Match</h2>
        <p className="mt-1 text-sm text-slate-500">
          {user?.full_name ?? user?.username}, careers ranked for you by match
          percentage — computed from your skills, interests, projects and career goal.
        </p>
      </div>

      {loading ? (
        <Spinner />
      ) : error ? (
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
      ) : (
        <>
          {data && (
            <Alert tone="info">
              <span>{data.disclaimer}</span>
            </Alert>
          )}

          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard
              label="Top match"
              value={topMatch ? `${Math.round(topMatch.match_percentage)}%` : '—'}
              icon={Compass}
              sub={topMatch?.career.title ?? 'No careers published'}
            />
            <StatCard
              label="Strong matches"
              value={strongMatches}
              icon={TrendingUp}
              sub="Careers at 70% or above"
            />
            <StatCard
              label="Careers analyzed"
              value={matches.length}
              icon={ListChecks}
              sub="Active roles in the catalog"
            />
          </div>

          {matches.length === 0 ? (
            <Card>
              <div className="flex flex-col items-center gap-3 py-8 text-center">
                <Compass className="h-10 w-10 text-slate-300" aria-hidden="true" />
                <div>
                  <p className="font-medium text-slate-800">No careers to match yet</p>
                  <p className="mt-1 text-sm text-slate-500">
                    The admin defines career paths here before recommendations can run.
                  </p>
                </div>
              </div>
            </Card>
          ) : (
            <div className="space-y-4">
              {matches.map((match, index) => (
                <MatchCard
                  key={match.career.id}
                  match={match}
                  rank={index + 1}
                  open={expanded === match.career.id}
                  onToggle={() =>
                    setExpanded(expanded === match.career.id ? null : match.career.id)
                  }
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

function MatchCard({
  match,
  rank,
  open,
  onToggle,
}: {
  match: CareerMatch
  rank: number
  open: boolean
  onToggle: () => void
}) {
  const tone = matchTone(match.match_percentage)
  const met = match.matching_skills.length
  const total = met + match.missing_skills.length

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-brand-50 font-bold text-brand-700">
          {rank}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base font-semibold text-slate-900">
              {match.career.title}
            </h3>
            <Badge tone="slate">{match.career.category}</Badge>
          </div>
          <p className="mt-0.5 line-clamp-2 text-sm text-slate-500">
            {match.career.description}
          </p>
        </div>
        <div className="w-full shrink-0 lg:w-48">
          <div className="flex items-baseline justify-between">
            <span className="text-xs text-slate-500">Match</span>
            <span className={cn('text-2xl font-bold', TONE_TEXT[tone])}>
              {Math.round(match.match_percentage)}%
            </span>
          </div>
          <ProgressBar value={match.match_percentage} tone={tone} className="mt-1" />
        </div>
      </div>

      <div className="mt-4">
        <p className="text-sm text-slate-700">{match.explanation}</p>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {match.matching_skills.map((skill) => (
            <Badge key={`m-${skill}`} tone="green" className="gap-1">
              <CheckCircle2 className="h-3 w-3" aria-hidden="true" />
              {skill}
            </Badge>
          ))}
          {match.missing_skills.map((skill) => (
            <Badge key={`x-${skill}`} tone="amber" className="gap-1">
              <XCircle className="h-3 w-3" aria-hidden="true" />
              {skill}
            </Badge>
          ))}
        </div>
        <p className="mt-2 text-xs text-slate-400">
          {met} of {total} required skills met — green = matching, amber = missing
        </p>
      </div>

      {match.recommended_next_steps.length > 0 && (
        <div className="mt-4 border-t border-slate-100 pt-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-800">
            <ListChecks className="h-4 w-4 text-brand-600" aria-hidden="true" />
            Recommended next steps
          </div>
          <ul className="mt-2 space-y-1.5">
            {match.recommended_next_steps.map((step, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
                {step}
              </li>
            ))}
          </ul>
        </div>
      )}

      {match.career.learning_areas && (
        <div className="mt-4 flex items-start gap-2 rounded-lg bg-slate-50 px-3 py-2.5">
          <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" aria-hidden="true" />
          <p className="text-sm text-slate-600">
            <span className="font-medium text-slate-700">Recommended learning:</span>{' '}
            {match.career.learning_areas}
          </p>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
        <span className="text-xs text-slate-400">
          Drivers: skills {Math.round(match.breakdown.skills)}% · interests{' '}
          {Math.round(match.breakdown.interests)}% · projects{' '}
          {Math.round(match.breakdown.projects)}% · goal{' '}
          {Math.round(match.breakdown.goal)}%
        </span>
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={open}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 hover:text-brand-800"
        >
          <Info className="h-4 w-4" aria-hidden="true" />
          {open ? 'Hide details' : 'Why this match?'}
        </button>
      </div>

      {open && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/60 p-4">
          <dl className="grid gap-3 sm:grid-cols-2">
            <div>
              <dt className="text-xs font-medium text-slate-500">Domain</dt>
              <dd className="text-sm text-slate-800">{match.career.category}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-slate-500">Typical education</dt>
              <dd className="text-sm text-slate-800">{match.career.education}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-slate-500">Salary range</dt>
              <dd className="text-sm text-slate-800">{match.career.salary_range}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium text-slate-500">Required skills</dt>
              <dd className="text-sm text-slate-800">{total}</dd>
            </div>
          </dl>
          {match.career.outlook && (
            <p className="mt-3 border-t border-slate-200 pt-3 text-sm text-slate-600">
              <span className="font-medium text-slate-700">Outlook:</span>{' '}
              {match.career.outlook}
            </p>
          )}
        </div>
      )}
    </Card>
  )
}