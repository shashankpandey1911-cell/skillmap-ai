import { get, post, patch, remove } from '../client'

// ─── Dashboard Summary ────────────────────────────────────────────────────
export interface AdminDashboardSummary {
  total_users: number
  students: number
  professors: number
  admins: number
}

export function dashboardSummary(): Promise<AdminDashboardSummary> {
  return get<AdminDashboardSummary>('/admin/dashboard-summary')
}

// ─── Users ────────────────────────────────────────────────────────────────
export interface AdminUser {
  id: number
  username: string
  email: string
  full_name: string
  first_name: string
  last_name: string
  role: string
  phone: string
  is_active: boolean
  date_joined: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export function listUsers(params?: Record<string, string>): Promise<PaginatedResponse<AdminUser>> {
  return get<PaginatedResponse<AdminUser>>('/admin/users', { params })
}

export function createUser(data: {
  full_name: string
  email: string
  password: string
  role: string
  phone?: string
}): Promise<AdminUser> {
  return post<AdminUser>('/admin/users/create', data)
}

export function updateUser(
  id: number,
  data: Partial<Pick<AdminUser, 'is_active' | 'role' | 'phone'>>
): Promise<AdminUser> {
  return patch<AdminUser>(`/admin/users/${id}`, data)
}

export function deleteUser(id: number): Promise<void> {
  return remove(`/admin/users/${id}`)
}

export function changeUserPassword(
  id: number,
  data: { new_password: string; confirm_password: string }
): Promise<{ detail: string }> {
  return post<{ detail: string }>(`/admin/users/${id}/change-password`, data)
}

// ─── Skills ───────────────────────────────────────────────────────────────
export interface AdminSkill {
  id: number
  name: string
  category: string
  description: string
  is_active: boolean
  user_count: number
  created_at: string
}

export function listSkills(params?: Record<string, string>): Promise<PaginatedResponse<AdminSkill>> {
  return get<PaginatedResponse<AdminSkill>>('/admin/skills', { params })
}

export function createSkill(data: {
  name: string
  category: string
  description?: string
}): Promise<AdminSkill> {
  return post<AdminSkill>('/admin/skills', data)
}

export function updateSkill(
  id: number,
  data: Partial<Pick<AdminSkill, 'name' | 'category' | 'description' | 'is_active'>>
): Promise<AdminSkill> {
  return patch<AdminSkill>(`/admin/skills/${id}`, data)
}

export function deleteSkill(id: number): Promise<void> {
  return remove(`/admin/skills/${id}`)
}

// ─── Careers ──────────────────────────────────────────────────────────────
export interface AdminCareerRequirement {
  id: number
  skill: number
  skill_name: string
  target_level: number
  importance: string
}

export interface AdminCareer {
  id: number
  title: string
  description: string
  category: string
  education: string
  outlook: string
  salary_range: string
  domain_keywords: string
  learning_areas: string
  is_active: boolean
  requirements: AdminCareerRequirement[]
  created_at: string
}

export function listCareers(params?: Record<string, string>): Promise<PaginatedResponse<AdminCareer>> {
  return get<PaginatedResponse<AdminCareer>>('/admin/careers', { params })
}

export function createCareer(data: Partial<AdminCareer>): Promise<AdminCareer> {
  return post<AdminCareer>('/admin/careers', data)
}

export function updateCareer(
  id: number,
  data: Partial<AdminCareer>
): Promise<AdminCareer> {
  return patch<AdminCareer>(`/admin/careers/${id}`, data)
}

export function deleteCareer(id: number): Promise<void> {
  return remove(`/admin/careers/${id}`)
}

// ─── Assessments ──────────────────────────────────────────────────────────
export interface AdminAssessmentOption {
  id: number
  text: string
  is_correct: boolean
  order: number
}

export interface AdminAssessmentQuestion {
  id: number
  text: string
  marks: number
  order: number
  options: AdminAssessmentOption[]
}

export interface AdminAssessment {
  id: number
  title: string
  description: string
  skill: number
  skill_name: string
  difficulty: string
  duration_minutes: number
  is_published: boolean
  question_count: number
  created_at: string
  questions?: AdminAssessmentQuestion[]
}

export function listAssessments(params?: Record<string, string>): Promise<PaginatedResponse<AdminAssessment>> {
  return get<PaginatedResponse<AdminAssessment>>('/admin/assessments', { params })
}

export function createAssessment(
  data: Partial<AdminAssessment>
): Promise<AdminAssessment> {
  return post<AdminAssessment>('/admin/assessments', data)
}

export function getAssessment(id: number): Promise<AdminAssessment> {
  return get<AdminAssessment>(`/admin/assessments/${id}`)
}

export function updateAssessment(
  id: number,
  data: Partial<AdminAssessment>
): Promise<AdminAssessment> {
  return patch<AdminAssessment>(`/admin/assessments/${id}`, data)
}

export function deleteAssessment(id: number): Promise<void> {
  return remove(`/admin/assessments/${id}`)
}

// ─── Opportunities ────────────────────────────────────────────────────────
export interface AdminOpportunityRequirement {
  id: number
  skill: number
  skill_name: string
  min_level: number
}

export interface AdminOpportunity {
  id: number
  title: string
  company: string
  opportunity_type: string
  description: string
  eligibility: string
  location: string
  is_remote: boolean
  deadline: string | null
  application_link: string
  compensation: string
  status: string
  requirements: AdminOpportunityRequirement[]
  application_count: number
  created_at: string
}

export function listOpportunities(params?: Record<string, string>): Promise<PaginatedResponse<AdminOpportunity>> {
  return get<PaginatedResponse<AdminOpportunity>>('/admin/opportunities', { params })
}

export function createOpportunity(
  data: Partial<AdminOpportunity>
): Promise<AdminOpportunity> {
  return post<AdminOpportunity>('/admin/opportunities', data)
}

export function updateOpportunity(
  id: number,
  data: Partial<AdminOpportunity>
): Promise<AdminOpportunity> {
  return patch<AdminOpportunity>(`/admin/opportunities/${id}`, data)
}

export function deleteOpportunity(id: number): Promise<void> {
  return remove(`/admin/opportunities/${id}`)
}

// ─── Learning Resources ───────────────────────────────────────────────────
export interface AdminLearningResource {
  id: number
  title: string
  description: string
  skill: number
  skill_name: string
  level: string
  type: string
  url: string
  estimated_duration_minutes: number
  is_active: boolean
  created_at: string
}

export function listResources(params?: Record<string, string>): Promise<PaginatedResponse<AdminLearningResource>> {
  return get<PaginatedResponse<AdminLearningResource>>('/admin/resources', { params })
}

export function createResource(
  data: Partial<AdminLearningResource>
): Promise<AdminLearningResource> {
  return post<AdminLearningResource>('/admin/resources', data)
}

export function updateResource(
  id: number,
  data: Partial<AdminLearningResource>
): Promise<AdminLearningResource> {
  return patch<AdminLearningResource>(`/admin/resources/${id}`, data)
}

export function deleteResource(id: number): Promise<void> {
  return remove(`/admin/resources/${id}`)
}

// ─── Applications ─────────────────────────────────────────────────────────
export interface AdminApplication {
  id: number
  student_name: string
  student_email: string
  opportunity_title: string
  opportunity_company: string
  status: string
  applied_at: string
  notes: string
}

export function listApplications(params?: Record<string, string>): Promise<AdminApplication[]> {
  return get<AdminApplication[]>('/admin/applications', { params })
}

// ─── Notifications ────────────────────────────────────────────────────────
export function sendNotification(data: {
  title: string
  body: string
  target: string
}): Promise<{ detail: string }> {
  return post<{ detail: string }>('/admin/notifications/send', data)
}

// ─── Analytics ────────────────────────────────────────────────────────────
export interface AdminAnalytics {
  total_users: number
  total_students: number
  total_professors: number
  total_admins: number
  total_skills: number
  total_careers: number
  total_assessments: number
  total_opportunities: number
  total_applications: number
  total_learning_resources: number
  selected_students: number
  active_opportunities: number
  published_assessments: number
  users_by_role: { role: string; count: number }[]
  users_by_month: { month: string; count: number }[]
  popular_skills: { name: string; category: string; student_count: number }[]
  popular_careers: { title: string; category: string; req_count: number }[]
  applications_by_status: { status: string; count: number }[]
  common_skill_gaps: {
    skill: string
    category: string
    required_by: number
    students_have: number
  }[]
}

export function getAnalytics(): Promise<AdminAnalytics> {
  return get<AdminAnalytics>('/admin/analytics')
}
