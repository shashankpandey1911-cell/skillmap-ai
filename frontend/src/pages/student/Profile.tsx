import { useMemo, useState } from 'react'
import { Award, ExternalLink, FolderGit2, Pencil, Plus } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { useApi } from '../../hooks/useApi'
import {
  deleteCertification,
  deleteProject,
  listCertifications,
  listProjects,
  me,
  type Certification,
  type Project,
} from '../../api/endpoints/students'
import { Alert, Badge, Button, Card, ConfirmDelete, ProgressBar, Spinner } from '../../components/ui'
import { EditProfileModal } from './profile/EditProfileModal'
import { ProjectFormModal } from './profile/ProjectFormModal'
import { CertificationFormModal } from './profile/CertificationFormModal'

const SECTION_LABELS: Record<string, string> = {
  personal: 'Personal',
  academic: 'Academic',
  career: 'Career',
  projects: 'Projects',
  certifications: 'Certifications',
}

function formatDate(value: string | null): string {
  if (!value) return '—'
  const d = new Date(`${value}T00:00:00`)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })
}

function Field({ label, value }: { label: string; value?: string | number | null }) {
  if (value === undefined || value === null || value === '') return null
  return (
    <div>
      <dt className="text-xs font-medium text-slate-400">{label}</dt>
      <dd className="mt-0.5 text-sm text-slate-800">{value}</dd>
    </div>
  )
}

