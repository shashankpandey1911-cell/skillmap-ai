import { get, post } from '../client'
import type { Skill } from './skills'

export const DIFFICULTIES = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT'] as const
export type Difficulty = (typeof DIFFICULTIES)[number]

export const DIFFICULTY_LABELS: Record<Difficulty, string> = {
  BEGINNER: 'Beginner',
  INTERMEDIATE: 'Intermediate',
  ADVANCED: 'Advanced',
  EXPERT: 'Expert',
}

/** Student-facing assessment metadata (questions are never in this payload). */
export interface AssessmentInfo {
  id: number
  title: string
  description: string
  skill: Skill
  difficulty: Difficulty
  duration_minutes: number
  question_count: number
  my_last_score: number | null
  my_attempts: number
}

export interface OptionChoice {
  id: number
  text: string
  order: number
}

/** Question served during an attempt: options carry no correct flag. */
export interface AssessmentQuestion {
  id: number
  text: string
  marks: number
  order: number
  options: OptionChoice[]
}

export interface StartedAssessment {
  attempt: { id: number; status: string; started_at: string }
  assessment: AssessmentInfo
  questions: AssessmentQuestion[]
}

export interface ReviewItem {
  question_id: number
  question_text: string
  selected_option_text: string | null
  correct_option_text: string | null
  is_correct: boolean
}

export interface AssessmentResultRecord {
  id: number
  score: number
  correct_count: number
  total_questions: number
  submitted_at: string
  improvement_suggestions: string[]
  assessment: AssessmentInfo
  review: ReviewItem[]
}

export interface SubmitAnswer {
  question_id: number
  option_id: number
}

// --- Student flows ---
export function listAssessments(): Promise<AssessmentInfo[]> {
  return get<AssessmentInfo[]>('/assessments')
}

export function startAssessment(id: number): Promise<StartedAssessment> {
  return post<StartedAssessment>(`/assessments/${id}/start`)
}

export function submitAssessment(
  id: number,
  attemptId: number,
  answers: SubmitAnswer[],
): Promise<AssessmentResultRecord> {
  return post<AssessmentResultRecord>(`/assessments/${id}/submit`, {
    attempt_id: attemptId,
    answers,
  })
}

export function listMyResults(): Promise<AssessmentResultRecord[]> {
  return get<AssessmentResultRecord[]>('/students/me/assessment-results')
}
