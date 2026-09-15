import type { LucideIcon } from 'lucide-react'
import { Briefcase, GraduationCap, Rocket, Trophy } from 'lucide-react'
import {
  OPPORTUNITY_TYPE_LABELS,
  type OpportunityType,
} from '../../../api/endpoints/opportunities'
import type { BadgeTone } from '../../../components/ui'

interface TypeMeta {
  icon: LucideIcon
  badgeTone: BadgeTone
}

export const TYPE_META: Record<OpportunityType, TypeMeta> = {
  JOB: { icon: Briefcase, badgeTone: 'brand' },
  INTERNSHIP: { icon: GraduationCap, badgeTone: 'green' },
  HACKATHON: { icon: Rocket, badgeTone: 'amber' },
  COMPETITION: { icon: Trophy, badgeTone: 'slate' },
}

export function typeLabel(type: OpportunityType): string {
  return OPPORTUNITY_TYPE_LABELS[type]
}

/** Parse a YYYY-MM-DD API date at local midnight so day math is timezone-safe. */
function dateOnly(iso: string): Date {
  return new Date(`${iso}T00:00:00`)
}

export function formatDate(iso: string): string {
  return dateOnly(iso).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function deadlineMeta(deadline: string | null): {
  label: string
  tone: BadgeTone
} {
  if (!deadline) return { label: 'Open-ended', tone: 'slate' }
  const daysLeft = Math.ceil(
    (dateOnly(deadline).getTime() - Date.now()) / (24 * 60 * 60 * 1000),
  )
  if (daysLeft <= 0) return { label: 'Closes today', tone: 'red' }
  if (daysLeft === 1) return { label: 'Closes tomorrow', tone: 'red' }
  if (daysLeft <= 7) return { label: `${daysLeft} days left`, tone: 'amber' }
  return { label: `${daysLeft} days left`, tone: 'slate' }
}

export function matchTone(match: number | null): BadgeTone {
  if (match === null) return 'slate'
  if (match >= 80) return 'green'
  if (match >= 60) return 'brand'
  if (match >= 40) return 'amber'
  return 'red'
}
