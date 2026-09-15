import { useState, useEffect } from 'react'
import {
  listUsers,
  createUser,
  updateUser,
  deleteUser,
  changeUserPassword,
  type AdminUser,
} from '../../api/endpoints/admin'
import { Alert, Card, Input, Spinner, useToast } from '../../components/ui'

const ROLES = ['STUDENT', 'PROFESSOR', 'ADMIN']

export function UsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [changePasswordUser, setChangePasswordUser] = useState<AdminUser | null>(null)
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'STUDENT',
    phone: '',
  })
  const [pwForm, setPwForm] = useState({ new_password: '', confirm_password: '' })
  const [creating, setCreating] = useState(false)
  const [changingPw, setChangingPw] = useState(false)
  const { toast } = useToast()

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const params: Record<string, string> = {}
      if (search) params.search = search
      if (roleFilter) params.role = roleFilter
      const res = await listUsers(params)
      setUsers(res.results)
      setCount(res.count)
    } catch {
      setError('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [search, roleFilter])

  const handleCreate = async () => {
    if (!form.full_name || !form.email || !form.password) return
    setCreating(true)
    try {
      await createUser(form)
      setShowCreate(false)
      setForm({ full_name: '', email: '', password: '', role: 'STUDENT', phone: '' })
      toast('success', 'User created successfully')
      load()
    } catch {
      setError('Failed to create user')
    } finally {
      setCreating(false)
    }
  }

  const toggleActive = async (user: AdminUser) => {
    try {
      await updateUser(user.id, { is_active: !user.is_active })
      toast('success', `User ${user.is_active ? 'deactivated' : 'activated'}`)
      load()
    } catch {
      setError('Failed to update user')
    }
  }

  const changeRole = async (user: AdminUser, newRole: string) => {
    try {
      await updateUser(user.id, { role: newRole })
      toast('success', 'Role updated')
      load()
    } catch {
      setError('Failed to change role')
    }
  }

  const handleDelete = async (user: AdminUser) => {
    if (!confirm(`Delete ${user.email}? This cannot be undone.`)) return
    try {
      await deleteUser(user.id)
      toast('success', 'User deleted')
      load()
    } catch {
      setError('Failed to delete user')
    }
  }

  const openChangePassword = (user: AdminUser) => {
    setChangePasswordUser(user)
    setShowChangePassword(true)
  }

  const handleChangePassword = async () => {
    if (!changePasswordUser) return
    if (!pwForm.new_password || !pwForm.confirm_password) {
      toast('error', 'Both password fields are required')
      return
    }
    if (pwForm.new_password !== pwForm.confirm_password) {
      toast('error', 'The two password fields do not match')
      return
    }
    if (pwForm.new_password.length < 8) {
      toast('error', 'Password must be at least 8 characters')
      return
    }
    setChangingPw(true)
    try {
      await changeUserPassword(changePasswordUser.id, {
        new_password: pwForm.new_password,
        confirm_password: pwForm.confirm_password,
      })
      toast('success', `Password updated for ${changePasswordUser.email}`)
      setShowChangePassword(false)
      setPwForm({ new_password: '', confirm_password: '' })
      load()
    } catch (err: any) {
      const msg = err?.response?.data?.new_password
        || err?.response?.data?.confirm_password
        || err?.response?.data?.detail
        || 'Failed to change password'
      toast('error', typeof msg === 'string' ? msg : 'Failed to change password')
    } finally {
      setChangingPw(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header + Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Manage Users</h2>
          <p className="text-sm text-gray-500 mt-1">{count} total users</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          + Add User
        </button>
      </div>

      {error && <Alert tone="error">{error}</Alert>}

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-3">
          <input
            type="text"
            placeholder="Search by name, email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Roles</option>
            {ROLES.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </Card>

      {/* Users Table */}
      {loading ? (
        <Spinner />
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-medium text-gray-500">User</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Role</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-500">Joined</th>
                  <th className="text-right py-3 px-4 font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div>
                        <p className="font-medium text-slate-900">{u.full_name}</p>
                        <p className="text-xs text-gray-500">{u.email}</p>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <select
                        value={u.role}
                        onChange={(e) => changeRole(u, e.target.value)}
                        className="text-xs border border-gray-200 rounded px-2 py-1"
                      >
                        {ROLES.map((r) => (
                          <option key={r} value={r}>{r}</option>
                        ))}
                      </select>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => toggleActive(u)}
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium cursor-pointer
                          ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}
                      >
                        {u.is_active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td className="py-3 px-4 text-gray-500 text-xs">
                      {new Date(u.date_joined).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openChangePassword(u)}
                          className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                        >
                          Change Password
                        </button>
                        <button
                          onClick={() => handleDelete(u)}
                          className="text-red-500 hover:text-red-700 text-xs font-medium"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-gray-400">No users found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Create User Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Create User</h3>
            <input
              type="text"
              placeholder="Full Name"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <input
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <input
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Phone (optional)"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={creating}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {creating ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Change Password Modal */}
      {showChangePassword && changePasswordUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">
              Change Password
            </h3>
            <p className="text-sm text-gray-500">
              User: {changePasswordUser.full_name} ({changePasswordUser.email})
            </p>

            <Input
              label="New Password"
              type="password"
              placeholder="Enter new password"
              value={pwForm.new_password}
              onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
              autoComplete="new-password"
            />
            <Input
              label="Confirm New Password"
              type="password"
              placeholder="Confirm new password"
              value={pwForm.confirm_password}
              onChange={(e) => setPwForm({ ...pwForm, confirm_password: e.target.value })}
              autoComplete="new-password"
            />

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowChangePassword(false)
                  setPwForm({ new_password: '', confirm_password: '' })
                }}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
              >
                Cancel
              </button>
              <button
                onClick={handleChangePassword}
                disabled={changingPw}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {changingPw ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
