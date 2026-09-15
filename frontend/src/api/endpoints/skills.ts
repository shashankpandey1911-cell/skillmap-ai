import { get, post, patch, remove } from '../client'

export const SKILL_CATEGORIES = [
  'Programming',
  'Web Development',
  'Database',
  'Cloud',
  'AI/ML',
  'Data Science',
  'Tools',
  'Soft Skills',
  'Other',
] as const

export type SkillCategory = (typeof SKILL_CATEGORIES)[number]

export interface Skill {
  id: number
  name: string
  category: SkillCategory
  description: string
}

export interface UserSkill {
  id: number
  skill: Skill
  proficiency_level: number // 1-5 self-rating
  experience_level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT'
  assessment_score: number | null
  /** Display level 0-100: assessment score when present, else proficiency x 20. */
  score: number
  updated_at: string
}

export interface UserSkillPayload {
  skill: number
  proficiency_level: number
  experience_level: UserSkill['experience_level']
}

export const EXPERIENCE_LEVELS: { value: UserSkill['experience_level']; label: string }[] = [
  { value: 'BEGINNER', label: 'Beginner' },
  { value: 'INTERMEDIATE', label: 'Intermediate' },
  { value: 'ADVANCED', label: 'Advanced' },
  { value: 'EXPERT', label: 'Expert' },
]

export const PROFICIENCY_LABELS: Record<number, string> = {
  1: '1 · Basic',
  2: '2 · Developing',
  3: '3 · Proficient',
  4: '4 · Advanced',
  5: '5 · Expert',
}

// --- Master catalog ---
export function listCatalog(params?: { search?: string; category?: string }): Promise<Skill[]> {
  const query = new URLSearchParams()
  if (params?.search) query.set('search', params.search)
  if (params?.category) query.set('category', params.category)
  const qs = query.toString()
  return get<Skill[]>(`/skills/catalog${qs ? `?${qs}` : ''}`)
}

// --- Student's skills ---
export function listMySkills(params?: { search?: string; category?: string }): Promise<UserSkill[]> {
  const query = new URLSearchParams()
  if (params?.search) query.set('search', params.search)
  if (params?.category) query.set('category', params.category)
  const qs = query.toString()
  return get<UserSkill[]>(`/students/me/skills${qs ? `?${qs}` : ''}`)
}

export function addMySkill(payload: UserSkillPayload): Promise<UserSkill> {
  return post<UserSkill>('/students/me/skills', payload)
}

export function updateMySkill(id: number, payload: Partial<UserSkillPayload>): Promise<UserSkill> {
  return patch<UserSkill>(`/students/me/skills/${id}`, payload)
}

export function deleteMySkill(id: number): Promise<void> {
  return remove<void>(`/students/me/skills/${id}`)
}