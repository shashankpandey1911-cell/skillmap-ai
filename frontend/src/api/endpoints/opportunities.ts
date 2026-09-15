import { get } from '../client'
import type { Skill } from './skills'

export const OPPORTUNITY_TYPES = ['JOB', 'INTERNSHIP', 'HACKATHON', 'COMPETITION'] as const
export type OpportunityType = (typeof OPPORTUNITY_TYPES)[number]

export const OPPORTUNITY_TYPE_LABELS: Record<OpportunityType, string> = {
  JOB: 'Job',
  INTERNSHIP: 'Internship',
  HACKATHON: 'Hackathon',
  COMPETITION: 'Competition',
}

export const OPPORTUNITY_STATUSES = ['ACTIVE', 'DRAFT', 'CLOSED'] as const
export type OpportunityStatus = (typeof OPPORTUNITY_STATUSES)[number]

/** Signal breakdown behind an opportunity's match percentage. */
export interface MatchBreakdown {
  /** Null when the posting lists no required skills. */
  skills: number | null
  profile: number
  projects: number
}

/** Fields shared by the browse listing, detail view and recommendations. */
export interface OpportunitySummary {
  id: number
  title: string
  company: string
  opportunity_type: OpportunityType
  description: string
  eligibility: string
  location: string
  is_remote: boolean
  /** ISO date (YYYY-MM-DD) or null for an open-ended posting. */
  deadline: string | null
  compensation: string
  application_link: string
  /** ISO datetime; used by the "Recently added" rail. */
  created_at: string
  skill_names: string[]
  match_percentage: number | null
  matching_skills: string[]
  missing_skills: string[]
  matched_requirements: number
  total_requirements: number
  breakdown: MatchBreakdown | null
  explanation: string | null
  recommended_next_steps: string[]
}

export interface OpportunityRequirementRow {
  id: number
  skill: Skill
  min_level: number
  /** The student's current 0-100 level for this skill. */
  my_level: number
  met: boolean
}

export interface OpportunityDetail extends OpportunitySummary {
  requirements: OpportunityRequirementRow[]
  /** The student's own application for this posting, if they have applied. */
  my_application?: {
    id: number
    status: string
    applied_at: string
  } | null
}

export interface OpportunityRecommendations {
  disclaimer: string
  items: OpportunitySummary[]
}

export interface OpportunityListParams {
  search?: string
  type?: OpportunityType
  location?: string
  remote?: boolean
  /** recent (default) | deadline | match */
  sort?: 'recent' | 'deadline' | 'match'
  studentId?: number
}

export function listOpportunities(params: OpportunityListParams = {}): Promise<OpportunitySummary[]> {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.type) query.set('type', params.type)
  if (params.location) query.set('location', params.location)
  if (params.remote) query.set('remote', '1')
  if (params.sort && params.sort !== 'recent') query.set('sort', params.sort)
  if (params.studentId) query.set('student_id', String(params.studentId))
  const qs = query.toString()
  return get<OpportunitySummary[]>(`/opportunities${qs ? `?${qs}` : ''}`)
}

export function getOpportunity(id: number, studentId?: number): Promise<OpportunityDetail> {
  return get<OpportunityDetail>(
    `/opportunities/${id}${studentId ? `?student_id=${studentId}` : ''}`,
  )
}

/** Every active posting ranked by the smart match engine, best first. */
export function getOpportunityRecommendations(
  studentId?: number,
): Promise<OpportunityRecommendations> {
  return get<OpportunityRecommendations>(
    `/opportunities/recommendations${studentId ? `?student_id=${studentId}` : ''}`,
  )
}
