import { get, patch, post } from '../client'
import type { OpportunityType } from './opportunities'

export const APPLICATION_STATUSES = [
  'APPLIED',
  'SUBMITTED',
  'UNDER_REVIEW',
  'SHORTLISTED',
  'INTERVIEW',
  'SELECTED',
  'REJECTED',
] as const
export type ApplicationStatus = (typeof APPLICATION_STATUSES)[number]

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  APPLIED: 'Applied',
  SUBMITTED: 'Submitted',
  UNDER_REVIEW: 'Under Review',
  SHORTLISTED: 'Shortlisted',
  INTERVIEW: 'Interview',
  SELECTED: 'Selected',
  REJECTED: 'Rejected',
}

/** The forward path of the lifecycle (REJECTED is a terminal outcome). */
export const STATUS_STAGES: ApplicationStatus[] = [
  'APPLIED',
  'SUBMITTED',
  'UNDER_REVIEW',
  'SHORTLISTED',
  'INTERVIEW',
  'SELECTED',
]

/** Opportunity fields attached to each application (deadline included). */
export interface OpportunityBrief {
  id: number
  title: string
  company: string
  opportunity_type: OpportunityType
  location: string
  is_remote: boolean
  /** ISO date (YYYY-MM-DD) or null when the posting is open-ended. */
  deadline: string | null
  compensation: string
}

export interface ApplicationRecord {
  id: number
  opportunity: OpportunityBrief
  status: ApplicationStatus
  notes: string
  /** ISO date (YYYY-MM-DD) or null until the admin schedules an interview. */
  interview_date: string | null
  applied_at: string
  updated_at: string
}

export interface MyApplicationSummary {
  id: number
  status: ApplicationStatus
  applied_at: string
}

export function listMyApplications(params?: {
  status?: ApplicationStatus
  search?: string
}): Promise<ApplicationRecord[]> {
  const query = new URLSearchParams()
  if (params?.status) query.set('status', params.status)
  if (params?.search) query.set('search', params.search)
  const qs = query.toString()
  return get<ApplicationRecord[]>(`/students/me/applications${qs ? `?${qs}` : ''}`)
}

export function applyToOpportunity(opportunityId: number): Promise<ApplicationRecord> {
  return post<ApplicationRecord>('/students/me/applications', { opportunity: opportunityId })
}

export function updateApplicationNotes(id: number, notes: string): Promise<ApplicationRecord> {
  return patch<ApplicationRecord>(`/students/me/applications/${id}`, { notes })
}
