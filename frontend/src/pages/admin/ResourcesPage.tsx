import { useState, useEffect } from 'react'
import {
  listResources,
  createResource,
  deleteResource,
  type AdminLearningResource,
} from '../../api/endpoints/admin'
import { Alert, Card, Spinner } from '../../components/ui'

const TYPES = ['COURSE', 'VIDEO', 'DOCUMENTATION', 'PRACTICE', 'PROJECT', 'QUIZ']
const LEVELS = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED']

export function ResourcesPage() {
  const [resources, setResources] = useState<AdminLearningResource[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    title: '', description: '', skill: 0, level: 'INTERMEDIATE',
    type: 'COURSE', url: '', estimated_duration_minutes: 30,
  })

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (typeFilter) params.type = typeFilter
      const res = await listResources(params)
      setResources(res.results)
      setCount(res.count)
    } catch {
      setError('Failed to load resources')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search, typeFilter])

  const handleCreate = async () => {
    if (!form.title || !form.skill) return
    try {
      await createResource(form)
      setShowCreate(false)
      setForm({ title: '', description: '', skill: 0, level: 'INTERMEDIATE', type: 'COURSE', url: '', estimated_duration_minutes: 30 })
      load()
    } catch {
      setError('Failed to create resource')
    }
  }

  const handleDelete = async (r: AdminLearningResource) => {
    if (!confirm(`Delete resource "${r.title}"?`)) return
    try {
      await deleteResource(r.id)
      load()
    } catch {
      setError('Failed to delete resource')
    }
  }

  const typeIcon: Record<string, string> = {
    COURSE: '📚', VIDEO: '🎬', DOCUMENTATION: '📄', PRACTICE: '✏️', PROJECT: '🛠', QUIZ: '❓',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Manage Learning Resources</h2>
          <p className="text-sm text-gray-500 mt-1">{count} resources</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          + Add Resource
        </button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <Card>
        <div className="flex flex-wrap gap-3">
          <input type="text" placeholder="Search resources..."
            value={search} onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500" />
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="">All Types</option>
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </Card>

      {loading ? <Spinner /> : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {resources.map((r) => (
            <Card key={r.id}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span>{typeIcon[r.type] ?? '📄'}</span>
                    <h3 className="font-medium text-slate-900 text-sm">{r.title}</h3>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{r.skill_name} · {r.level}</p>
                  <p className="text-xs text-gray-400 mt-1">⏱ {r.estimated_duration_minutes} min</p>
                  {r.url && (
                    <a href={r.url} target="_blank" rel="noopener noreferrer"
                      className="text-xs text-blue-500 hover:underline mt-1 block truncate">
                      {r.url}
                    </a>
                  )}
                </div>
                <button onClick={() => handleDelete(r)} className="text-red-400 hover:text-red-600 text-xs ml-2">✕</button>
              </div>
            </Card>
          ))}
          {resources.length === 0 && (
            <p className="col-span-full text-center text-gray-400 py-8">No resources found</p>
          )}
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Add Resource</h3>
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
              <select value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              <select value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <input type="url" placeholder="URL" value={form.url}
              onChange={(e) => setForm({ ...form, url: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            <input type="number" placeholder="Duration (minutes)" value={form.estimated_duration_minutes}
              onChange={(e) => setForm({ ...form, estimated_duration_minutes: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
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
