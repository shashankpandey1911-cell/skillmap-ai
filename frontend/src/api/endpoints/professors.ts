import { get, post, remove } from '../client'

// --- Student List ---
export interface StudentListItem {
  id: number
  email: string
  full_name: string
  first_name: string
  last_name: string
  college: string
  course: string
  branch: string
  year: number | null
  profile_completeness: number
  skills_count: number
  career_readiness: number
  date_joined: string
}

export function getStudents(params?: {
  search?: string
  branch?: string
  year?: string
  college?: string
  order?: string
}): Promise<StudentListItem[]> {
  const query = new URLSearchParams()
  if (params?.search) query.set('search', params.search)
  if (params?.branch) query.set('branch', params.branch)
  if (params?.year) query.set('year', params.year)
  if (params?.college) query.set('college', params.college)
  if (params?.order) query.set('order', params.order)
  const qs = query.toString()
  return get<StudentListItem[]>(`/professors/students${qs ? `?${qs}` : ''}`)
}

// --- Student Dossier ---
export interface StudentProfile {
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
  completeness: number
}

export interface StudentSkill {
  name: string
  category: string
  proficiency_level: number
  proficiency_percent: number
  experience_level: string
  assessment_score: number | null
}

export interface AssessmentResult {
  assessment_title: string
  score: number
  total_questions: number
  percentage: number
  completed_at: string | null
}

export interface SkillGap {
  skill_name: string
  category: string
  current_level: number
  required_level: number
  gap_percentage: number
  gap_class: string
  priority: string
  recommended_action: string
}

export interface StudentProject {
  name: string
  description: string
  technologies: string
  github_url: string
  demo_url: string
}

export interface StudentCertification {
  name: string
  provider: string
  issued_date: string | null
  credential_url: string
}

export interface StudentApplication {
  opportunity_title: string
  company: string
  status: string
  applied_at: string
  interview_date: string | null
}

export interface StudentDossier {
  id: number
  email: string
  full_name: string
  first_name: string
  last_name: string
  phone: string
  college: string
  course: string
  branch: string
  year: number | null
  profile: StudentProfile
  skills: StudentSkill[]
  assessment_results: AssessmentResult[]
  skill_gaps: SkillGap[]
  career_readiness: number
  projects: StudentProject[]
  certifications: StudentCertification[]
  applications: StudentApplication[]
}

export function getStudentDossier(studentId: number): Promise<StudentDossier> {
  return get<StudentDossier>(`/professors/students/${studentId}/dossier`)
}

// --- Guidance ---
export interface GuidanceNote {
  id: number
  professor_name: string
  student_name: string
  title: string
  message: string
  category: string
  created_at: string
  updated_at: string
}

export function getGuidanceNotes(studentId: number): Promise<GuidanceNote[]> {
  return get<GuidanceNote[]>(`/professors/students/${studentId}/guidance`)
}

export function addGuidanceNote(
  studentId: number,
  data: { title: string; message: string; category: string }
): Promise<GuidanceNote> {
  return post<GuidanceNote>(`/professors/students/${studentId}/guidance`, data)
}

export function deleteGuidanceNote(noteId: number): Promise<void> {
  return remove(`/professors/guidance/${noteId}`)
}

// --- Analytics ---
export interface CareerGoal {
  goal: string
  count: number
}

export interface SkillGapStat {
  skill: string
  affected_students: number
  avg_gap: number
}

export interface YearDist {
  year: number
  count: number
}

export interface ReadinessDist {
  high: number
  medium: number
  low: number
}

export interface ProfessorAnalytics {
  total_students: number
  career_ready_students: number
  students_with_gaps: number
  avg_assessment_score: number
  popular_career_goals: CareerGoal[]
  common_skill_gaps: SkillGapStat[]
  students_by_year: YearDist[]
  readiness_distribution: ReadinessDist
}

export function getAnalytics(): Promise<ProfessorAnalytics> {
  return get<ProfessorAnalytics>('/professors/analytics')
}

// --- Legacy dashboard summary ---
export interface ProfessorDashboardSummary {
  total_students: number
  students_with_profiles: number
  avg_profile_completeness: number
  assessments_completed: number
  feedback_given: number
}

export function dashboardSummary(): Promise<ProfessorDashboardSummary> {
  return get<ProfessorDashboardSummary>('/professors/dashboard-summary')
}
