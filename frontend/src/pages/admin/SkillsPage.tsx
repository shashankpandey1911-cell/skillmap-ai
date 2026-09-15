import { useState, useEffect } from 'react'
import {
  listSkills,
  createSkill,
  updateSkill,
  deleteSkill,
  type AdminSkill,
} from '../../api/endpoints/admin'
import { Alert, Card, Spinner } from '../../components/ui'

const CATEGORIES = [
  'Programming', 'Web Development', 'Database', 'Cloud',
  'AI/ML', 'Data Science', 'Tools', 'Soft Skills', 'Other',
]

export function SkillsPage() {
  const [skills, setSkills] = useState<AdminSkill[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', category: 'Programming', description: '' })

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (catFilter) params.category = catFilter
      const res = await listSkills(params)
      setSkills(res.results)
      setCount(res.count)
    } catch {
      setError('Failed to load skills')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search, catFilter])

  const handleCreate = async () => {
    if (!form.name) return
    try {
      await createSkill(form)
      setShowCreate(false)
      setForm({ name: '', category: 'Programming', description: '' })
      load()
    } catch {
      setError('Failed to create skill')
    }
  }

  const toggleActive = async (skill: AdminSkill) => {
    try {
      await updateSkill(skill.id, { is_active: !skill.is_active })
      load()
    } catch {
      setError('Failed to update skill')
    }
  }

  const handleDelete = async (skill: AdminSkill) => {
    if (!confirm(`Delete skill "${skill.name}"?`)) return
    try {
      await deleteSkill(skill.id)
      load()
    } catch {
      setError('Failed to delete skill')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Manage Skills</h2>
          <p className="text-sm text-gray-500 mt-1">{count} skills in catalog</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          + Add Skill
        </button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <Card>
        <div className="flex flex-wrap gap-3">
          <input
            type="text"
            placeholder="Search skills..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={catFilter}
            onChange={(e) => setCatFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </Card>

      {loading ? (
        <Spinner />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {skills.map((s) => (
            <Card key={s.id}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-slate-900">{s.name}</h3>
                  <p className="text-xs text-gray-500 mt-1">{s.category}</p>
                  <p className="text-xs text-gray-400 mt-1">{s.user_count} students</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleActive(s)}
                    className={`px-2 py-1 rounded text-xs font-medium
                      ${s.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}
                  >
                    {s.is_active ? 'Active' : 'Off'}
                  </button>
                  <button
                    onClick={() => handleDelete(s)}
                    className="text-red-400 hover:text-red-600 text-xs"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </Card>
          ))}
          {skills.length === 0 && (
            <p className="col-span-full text-center text-gray-400 py-8">No skills found</p>
          )}
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Add Skill</h3>
            <input
              type="text"
              placeholder="Skill name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            <textarea
              placeholder="Description (optional)"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              rows={2}
            />
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-gray-600">Cancel</button>
              <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium">Add</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
