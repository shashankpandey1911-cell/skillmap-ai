import type { MatchBreakdown } from '../../../api/endpoints/opportunities'
import { ProgressBar } from '../../../components/ui'

/** Three mini progress rows that explain the composition of a match %. */
export function BreakdownRows({ breakdown }: { breakdown: MatchBreakdown | null }) {
  if (!breakdown) return null
  return (
    <div className="space-y-2.5">
      <Row label="Skills & assessments" value={breakdown.skills} />
      <Row label="Profile & eligibility" value={breakdown.profile} />
      <Row label="Projects" value={breakdown.projects} />
    </div>
  )
}

function Row({ label, value }: { label: string; value: number | null }) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px]">
        <span className="text-slate-500">{label}</span>
        <span className="font-medium text-slate-700">
          {value === null ? '—' : `${Math.round(value)}%`}
        </span>
      </div>
      <ProgressBar
        value={value ?? 0}
        tone={value === null ? 'slate' : value >= 70 ? 'green' : 'brand'}
        className="h-1.5"
      />
    </div>
  )
}
