import { useState, useEffect } from 'react'
import { listApplications, type AdminApplication } from '../../api/endpoints/admin'
import { Alert, Card, Spinner } from '../../components/ui'

const STATUSES = ['APPLIED', 'SUBMITTED', 'UNDER_REVIEW', 'SHORTLISTED', 'INTERVIEW', 'SELECTED', 'REJECTED']

export function ApplicationsPage() {
  const [apps, setApps] = useState<AdminApplication[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const res = await listApplications(params)
      setApps(res)
    } catch {
      setError('Failed to load applications')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search, statusFilter])

  const statusBadge = (status: string) => {
    const colors: Record<string, string> = {
      APPLIED: 'bg-blue-100 text-blue-700',
      SUBMITTED: 'bg-indigo-100 text-indigo-700',
      UNDER_REVIEW: 'bg-yellow-100 text-yellow-700',
      SHORTLISTED: 'bg-purple-100 text-purple-700',
      INTERVIEW: 'bg-orange-100 text-orange-700',
      SELECTED: 'bg-green-100 text-green-700',
      REJECTED: 'bg-red-100 text-red-700',
    }
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status] ?? 'bg-gray-100 text-gray-700'}`}>
        {status.replace('_', ' ')}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Manage Applications</h2>
        <p className="text-sm text-gray-500 mt-1">{apps.length} applications</p>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      <Card>
        <div className="flex flex-wrap gap-3">
          <input type="text" placeholder="Search by student, opportunity..."
            value={search} onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500" />
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="">All Statuses</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
          </select>
        </div>
      </Card>

      {loading ? <Spinner /> : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Student</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Opportunity</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Applied</th>
                </tr>
              </thead>
              <tbody>
                {apps.map((a) => (
                  <tr key={a.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <p className="font-medium text-slate-900">{a.student_name}</p>
                      <p className="text-xs text-gray-500">{a.student_email}</p>
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-medium text-slate-700">{a.opportunity_title}</p>
                      <p className="text-xs text-gray-500">{a.opportunity_company}</p>
                    </td>
                    <td className="py-3 px-4">{statusBadge(a.status)}</td>
                    <td className="py-3 px-4 text-xs text-gray-500">
                      {new Date(a.applied_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
                {apps.length === 0 && (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-gray-400">No applications found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
