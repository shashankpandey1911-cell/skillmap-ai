import { get, post, patch, remove } from '../client'
import type { User } from '../../types'

export interface StudentProfileData {
  college: string
  course: string
  branch: string
  year: number | null
  cgpa: number | string | null
  semester: number | null
  achievements: string
  career_goal: string
  preferred_domain: string
  interests: string
  about: string
  linkedin_url: string
  github_url: string
}

/** Anything the edit form can change (user fields + profile fields). */
export type StudentProfileUpdate = Partial<
  Pick<User, 'first_name' | 'last_name' | 'phone'> & StudentProfileData
>

export interface ProfileCompleteness {
  overall: number
  sections: Record<'personal' | 'academic' | 'career' | 'projects' | 'certifications', number>
}

export interface StudentMe {
  user: User
  profile: StudentProfileData
  completeness: ProfileCompleteness
}

export interface Project {
  id: number
  name: string
  description: string
  technologies: string
  github_url: string
  demo_url: string
}

export type ProjectPayload = Omit<Project, 'id'>

export interface Certification {
  id: number
  name: string
  provider: string
  issued_date: string | null
  credential_url: string
}

export type CertificationPayload = Omit<Certification, 'id'>

export interface RecentAchievement {
  feedback_id: number
  title: string
  company: string
  opportunity_type: string
  achieved_at: string
}

export interface TopSkill {
  name: string
  proficiency: number
  category: string
}

export interface TopCareerMatch {
  title: string
  match_percentage: number
  matching_skills: string[]
}

export interface TopOpportunity {
  id: number
  title: string
  company: string
  match_percentage: number
}

export interface UpcomingDeadline {
  id: number
  title: string
  company: string
  deadline: string | null
}

export interface StudentDashboardSummary {
  profile_completeness: number
  skills_count: number
  assessments_taken: number
  applications_count: number
  career_readiness: number
  top_skills: TopSkill[]
  skill_gaps_count: number
  career_matches_count: number
  top_career_match: TopCareerMatch | null
  opportunities_count: number
  top_opportunities: TopOpportunity[]
  learning_progress: number
  completed_resources: number
  total_resources: number
  applications_by_status: Record<string, number>
  upcoming_deadlines: UpcomingDeadline[]
  achievements_count: number
  feedback_pending_count: number
  recent_achievements: RecentAchievement[]
}

// --- Profile ---
export function me(): Promise<StudentMe> {
  return get<StudentMe>('/students/me')
}

export function updateMe(payload: StudentProfileUpdate): Promise<StudentMe> {
  return patch<StudentMe>('/students/me', payload)
}

// --- Projects ---
export function listProjects(): Promise<Project[]> {
  return get<Project[]>('/students/me/projects')
}

export function createProject(payload: ProjectPayload): Promise<Project> {
  return post<Project>('/students/me/projects', payload)
}

export function updateProject(id: number, payload: ProjectPayload): Promise<Project> {
  return patch<Project>(`/students/me/projects/${id}`, payload)
}

export function deleteProject(id: number): Promise<void> {
  return remove<void>(`/students/me/projects/${id}`)
}

// --- Certifications ---
export function listCertifications(): Promise<Certification[]> {
  return get<Certification[]>('/students/me/certifications')
}

export function createCertification(payload: CertificationPayload): Promise<Certification> {
  return post<Certification>('/students/me/certifications', payload)
}

export function updateCertification(id: number, payload: CertificationPayload): Promise<Certification> {
  return patch<Certification>(`/students/me/certifications/${id}`, payload)
}

export function deleteCertification(id: number): Promise<void> {
  return remove<void>(`/students/me/certifications/${id}`)
}

export function dashboardSummary(): Promise<StudentDashboardSummary> {
  return get<StudentDashboardSummary>('/students/dashboard-summary')
}