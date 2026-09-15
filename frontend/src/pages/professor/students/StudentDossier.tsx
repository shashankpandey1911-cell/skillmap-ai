import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, Target, BookOpen, Briefcase, FileText,
  Plus, Trash2, AlertTriangle
} from 'lucide-react'
import {
  getStudentDossier,
  getGuidanceNotes,
  addGuidanceNote,
  deleteGuidanceNote,
  type StudentDossier as DossierType,
  type GuidanceNote
} from '../../../api/endpoints/professors'
import { Card, Spinner, Badge, Button, ProgressBar } from '../../../components/ui'

const GAP_COLORS: Record<string, string> = {
  HIGH: 'red',
  MEDIUM: 'amber',
  LOW: 'blue',
  NONE: 'green',
}

const STATUS_COLORS: Record<string, string> = {
  APPLIED: 'blue',
  SUBMITTED: 'indigo',
  UNDER_REVIEW: 'amber',
  SHORTLISTED: 'green',
  INTERVIEW: 'purple',
  SELECTED: 'emerald',
  REJECTED: 'red',
}

export function StudentDossierPage() {
  const { id } = useParams<{ id: string }>()
  const [dossier, setDossier] = useState<DossierType | null>(null)
  const [guidance, setGuidance] = useState<GuidanceNote[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'gaps' | 'applications' | 'guidance'>('overview')
  const [guidanceForm, setGuidanceForm] = useState({ title: '', message: '', category: 'GENERAL' })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!id) return
    const fetchData = async () => {
      setLoading(true)
      try {
        const [d, g] = await Promise.all([
          getStudentDossier(Number(id)),
          getGuidanceNotes(Number(id))
        ])
        setDossier(d)
        setGuidance(g)
      } catch (err: any) {
        setError(err.message || 'Failed to load dossier')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleAddGuidance = async () => {
    if (!id || !guidanceForm.title || !guidanceForm.message) return
    setSubmitting(true)
    try {
      const note = await addGuidanceNote(Number(id), guidanceForm)
      setGuidance([note, ...guidance])
      setGuidanceForm({ title: '', message: '', category: 'GENERAL' })
    } catch (err: any) {
      alert(err.message || 'Failed to add guidance')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteGuidance = async (noteId: number) => {
    if (!confirm('Delete this guidance note?')) return
    try {
      await deleteGuidanceNote(noteId)
      setGuidance(guidance.filter(n => n.id !== noteId))
    } catch (err: any) {
      alert(err.message || 'Failed to delete')
    }
  }

  if (loading) return <Spinner />
  if (error) return <div className="text-red-600">{error}</div>
  if (!dossier) return <div className="text-slate-500">Student not found</div>

  const tabs = [
    { key: 'overview', label: 'Overview', icon: Target },
    { key: 'skills', label: 'Skills', icon: BookOpen },
    { key: 'gaps', label: 'Skill Gaps', icon: AlertTriangle },
    { key: 'applications', label: 'Applications', icon: Briefcase },
    { key: 'guidance', label: 'Guidance', icon: FileText },
  ] as const

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/professor/students" className="text-slate-500 hover:text-slate-700">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h2 className="text-xl font-semibold text-slate-900">{dossier.full_name}</h2>
          <p className="text-sm text-slate-500">{dossier.email}</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Badge tone={dossier.career_readiness >= 70 ? 'green' : dossier.career_readiness >= 40 ? 'amber' : 'red'}>
            Career Readiness: {dossier.career_readiness}%
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Profile */}
          <Card title="Profile">
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">College</span>
                <span className="text-slate-900">{dossier.profile.college || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Course</span>
                <span className="text-slate-900">{dossier.profile.course || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Branch</span>
                <span className="text-slate-900">{dossier.profile.branch || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Year</span>
                <span className="text-slate-900">{dossier.profile.year || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">CGPA</span>
                <span className="text-slate-900">{dossier.profile.cgpa || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Career Goal</span>
                <span className="text-slate-900 text-right max-w-[60%]">{dossier.profile.career_goal || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Interests</span>
                <span className="text-slate-900 text-right max-w-[60%]">{dossier.profile.interests || '—'}</span>
              </div>
            </div>
            <div className="mt-4">
              <p className="text-sm text-slate-500 mb-2">Profile Completeness</p>
              <ProgressBar value={dossier.profile.completeness} />
            </div>
          </Card>

          {/* Career Readiness */}
          <Card title="Career Readiness">
            <div className="flex items-center justify-center py-6">
              <div className="relative w-32 h-32">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#e2e8f0" strokeWidth="8" />
                  <circle
                    cx="50" cy="50" r="40" fill="none"
                    stroke={dossier.career_readiness >= 70 ? '#22c55e' : dossier.career_readiness >= 40 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="8"
                    strokeDasharray={`${dossier.career_readiness * 2.51} 251`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-slate-900">{dossier.career_readiness}%</span>
                </div>
              </div>
            </div>
            <p className="text-center text-sm text-slate-500">
              {dossier.career_readiness >= 70
                ? 'This student is well-prepared for their target career.'
                : 'This student has gaps to address before being career-ready.'}
            </p>
          </Card>

          {/* Projects */}
          <Card title="Projects">
            {dossier.projects.length > 0 ? (
              <div className="space-y-3">
                {dossier.projects.map((p, i) => (
                  <div key={i} className="p-3 bg-slate-50 rounded-lg">
                    <h4 className="font-medium text-slate-900">{p.name}</h4>
                    <p className="text-sm text-slate-600 mt-1">{p.description}</p>
                    <p className="text-xs text-slate-500 mt-2">{p.technologies}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 text-center py-4">No projects added yet</p>
            )}
          </Card>

          {/* Certifications */}
          <Card title="Certifications">
            {dossier.certifications.length > 0 ? (
              <div className="space-y-3">
                {dossier.certifications.map((c, i) => (
                  <div key={i} className="p-3 bg-slate-50 rounded-lg">
                    <h4 className="font-medium text-slate-900">{c.name}</h4>
                    <p className="text-sm text-slate-600">{c.provider}</p>
                    {c.issued_date && (
                      <p className="text-xs text-slate-500 mt-1">
                        Issued: {new Date(c.issued_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 text-center py-4">No certifications added yet</p>
            )}
          </Card>
        </div>
      )}

      {activeTab === 'skills' && (
        <Card title="Skills">
          {dossier.skills.length > 0 ? (
            <div className="space-y-3">
              {dossier.skills.map((skill, i) => (
                <div key={i} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-slate-900">{skill.name}</h4>
                      <Badge tone="slate">{skill.category}</Badge>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{skill.experience_level}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-slate-900">{skill.proficiency_percent}%</p>
                    {skill.assessment_score !== null && (
                      <p className="text-xs text-slate-500">Assessment: {skill.assessment_score}%</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 text-center py-8">No skills added yet</p>
          )}
        </Card>
      )}

      {activeTab === 'gaps' && (
        <Card title="Skill Gaps">
          {dossier.skill_gaps.length > 0 ? (
            <div className="space-y-3">
              {dossier.skill_gaps.map((gap, i) => (
                <div key={i} className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-slate-900">{gap.skill_name}</h4>
                      <p className="text-xs text-slate-500">{gap.category}</p>
                    </div>
                    <Badge tone={GAP_COLORS[gap.gap_class] as any}>
                      {gap.gap_class} · {gap.gap_percentage}% gap
                    </Badge>
                  </div>
                  <div className="mt-3 flex items-center gap-4 text-sm">
                    <span className="text-slate-500">
                      Current: <span className="font-medium text-slate-900">{gap.current_level}%</span>
                    </span>
                    <span className="text-slate-500">
                      Required: <span className="font-medium text-slate-900">{gap.required_level}%</span>
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{gap.recommended_action}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Target className="h-12 w-12 mx-auto text-emerald-500" />
              <p className="mt-2 text-slate-500">No skill gaps — this student meets all requirements!</p>
            </div>
          )}
        </Card>
      )}

      {activeTab === 'applications' && (
        <Card title="Applications">
          {dossier.applications.length > 0 ? (
            <div className="space-y-3">
              {dossier.applications.map((app, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-slate-900">{app.opportunity_title}</h4>
                    <p className="text-sm text-slate-500">{app.company}</p>
                  </div>
                  <div className="text-right">
                    <Badge tone={STATUS_COLORS[app.status] as any}>{app.status.replace('_', ' ')}</Badge>
                    <p className="text-xs text-slate-500 mt-1">
                      Applied: {new Date(app.applied_at).toLocaleDateString()}
                    </p>
                    {app.interview_date && (
                      <p className="text-xs text-amber-600 mt-1">
                        Interview: {new Date(app.interview_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 text-center py-8">No applications yet</p>
          )}
        </Card>
      )}

      {activeTab === 'guidance' && (
        <div className="space-y-6">
          {/* Add Guidance Form */}
          <Card title="Add Guidance Note">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
                <input
                  type="text"
                  value={guidanceForm.title}
                  onChange={(e) => setGuidanceForm({ ...guidanceForm, title: e.target.value })}
                  placeholder="e.g., Focus on DSA practice"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Message</label>
                <textarea
                  value={guidanceForm.message}
                  onChange={(e) => setGuidanceForm({ ...guidanceForm, message: e.target.value })}
                  placeholder="Provide detailed guidance for the student..."
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Category</label>
                <select
                  value={guidanceForm.category}
                  onChange={(e) => setGuidanceForm({ ...guidanceForm, category: e.target.value })}
                  className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-500"
                >
                  <option value="GENERAL">General</option>
                  <option value="ACADEMIC">Academic</option>
                  <option value="CAREER">Career</option>
                  <option value="SKILL">Skill Development</option>
                </select>
              </div>
              <Button
                onClick={handleAddGuidance}
                disabled={!guidanceForm.title || !guidanceForm.message || submitting}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Guidance
              </Button>
            </div>
          </Card>

          {/* Guidance Notes List */}
          <Card title="Guidance Notes">
            {guidance.length > 0 ? (
              <div className="space-y-3">
                {guidance.map((note) => (
                  <div key={note.id} className="p-4 border border-slate-200 rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-slate-900">{note.title}</h4>
                        <p className="text-sm text-slate-600 mt-1">{note.message}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge tone="slate">{note.category}</Badge>
                          <span className="text-xs text-slate-500">
                            by {note.professor_name} · {new Date(note.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteGuidance(note.id)}
                        className="text-slate-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 text-center py-8">No guidance notes yet</p>
            )}
          </Card>
        </div>
      )}
    </div>
  )
}
