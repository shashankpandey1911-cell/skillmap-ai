import { useState } from 'react'
import { sendNotification } from '../../api/endpoints/admin'
import { Alert, Card } from '../../components/ui'

const TARGETS = [
  { value: 'all', label: 'All Users' },
  { value: 'students', label: 'Students Only' },
  { value: 'professors', label: 'Professors Only' },
]

export function NotificationsPage() {
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [target, setTarget] = useState('all')
  const [sending, setSending] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  const handleSend = async () => {
    if (!title.trim() || !body.trim()) {
      setError('Title and body are required')
      return
    }
    setSending(true)
    setError('')
    setSuccess('')
    try {
      const res = await sendNotification({ title, body, target })
      setSuccess(res.detail)
      setTitle('')
      setBody('')
      setTarget('all')
    } catch {
      setError('Failed to send notification')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Send Notification</h2>
        <p className="text-sm text-gray-500 mt-1">Broadcast a notification to platform users</p>
      </div>

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <Card>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target Audience</label>
            <div className="flex gap-3">
              {TARGETS.map((t) => (
                <button
                  key={t.value}
                  onClick={() => setTarget(t.value)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
                    ${target === t.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input
              type="text"
              placeholder="Notification title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Message *</label>
            <textarea
              placeholder="Write your notification message here..."
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
              rows={5}
            />
          </div>

          <button
            onClick={handleSend}
            disabled={sending || !title.trim() || !body.trim()}
            className="w-full px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {sending ? 'Sending...' : 'Send Notification'}
          </button>
        </div>
      </Card>
    </div>
  )
}
