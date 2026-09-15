import { useState, useEffect } from 'react'
import {
  listOpportunities,
  createOpportunity,
  updateOpportunity,
  deleteOpportunity,
  type AdminOpportunity,
} from '../../api/endpoints/admin'
import { Alert, Card, Spinner } from '../../components/ui'

const TYPES = ['JOB', 'INTERNSHIP', 'HACKATHON', 'COMPETITION']
const STATUSES = ['ACTIVE', 'DRAFT', 'CLOSED']

export function OpportunitiesPage() {
  const [opps, setOpps] = useState<AdminOpportunity[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    title: '', company: '', opportunity_type: 'JOB', description: '',
    eligibility: '', location: '', is_remote: false, deadline: '',
    application_link: '', compensation: '', status: 'DRAFT',
  })

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (typeFilter) params.type = typeFilter
      if (statusFilter) params.status = statusFilter
      const res = await listOpportunities(params)
      setOpps(res.results)
      setCount(res.count)
    } catch {
      setError('Failed to load opportunities')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search, typeFilter, statusFilter])

  const handleCreate = async () => {
    if (!form.title || !form.company) return
    try {
      await createOpportunity(form)
      setShowCreate(false)
      setForm({
        title: '', company: '', opportunity_type: 'JOB', description: '',
        eligibility: '', location: '', is_remote: false, deadline: '',
        application_link: '', compensation: '', status: 'DRAFT',
      })
      load()
    } catch {
      setError('Failed to create opportunity')
    }
  }

  const handleDelete = async (opp: AdminOpportunity) => {
    if (!confirm(`Delete "${opp.title}"?`)) return
    try {
      await deleteOpportunity(opp.id)
      load()
    } catch {
      setError('Failed to delete opportunity')
    }
  }

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      ACTIVE: 'bg-green-100 text-green-700',
      DRAFT: 'bg-yellow-100 text-yellow-700',
      CLOSED: 'bg-red-100 text-red-700',
    }
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] ?? 'bg-gray-100 text-gray-700'}`}>
        {status}
      </span>
    )
  }

  const typeBadge = (type: string) => {
    const colors: Record<string, string> = {
      JOB: 'bg-blue-100 text-blue-700',
      INTERNSHIP: 'bg-purple-100 text-purple-700',
      HACKATHON: 'bg-amber-100 text-amber-700',
      COMPETITION: 'bg-pink-100 text-pink-700',
    }
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[type] ?? 'bg-gray-100 text-gray-700'}`}>
        {type}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Manage Opportunities</h2>
          <p className="text-sm text-gray-500 mt-1">{count} total postings</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          + Add Opportunity
        </button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <Card>
        <div className="flex flex-wrap gap-3">
          <input
            type="text"
            placeholder="Search by title, company..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
          />
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="">All Types</option>
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="">All Statuses</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </Card>

      {loading ? (
        <Spinner />
      ) : (
        <div className="space-y-3">
          {opps.map((o) => (
            <Card key={o.id}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-medium text-slate-900">{o.title}</h3>
                    {typeBadge(o.opportunity_type)}
                    {statusBadge(o.status)}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{o.company}</p>
                  <div className="flex gap-4 mt-2 text-xs text-gray-400">
                    {o.location && <span>📍 {o.location}</span>}
                    {o.deadline && <span>📅 {o.deadline}</span>}
                    {o.compensation && <span>💰 {o.compensation}</span>}
                    {o.application_count > 0 && <span>📝 {o.application_count} applications</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => updateOpportunity(o.id, { status: o.status === 'ACTIVE' ? 'DRAFT' : 'ACTIVE' }).then(load)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    {o.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => handleDelete(o)}
                    className="text-red-400 hover:text-red-600 text-xs"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </Card>
          ))}
          {opps.length === 0 && (
            <p className="text-center text-gray-400 py-8">No opportunities found</p>
          )}
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-slate-900">Add Opportunity</h3>
            <div className="grid grid-cols-2 gap-3">
              <input type="text" placeholder="Title *" value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <input type="text" placeholder="Company *" value={form.company}
                onChange={(e) => setForm({ ...form, company: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <select value={form.opportunity_type}
                onChange={(e) => setForm({ ...form, opportunity_type: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
              <select value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
              <input type="text" placeholder="Location" value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <input type="date" placeholder="Deadline" value={form.deadline}
                onChange={(e) => setForm({ ...form, deadline: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <input type="text" placeholder="Compensation" value={form.compensation}
                onChange={(e) => setForm({ ...form, compensation: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
              <input type="url" placeholder="Application Link" value={form.application_link}
                onChange={(e) => setForm({ ...form, application_link: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input type="checkbox" checked={form.is_remote}
                onChange={(e) => setForm({ ...form, is_remote: e.target.checked })}
                className="rounded" />
              Remote available
            </label>
            <textarea placeholder="Description" value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" rows={3} />
            <textarea placeholder="Eligibility" value={form.eligibility}
              onChange={(e) => setForm({ ...form, eligibility: e.target.value })}
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
