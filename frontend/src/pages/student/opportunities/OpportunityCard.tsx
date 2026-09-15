import { Link } from 'react-router-dom'
import { ArrowRight, CalendarDays, MapPin, Wallet } from 'lucide-react'
import type { OpportunitySummary } from '../../../api/endpoints/opportunities'
import { Badge, Card, ProgressBar } from '../../../components/ui'
import { deadlineMeta, formatDate, matchTone } from './helpers'
import { TypeBadge } from './TypeBadge'

const SKILL_PREVIEW_LIMIT = 4

export function OpportunityCard({ opportunity }: { opportunity: OpportunitySummary }) {
  const deadline = deadlineMeta(opportunity.deadline)
  const match = opportunity.match_percentage

  return (
    <Card className="flex h-full flex-col">
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

      <p className="mt-2 line-clamp-2 text-sm text-slate-600">
        {opportunity.description || 'No description provided yet.'}
      </p>

      <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-slate-500">
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
            <Badge tone="slate">{deadline.label}</Badge>
          )}
        </span>
        {opportunity.compensation && (
          <span className="inline-flex items-center gap-1">
            <Wallet className="h-3.5 w-3.5" aria-hidden="true" />
            {opportunity.compensation}
          </span>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {opportunity.skill_names.length === 0 ? (
          <Badge tone="slate">No specific skills listed</Badge>
        ) : (
          opportunity.skill_names.slice(0, SKILL_PREVIEW_LIMIT).map((name) => (
            <Badge key={name} tone="slate">
              {name}
            </Badge>
          ))
        )}
        {opportunity.skill_names.length > SKILL_PREVIEW_LIMIT && (
          <span className="self-center text-xs text-slate-400">
            +{opportunity.skill_names.length - SKILL_PREVIEW_LIMIT} more
          </span>
        )}
      </div>

      <div className="mt-4 flex items-center gap-3 border-t border-slate-100 pt-3">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-baseline justify-between gap-2 text-xs">
            {match === null ? (
              <span className="text-slate-500">
                {opportunity.total_requirements === 0
                  ? 'Open to all backgrounds'
                  : 'Match unavailable'}
              </span>
            ) : (
              <>
                <span className="text-slate-500">
                  Skills match · {opportunity.matched_requirements}/
                  {opportunity.total_requirements} met
                </span>
                <span className="font-semibold text-slate-800">
                  {Math.round(match)}%
                </span>
              </>
            )}
          </div>
          {match !== null && <ProgressBar value={match} tone={matchTone(match)} />}
        </div>
        <Link
          to={`/student/opportunities/${opportunity.id}`}
          className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-brand-700 hover:text-brand-800 hover:underline"
        >
          Details
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      </div>
    </Card>
  )
}
