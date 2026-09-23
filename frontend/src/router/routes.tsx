import type { ComponentType } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  Award,
  BarChart3,
  BookOpen,
  Briefcase,
  ClipboardCheck,
  ClipboardList,
  Compass,
  GraduationCap,
  LayoutDashboard,
  Settings,
  Sparkles,
  Target,
  Users,
  UserCircle2,
} from 'lucide-react'
import type { Role } from '../types'
import { StudentDashboard } from '../pages/student/Dashboard'
import { StudentProfilePage } from '../pages/student/Profile'
import { MySkillsPage } from '../pages/student/Skills'
import { MyAssessmentsPage } from '../pages/student/Assessments'
import { SkillGapPage } from '../pages/student/SkillGap'
import { CareerMatchPage } from '../pages/student/CareerMatch'
import { LearningRoadmapPage } from '../pages/student/LearningRoadmap'
import { OpportunitiesPage } from '../pages/student/opportunities/ListPage'
import { OpportunityDetailPage } from '../pages/student/opportunities/DetailPage'
import { OpportunityMatchesPage } from '../pages/student/opportunities/Recommendations'
import { MyApplicationsPage } from '../pages/student/applications/MyApplications'
import { CareerImprovementPage } from '../pages/student/CareerImprovement'
import { ProfessorDashboard } from '../pages/professor/Dashboard'
import { ProfessorStudentList } from '../pages/professor/students/StudentList'
import { StudentDossierPage } from '../pages/professor/students/StudentDossier'
import { ProfessorAnalytics } from '../pages/professor/Analytics'
import { AdminDashboard } from '../pages/admin/Dashboard'

import { UsersPage } from '../pages/admin/UsersPage'
import { SkillsPage } from '../pages/admin/SkillsPage'
import { CareersPage } from '../pages/admin/CareersPage'
import { AssessmentsPage } from '../pages/admin/AssessmentsPage'
import { OpportunitiesPage as AdminOpportunitiesPage } from '../pages/admin/OpportunitiesPage'
import { ResourcesPage } from '../pages/admin/ResourcesPage'
import { ApplicationsPage } from '../pages/admin/ApplicationsPage'
import { AnalyticsPage } from '../pages/admin/AnalyticsPage'
import { NotificationsPage } from '../pages/admin/NotificationsPage'

/**
 * Single source of truth for navigation. The sidebar renders from
 * `navItems()` and the router builds routes from these tables, so the
 * navigation can never drift from the actual routes.
 */

export interface RouteMeta {
  path: string
  title: string
  description: string
  /** Which build phase implements this feature (see docs/ROADMAP.md). */
  phase: string
  role?: Role
  nav?: boolean
  icon?: LucideIcon
  /** Real page component; falls back to FeaturePlaceholder while pending. */
  page?: ComponentType
  /** Feature list shown on the placeholder while the phase is pending. */
  planned?: string[]
}

export const studentRoutes: RouteMeta[] = [
  {
    path: '/student/dashboard',
    title: 'Student Dashboard',
    description: 'Career readiness overview: profile, skills, assessments and applications.',
    phase: 'Phase 2',
    role: 'STUDENT',
    nav: true,
    icon: LayoutDashboard,
    page: StudentDashboard,
  },
  {
    path: '/student/profile',
    title: 'My Profile',
    description: 'Your digital career profile: personal, academic, career, projects and certifications.',
    phase: 'Phase 3',
    role: 'STUDENT',
    nav: true,
    icon: UserCircle2,
    page: StudentProfilePage,
  },
  {
    path: '/student/skills',
    title: 'My Skills',
    description: 'Your skill catalog: self-rated proficiency, experience and assessment scores.',
    phase: 'Phase 4',
    role: 'STUDENT',
    nav: true,
    icon: GraduationCap,
    page: MySkillsPage,
  },
  {
    path: '/student/assessments',
    title: 'Skill Assessments',
    description: 'Take timed skill assessments and see your score update in real time.',
    phase: 'Phase 5',
    role: 'STUDENT',
    nav: true,
    icon: ClipboardCheck,
    page: MyAssessmentsPage,
  },
  {
    path: '/student/careers',
    title: 'Skill Gap Analysis',
    description: 'Compare your current skill levels against a career’s requirements and see exactly what to close.',
    phase: 'Phase 6',
    role: 'STUDENT',
    nav: true,
    icon: Target,
    page: SkillGapPage,
  },
  {
    path: '/student/career-match',
    title: 'Career Match',
    description: 'Careers ranked by match percentage, with matching and missing skills explained.',
    phase: 'Phase 7',
    role: 'STUDENT',
    nav: true,
    icon: Compass,
    page: CareerMatchPage,
  },
  {
    path: '/student/learning',
    title: 'Learning Roadmap',
    description: 'Your personalized learning roadmap — turn every skill gap into concrete resources and track progress.',
    phase: 'Phase 8',
    role: 'STUDENT',
    nav: true,
    icon: BookOpen,
    page: LearningRoadmapPage,
  },
  {
    path: '/student/opportunity-matches',
    title: 'Opportunity Matches',
    description: 'Open roles ranked by an explainable match — recommended for you, highest match, closing soon and recently added.',
    phase: 'Phase 10',
    role: 'STUDENT',
    nav: true,
    icon: Sparkles,
    page: OpportunityMatchesPage,
  },
  {
    path: '/student/opportunities',
    title: 'Opportunities',
    description: 'Browse open jobs, internships, hackathons and competitions — filtered and scored against your skills.',
    phase: 'Phase 9',
    role: 'STUDENT',
    nav: true,
    icon: Briefcase,
    page: OpportunitiesPage,
  },
  {
    path: '/student/opportunities/:id',
    title: 'Opportunity Details',
    description: 'Full posting with required skills and your match score.',
    phase: 'Phase 9',
    role: 'STUDENT',
    page: OpportunityDetailPage,
  },
  {
    path: '/student/applications',
    title: 'My Applications',
    description: 'Apply to opportunities and track every application through its status lifecycle.',
    phase: 'Phase 11',
    role: 'STUDENT',
    nav: true,
    icon: ClipboardList,
    page: MyApplicationsPage,
  },
  {
    path: '/student/improvement',
    title: 'Career Improvement',
    description: 'Learn from every decision — rejection gaps and recommendations you can accept, and selections recorded as achievements.',
    phase: 'Phase 12',
    role: 'STUDENT',
    nav: true,
    icon: Award,
    page: CareerImprovementPage,
  },
]

