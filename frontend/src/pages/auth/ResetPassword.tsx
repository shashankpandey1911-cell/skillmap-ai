import { useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Alert, Button, Card, Input } from '../../components/ui'
import { resetPassword } from '../../api/endpoints/auth'
import { extractApiError } from '../../utils/errors'

export function ResetPassword() {
  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') ?? ''
  const token = searchParams.get('token') ?? ''

  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [done, setDone] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }
    setSubmitting(true)
    try {
      await resetPassword(uid, token, password)
      setDone(true)
    } catch (err) {
      setError(extractApiError(err, 'The reset link is invalid or has expired.'))
    } finally {
      setSubmitting(false)
    }
  }

  if (!uid || !token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
        <Card className="w-full max-w-md">
          <Alert tone="error">This reset link is incomplete or has expired.</Alert>
          <p className="mt-6 text-center text-sm text-slate-500">
            <Link to="/auth/forgot-password" className="font-medium text-brand-700 hover:underline">
              Request a new link
            </Link>
          </p>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-xl font-semibold text-slate-900">Choose a new password</h1>
          <p className="mt-1 text-sm text-slate-500">Use at least 8 characters.</p>
        </div>

        {done ? (
          <>
            <Alert tone="success">Your password has been reset. You can now sign in.</Alert>
            <Link to="/auth/login" className="mt-5 block">
              <Button className="w-full">Go to sign in</Button>
            </Link>
          </>
        ) : (
          <>
            {error && <Alert tone="error" className="mb-4">{error}</Alert>}
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <Input
                label="New password"
                type="password"
                placeholder="8+ characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoFocus
              />
              <Input
                label="Confirm new password"
                type="password"
                placeholder="Repeat password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
              />
              <Button type="submit" className="w-full" loading={submitting}>
                Reset password
              </Button>
            </form>
          </>
        )}
      </Card>
    </div>
  )
}