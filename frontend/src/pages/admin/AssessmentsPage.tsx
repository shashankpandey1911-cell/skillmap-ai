import { useState, useEffect } from 'react'
import {
  listAssessments,
  createAssessment,
  updateAssessment,
  deleteAssessment,
  type AdminAssessment,
} from '../../api/endpoints/admin'
import { Alert, Card, Spinner } from '../../components/ui'

const DIFFICULTIES = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']

export function AssessmentsPage() {
  const [assessments, setAssessments] = useState<AdminAssessment[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    title: '', description: '', skill: 0, difficulty: 'INTERMEDIATE', duration_minutes: 10,
  })

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      const res = await listAssessments(params)
      setAssessments(res.results)
      setCount(res.count)
    } catch {
      setError('Failed to load assessments')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search])

  const handleCreate = async () => {
    if (!form.title || !form.skill) return
    try {
      await createAssessment(form)
      setShowCreate(false)
      setForm({ title: '', description: '', skill: 0, difficulty: 'INTERMEDIATE', duration_minutes: 10 })
      load()
    } catch {
      setError('Failed to create assessment')
    }
  }

  const togglePublish = async (a: AdminAssessment) => {
    try {
      await updateAssessment(a.id, { is_published: !a.is_published })
      load()
    } catch {
      setError('Failed to update assessment')
    }
  }

  const handleDelete = async (a: AdminAssessment) => {
    if (!confirm(`Delete assessment "${a.title}"?`)) return
    try {
      await deleteAssessment(a.id)
      load()
    } catch {
      setError('Failed to delete assessment')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Manage Assessments</h2>
          <p className="text-sm text-gray-500 mt-1">{count} assessments</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          + Add Assessment
        </button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <Card>
        <input type="text" placeholder="Search assessments..."
          value={search} onChange={(e) => setSearch(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500" />
      </Card>

      {loading ? <Spinner /> : (
        <div className="space-y-3">
          {assessments.map((a) => (
            <Card key={a.id}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium text-slate-900">{a.title}</h3>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{a.skill_name}</span>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{a.difficulty}</span>
                  </div>
                  <div className="flex gap-4 mt-2 text-xs text-gray-400">
                    <span>⏱ {a.duration_minutes} min</span>
                    <span>❓ {a.question_count} questions</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button onClick={() => togglePublish(a)}
                    className={`px-2 py-1 rounded text-xs font-medium
                      ${a.is_published ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {a.is_published ? 'Published' : 'Draft'}
                  </button>
                  <button onClick={() => handleDelete(a)} className="text-red-400 hover:text-red-600 text-xs">Delete</button>
                </div>
              </div>
            </Card>
          ))}
          {assessments.length === 0 && (
            <p className="text-center text-gray-400 py-8">No assessments found</p>
          )}
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Add Assessment</h3>
            <input type="text" placeholder="Title *" value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            <textarea placeholder="Description" value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" rows={2} />
            <input type="number" placeholder="Skill ID *" value={form.skill || ''}
              onChange={(e) => setForm({ ...form, skill: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            <div className="grid grid-cols-2 gap-3">
              <select value={form.difficulty}
                onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
              <input type="number" placeholder="Duration (min)" value={form.duration_minutes}
                onChange={(e) => setForm({ ...form, duration_minutes: Number(e.target.value) })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-gray-600">Cancel</button>
              <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium">Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
