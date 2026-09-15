import { get, post, remove } from '../client'

export const RESOURCE_TYPES = [
  'COURSE',
  'VIDEO',
  'DOCUMENTATION',
  'PRACTICE',
  'PROJECT',
  'QUIZ',
] as const
export type ResourceType = (typeof RESOURCE_TYPES)[number]

export const RESOURCE_LEVELS = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'] as const
export type ResourceLevel = (typeof RESOURCE_LEVELS)[number]

/** One learning resource as seen by a student (completion annotated). */
export interface LearningResource {
  id: number
  title: string
  description: string
  level: ResourceLevel
  type: ResourceType
  url: string
  estimated_duration_minutes: number
  completed: boolean
}

export interface LearningResourceListEntry {
  id: number
  title: string
  description: string
  skill_id: number
  skill_name: string
  level: ResourceLevel
  type: ResourceType
  url: string
  estimated_duration_minutes: number
  completed: boolean
}

/** A published platform assessment the roadmap can deep-link into. */
export interface PlatformAssessmentRef {
  id: number
  title: string
  difficulty: string
  question_count: number
  my_last_score: number | null
}

/** One step of a skill's roadmap (topic → resource → practice → assessment → improvement). */
export interface RoadmapStep {
  key: 'topic' | 'resource' | 'practice' | 'assessment' | 'improvement'
  title: string
  description: string
  items: LearningResource[]
  /** Present on the assessment step when a published platform assessment exists. */
  platform_assessment?: PlatformAssessmentRef
}

export interface RoadmapSkill {
  skill: { id: number; name: string; category: string }
  gap: {
    current_level: number
    required_level: number
    gap_percentage: number
    gap_class: 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH'
    priority: 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH'
  }
  recommended_action: string
  steps: RoadmapStep[]
}

export interface LearningRoadmap {
  career: { id: number; title: string; category: string }
  readiness_percentage: number
  progress: {
    total_resources: number
    completed_resources: number
    remaining_resources: number
    progress_percentage: number
  }
  priority_skills: {
    skill_id: number
    skill_name: string
    gap_class: RoadmapSkill['gap']['gap_class']
    priority: RoadmapSkill['gap']['priority']
    gap_percentage: number
  }[]
  roadmap: RoadmapSkill[]
  /** Phase 12: skills accepted from rejected-application feedback. */
  feedback_roadmap?: (RoadmapSkill & {
    source: { feedback_id: number; kind: string; opportunity: string; company: string }
  })[]
}

export function getLearningRoadmap(
  careerId: number,
  studentId?: number,
): Promise<LearningRoadmap> {
  const params = new URLSearchParams({ career_id: String(careerId) })
  if (studentId) params.set('student_id', String(studentId))
  return get<LearningRoadmap>(`/learning/roadmap?${params.toString()}`)
}

export function listLearningResources(params?: {
  skill_id?: number
  search?: string
  type?: ResourceType
}): Promise<LearningResourceListEntry[]> {
  const query = new URLSearchParams()
  if (params?.skill_id) query.set('skill_id', String(params.skill_id))
  if (params?.search) query.set('search', params.search)
  if (params?.type) query.set('type', params.type)
  const qs = query.toString()
  return get<LearningResourceListEntry[]>(`/learning/resources${qs ? `?${qs}` : ''}`)
}

export function markResourceCompleted(id: number): Promise<{ id: number; completed: boolean }> {
  return post<{ id: number; completed: boolean }>(`/learning/resources/${id}/complete`)
}

export function markResourceIncomplete(id: number): Promise<{ id: number; completed: boolean }> {
  return remove<{ id: number; completed: boolean }>(`/learning/resources/${id}/complete`)
}
