import { useState, useEffect } from 'react'
import {
  listCareers,
  createCareer,
  updateCareer,
  deleteCareer,
  type AdminCareer,
} from '../../api/endpoints/admin'
import { Alert, Card, Spinner } from '../../components/ui'

export function CareersPage() {
  const [careers, setCareers] = useState<AdminCareer[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    title: '', description: '', category: '', education: '',
    outlook: '', salary_range: '', domain_keywords: '', learning_areas: '',
  })

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      const res = await listCareers(params)
      setCareers(res.results)
      setCount(res.count)
    } catch {
      setError('Failed to load careers')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search])

  const handleCreate = async () => {
    if (!form.title) return
    try {
      await createCareer(form)
      setShowCreate(false)
      setForm({ title: '', description: '', category: '', education: '', outlook: '', salary_range: '', domain_keywords: '', learning_areas: '' })
      load()
    } catch {
      setError('Failed to create career')
    }
  }

  const toggleActive = async (c: AdminCareer) => {
    try {
      await updateCareer(c.id, { is_active: !c.is_active })
      load()
    } catch {
      setError('Failed to update career')
    }
  }

  const handleDelete = async (c: AdminCareer) => {
    if (!confirm(`Delete career "${c.title}"?`)) return
    try {
      await deleteCareer(c.id)
      load()
    } catch {
      setError('Failed to delete career')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Manage Careers</h2>
          <p className="text-sm text-gray-500 mt-1">{count} career paths</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          + Add Career
        </button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <Card>
        <input
          type="text"
          placeholder="Search careers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
        />
      </Card>

      {loading ? (
        <Spinner />
      ) : (
        <div className="space-y-3">
          {careers.map((c) => (
            <Card key={c.id}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium text-slate-900">{c.title}</h3>
                    <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">{c.category}</span>
                  </div>
                  {c.description && (
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{c.description}</p>
                  )}
                  <div className="flex gap-4 mt-2 text-xs text-gray-400">
                    {c.salary_range && <span>💰 {c.salary_range}</span>}
                    {c.education && <span>🎓 {c.education}</span>}
                    {c.requirements && <span>📊 {c.requirements.length} skills required</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => toggleActive(c)}
                    className={`px-2 py-1 rounded text-xs font-medium
                      ${c.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}
                  >
                    {c.is_active ? 'Active' : 'Off'}
                  </button>
                  <button
                    onClick={() => handleDelete(c)}
                    className="text-red-400 hover:text-red-600 text-xs"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </Card>
          ))}
          {careers.length === 0 && (
            <p className="text-center text-gray-400 py-8">No careers found</p>
          )}
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-slate-900">Add Career</h3>
            <input type="text" placeholder="Title *" value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            <textarea placeholder="Description" value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" rows={3} />
            <div className="grid grid-cols-2 gap-3">
              <input type="text" placeholder="Category" value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <input type="text" placeholder="Education" value={form.education}
                onChange={(e) => setForm({ ...form, education: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <input type="text" placeholder="Salary Range" value={form.salary_range}
                onChange={(e) => setForm({ ...form, salary_range: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <input type="text" placeholder="Domain Keywords" value={form.domain_keywords}
                onChange={(e) => setForm({ ...form, domain_keywords: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
            <textarea placeholder="Outlook" value={form.outlook}
              onChange={(e) => setForm({ ...form, outlook: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" rows={2} />
            <textarea placeholder="Learning Areas (comma-separated)" value={form.learning_areas}
              onChange={(e) => setForm({ ...form, learning_areas: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" rows={2} />
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
