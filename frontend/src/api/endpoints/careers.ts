import { get } from '../client'

export const GAP_CLASSES = ['NONE', 'LOW', 'MEDIUM', 'HIGH'] as const
export type GapClass = (typeof GAP_CLASSES)[number]

export const PRIORITIES = ['NONE', 'LOW', 'MEDIUM', 'HIGH'] as const
export type Priority = (typeof PRIORITIES)[number]

export const IMPORTANCE_LEVELS = ['LOW', 'MEDIUM', 'HIGH'] as const
export type Importance = (typeof IMPORTANCE_LEVELS)[number]

export interface Career {
  id: number
  title: string
  description: string
  category: string
  education: string
  salary_range: string
  learning_areas: string
  skill_count: number
  /** Only present on career detail responses. */
  outlook?: string
}

export interface CareerRequirement {
  id: number
  skill: { id: number; name: string; category: string; description: string }
  target_level: number
  importance: Importance
}

export interface CareerDetail extends Career {
  outlook: string
  requirements: CareerRequirement[]
}

/** One row of the Skill Gap Dashboard. */
export interface SkillGapEntry {
  skill_id: number
  skill_name: string
  category: string
  current_level: number
  required_level: number
  gap_percentage: number
  gap_class: GapClass
  importance: Importance
  priority: Priority
  recommended_action: string
}

export interface GapAnalysis {
  career: Career
  readiness_percentage: number
  gaps: SkillGapEntry[]
  summary: {
    total: number
    no_gap: number
    low: number
    medium: number
    high: number
  }
}

/** One ranked career recommendation. */
export interface CareerMatch {
  career: Career
  match_percentage: number
  matching_skills: string[]
  missing_skills: string[]
  breakdown: {
    skills: number
    interests: number
    projects: number
    goal: number
  }
  explanation: string
  recommended_next_steps: string[]
}

export interface CareerMatchesResponse {
  disclaimer: string
  matches: CareerMatch[]
}

export function listCareers(): Promise<Career[]> {
  return get<Career[]>('/careers')
}

export function getCareer(id: number): Promise<CareerDetail> {
  return get<CareerDetail>(`/careers/${id}`)
}

/** The calling student's own analysis (professors/admin pass student_id). */
export function getGapAnalysis(id: number, studentId?: number): Promise<GapAnalysis> {
  return get<GapAnalysis>(
    `/careers/${id}/gap-analysis${studentId ? `?student_id=${studentId}` : ''}`,
  )
}

/** Every active career ranked by match percentage for the student. */
export function getCareerMatches(studentId?: number): Promise<CareerMatchesResponse> {
  return get<CareerMatchesResponse>(
    `/careers/matches${studentId ? `?student_id=${studentId}` : ''}`,
  )
}