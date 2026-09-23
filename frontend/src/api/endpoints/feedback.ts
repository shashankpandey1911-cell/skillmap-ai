import { get, patch, post } from '../client'
import type { OpportunityBrief } from './applications'

export const FEEDBACK_KINDS = ['REJECTED', 'SELECTED'] as const
export type FeedbackKind = (typeof FEEDBACK_KINDS)[number]

export const FEEDBACK_STATUSES = ['PENDING', 'ACCEPTED', 'DISMISSED'] as const
export type FeedbackStatus = (typeof FEEDBACK_STATUSES)[number]

export const FEEDBACK_KIND_LABELS: Record<FeedbackKind, string> = {
  REJECTED: 'Application Rejected',
  SELECTED: 'Application Selected',
}

export const FEEDBACK_STATUS_LABELS: Record<FeedbackStatus, string> = {
  PENDING: 'Pending decision',
  ACCEPTED: 'Added to my roadmap',
  DISMISSED: 'Dismissed',
}

/** One live recommendation for a feedback gap (from the learning catalog). */
export interface FeedbackRecommendation {
  resource_id: number | null
  title: string
  kind: string
  level: string
  url: string
  estimated_duration_minutes: number | null
  description?: string
}

/** A skill gap recorded when the application was rejected. */
export interface FeedbackGap {
  id: number
  skill_id: number
  skill_name: string
  category: string
  current_level: number
  required_level: number
  gap_percentage: number
  gap_class: 'LOW' | 'MEDIUM' | 'HIGH'
  priority: 'LOW' | 'MEDIUM' | 'HIGH'
  recommended_action: string
  recommendations: FeedbackRecommendation[]
}

export interface ApplicationFeedback {
  id: number
  kind: FeedbackKind
  status: FeedbackStatus
  summary: string
  notes: string
  opportunity: OpportunityBrief
  gaps: FeedbackGap[]
  created_at: string
  updated_at: string
}

export function listFeedback(params?: {
  kind?: FeedbackKind
  status?: FeedbackStatus
  studentId?: number
}): Promise<ApplicationFeedback[]> {
  const query = new URLSearchParams()
  if (params?.kind) query.set('kind', params.kind)
  if (params?.status) query.set('status', params.status)
  if (params?.studentId) query.set('student_id', String(params.studentId))
  const qs = query.toString()
  return get<ApplicationFeedback[]>(`/feedback${qs ? `?${qs}` : ''}`)
}

export function getFeedback(id: number): Promise<ApplicationFeedback> {
  return get<ApplicationFeedback>(`/feedback/${id}`)
}

export function updateFeedbackNotes(id: number, notes: string): Promise<ApplicationFeedback> {
  return patch<ApplicationFeedback>(`/feedback/${id}`, { notes })
}

export function acceptFeedback(id: number): Promise<ApplicationFeedback> {
  return post<ApplicationFeedback>(`/feedback/${id}/accept`)
}

export function dismissFeedback(id: number): Promise<ApplicationFeedback> {
  return post<ApplicationFeedback>(`/feedback/${id}/dismiss`)
}