export const professorRoutes: RouteMeta[] = [
  {
    path: '/professor/dashboard',
    title: 'Professor Dashboard',
    description: 'Your students\' readiness at a glance and cohort analytics.',
    phase: 'Phase 2',
    role: 'PROFESSOR',
    nav: true,
    icon: LayoutDashboard,
    page: ProfessorDashboard,
  },
  {
    path: '/professor/students',
    title: 'Students',
    description: 'Browse your students and open their full career dossier.',
    phase: 'Phase 4',
    role: 'PROFESSOR',
    nav: true,
    icon: Users,
    page: ProfessorStudentList,
  },
  {
    path: '/professor/students/:id',
    title: 'Student Dossier',
    description: 'View a student\'s full career profile, skills, gaps, and guidance.',
    phase: 'Phase 4',
    role: 'PROFESSOR',
    nav: false,
    icon: Users,
    page: StudentDossierPage,
  },
  {
    path: '/professor/analytics',
    title: 'Analytics',
    description: 'Class-level skill and readiness analytics.',
    phase: 'Phase 6',
    role: 'PROFESSOR',
    nav: true,
    icon: BarChart3,
    page: ProfessorAnalytics,
  },
]

export const adminRoutes: RouteMeta[] = [
  {
    path: '/admin/dashboard',
    title: 'Admin Dashboard',
    description: 'Platform health: users, content and activity metrics.',
    phase: 'Phase 2',
    role: 'ADMIN',
    nav: true,
    icon: LayoutDashboard,
    page: AdminDashboard,
  },
  {
    path: '/admin/users',
    title: 'Manage Users',
    description: 'Create, edit, activate and assign roles to users.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: Users,
    page: UsersPage,
  },
  {
    path: '/admin/skills',
    title: 'Manage Skills',
    description: 'Maintain the master skill catalog.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: GraduationCap,
    page: SkillsPage,
  },
  {
    path: '/admin/careers',
    title: 'Manage Careers',
    description: 'Career catalog and required skill levels.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: Target,
    page: CareersPage,
  },
  {
    path: '/admin/assessments',
    title: 'Manage Assessments',
    description: 'Build assessments and their question banks.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: ClipboardList,
    page: AssessmentsPage,
  },
  {
    path: '/admin/opportunities',
    title: 'Manage Opportunities',
    description: 'Jobs and internships posted on the platform.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: Briefcase,
    page: AdminOpportunitiesPage,
  },
  {
    path: '/admin/resources',
    title: 'Manage Learning Resources',
    description: 'Curated courses, videos and articles.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: BookOpen,
    page: ResourcesPage,
  },
  {
    path: '/admin/applications',
    title: 'Manage Applications',
    description: 'View and filter all student applications.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: ClipboardList,
    page: ApplicationsPage,
  },
  {
    path: '/admin/analytics',
    title: 'Analytics',
    description: 'Platform-wide statistics for the hackathon demo.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: BarChart3,
    page: AnalyticsPage,
  },
  {
    path: '/admin/notifications',
    title: 'Notifications',
    description: 'Platform notifications to students.',
    phase: 'Phase 15',
    role: 'ADMIN',
    nav: true,
    icon: Settings,
    page: NotificationsPage,
  },
]

/** All role-scoped routes, ordered for placeholder rendering. */
export const allRoleRoutes: RouteMeta[] = [
  ...studentRoutes,
  ...professorRoutes,
  ...adminRoutes,
]

/** Nav items visible in the sidebar for a given role. */
export function navItems(role: Role): RouteMeta[] {
  return allRoleRoutes.filter((r) => r.nav && r.role === role)
}

export function findByPath(path: string): RouteMeta | undefined {
  return allRoleRoutes.find((r) => r.path === path)
}