export function StudentProfilePage() {
  const { user } = useAuth()
  const meQuery = useApi(me)
  const projectsQuery = useApi(listProjects)
  const certsQuery = useApi(listCertifications)

  const [editOpen, setEditOpen] = useState(false)
  const [projectModal, setProjectModal] = useState<{ open: boolean; project: Project | null }>({
    open: false,
    project: null,
  })
  const [certModal, setCertModal] = useState<{ open: boolean; certification: Certification | null }>({
    open: false,
    certification: null,
  })
  const [actionError, setActionError] = useState<string | null>(null)

  const data = meQuery.data
  const projects = projectsQuery.data ?? []
  const certifications = certsQuery.data ?? []

  const initials = useMemo(() => {
    const name = user?.full_name?.trim() || user?.username || '?'
    return name
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? '')
      .join('')
  }, [user])

  const refreshAll = () => {
    meQuery.refresh()
    projectsQuery.refresh()
    certsQuery.refresh()
  }

  const runDelete = async (action: () => Promise<void>) => {
    setActionError(null)
    try {
      await action()
      refreshAll()
    } catch {
      setActionError('Could not delete. Please try again.')
    }
  }

  if (meQuery.loading) return <Spinner />
  if (meQuery.error) return <Alert tone="error">{meQuery.error}</Alert>
  if (!data) return null

  const { profile, completeness } = data
  const sections = completeness.sections

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="px-5 py-5">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-700 text-xl font-semibold text-white">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-semibold text-slate-900">
              {data.user.full_name || data.user.username}
            </h2>
            <p className="truncate text-sm text-slate-500">{data.user.email}</p>
            <div className="mt-1.5 flex flex-wrap items-center gap-2">
              <Badge tone="brand">{data.user.role.toLowerCase()}</Badge>
              {profile.college && <Badge tone="slate">{profile.college}</Badge>}
              {profile.course && <Badge tone="slate">{profile.course}</Badge>}
              {profile.year && <Badge tone="slate">Year {profile.year}</Badge>}
            </div>
          </div>
          <Button onClick={() => setEditOpen(true)}>
            <Pencil className="h-4 w-4" aria-hidden="true" />
            Edit profile
          </Button>
        </div>
      </Card>

      {/* Completion */}
      <Card
        title="Profile completion"
        subtitle="Complete each section to get accurate skill gaps and career matches"
        actions={
          <Badge tone={completeness.overall >= 80 ? 'green' : completeness.overall >= 40 ? 'amber' : 'red'}>
            {completeness.overall}%
          </Badge>
        }
      >
        <ProgressBar value={completeness.overall} />
        <div className="mt-4 grid gap-3 sm:grid-cols-5">
          {Object.entries(sections).map(([key, value]) => (
            <div key={key} className="rounded-lg bg-slate-50 px-3 py-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-slate-600">{SECTION_LABELS[key] ?? key}</span>
                <span className={value >= 100 ? 'font-semibold text-emerald-600' : 'font-semibold text-slate-500'}>
                  {value}%
                </span>
              </div>
              <ProgressBar value={value} tone={value >= 100 ? 'green' : 'brand'} className="mt-1.5 h-1.5" />
            </div>
          ))}
        </div>
      </Card>

      {actionError && <Alert tone="error">{actionError}</Alert>}

      {/* Academic + Career */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Academic" subtitle="Scholastic record">
          <dl className="grid grid-cols-2 gap-x-4 gap-y-4 sm:grid-cols-3">
            <Field label="CGPA" value={profile.cgpa} />
            <Field label="Semester" value={profile.semester} />
            <Field label="Branch" value={profile.branch} />
          </dl>
          {profile.achievements ? (
            <p className="mt-4 text-sm text-slate-600">{profile.achievements}</p>
          ) : (
            <p className="mt-4 text-sm text-slate-400">
              Add achievements like hackathon wins, scholarships or dean's list.
            </p>
          )}
        </Card>

        <Card title="Career" subtitle="Goals and interests">
          <dl className="space-y-4">
            <Field label="Career goal" value={profile.career_goal} />
            <Field label="Preferred domain" value={profile.preferred_domain} />
          </dl>
          {profile.interests ? (
            <p className="mt-4 text-sm text-slate-600">{profile.interests}</p>
          ) : (
            <p className="mt-4 text-sm text-slate-400">
              Tell us what you enjoy working on — it improves your career matches.
            </p>
          )}
        </Card>
      </div>

      {/* Projects */}
      <Card
        title="Projects"
        subtitle="Showcase what you've built"
        actions={
          <Button size="sm" onClick={() => setProjectModal({ open: true, project: null })}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            Add project
          </Button>
        }
      >
        {projectsQuery.loading ? (
          <Spinner />
        ) : projects.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-6 text-center">
            <FolderGit2 className="h-8 w-8 text-slate-300" aria-hidden="true" />
            <p className="text-sm text-slate-500">No projects yet. Add your first project to strengthen your profile.</p>
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {projects.map((project) => (
              <li key={project.id} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-slate-900">{project.name}</p>
                  {project.description && (
                    <p className="mt-0.5 text-sm text-slate-500 line-clamp-2">{project.description}</p>
                  )}
                  {project.technologies && (
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {project.technologies.split(',').map((tech) => (
                        <Badge key={tech} tone="brand">{tech.trim()}</Badge>
                      ))}
                    </div>
                  )}
                  {(project.github_url || project.demo_url) && (
                    <div className="mt-1.5 flex flex-wrap gap-3">
                      {project.github_url && (
                        <a href={project.github_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-brand-700 hover:underline">
                          <ExternalLink className="h-3 w-3" /> GitHub
                        </a>
                      )}
                      {project.demo_url && (
                        <a href={project.demo_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-brand-700 hover:underline">
                          <ExternalLink className="h-3 w-3" /> Live demo
                        </a>
                      )}
                    </div>
                  )}
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  <button
                    type="button"
                    onClick={() => setProjectModal({ open: true, project })}
                    className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                    aria-label={`Edit ${project.name}`}
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <ConfirmDelete onConfirm={() => runDelete(() => deleteProject(project.id))} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {/* Certifications */}
      <Card
        title="Certifications"
        subtitle="Credentials that back up your skills"
        actions={
          <Button size="sm" onClick={() => setCertModal({ open: true, certification: null })}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            Add certification
          </Button>
        }
      >
        {certsQuery.loading ? (
          <Spinner />
        ) : certifications.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-6 text-center">
            <Award className="h-8 w-8 text-slate-300" aria-hidden="true" />
            <p className="text-sm text-slate-500">No certifications yet. Add one to boost your career readiness.</p>
          </div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {certifications.map((cert) => (
              <li key={cert.id} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-slate-900">{cert.name}</p>
                  <p className="mt-0.5 text-sm text-slate-500">
                    {cert.provider && <span>{cert.provider}</span>}
                    {cert.provider && cert.issued_date && <span> · </span>}
                    {formatDate(cert.issued_date)}
                  </p>
                  {cert.credential_url && (
                    <a href={cert.credential_url} target="_blank" rel="noreferrer" className="mt-1 inline-flex items-center gap-1 text-xs text-brand-700 hover:underline">
                      <ExternalLink className="h-3 w-3" /> View credential
                    </a>
                  )}
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  <button
                    type="button"
                    onClick={() => setCertModal({ open: true, certification: cert })}
                    className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                    aria-label={`Edit ${cert.name}`}
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <ConfirmDelete onConfirm={() => runDelete(() => deleteCertification(cert.id))} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {/* Modals — rendered only while open; keys remount them fresh per target. */}
      {editOpen && (
        <EditProfileModal
          key="edit-profile"
          me={data}
          onClose={() => setEditOpen(false)}
          onSaved={() => {
            setEditOpen(false)
            refreshAll()
          }}
        />
      )}
      {projectModal.open && (
        <ProjectFormModal
          key={projectModal.project?.id ?? 'new'}
          project={projectModal.project}
          onClose={() => setProjectModal((m) => ({ ...m, open: false }))}
          onSaved={() => {
            setProjectModal((m) => ({ ...m, open: false }))
            refreshAll()
          }}
        />
      )}
      {certModal.open && (
        <CertificationFormModal
          key={certModal.certification?.id ?? 'new'}
          certification={certModal.certification}
          onClose={() => setCertModal((m) => ({ ...m, open: false }))}
          onSaved={() => {
            setCertModal((m) => ({ ...m, open: false }))
            refreshAll()
          }}
        />
      )}
    </div>
  )
}
