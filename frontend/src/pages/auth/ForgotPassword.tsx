import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Alert, Button, Card, Input } from '../../components/ui'
import { forgotPassword } from '../../api/endpoints/auth'
import { extractApiError } from '../../utils/errors'

export function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [sent, setSent] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await forgotPassword(email.trim())
      setSent(true)
    } catch (err) {
      setError(extractApiError(err, 'Could not send the reset link. Please try again.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-xl font-semibold text-slate-900">Forgot password</h1>
          <p className="mt-1 text-sm text-slate-500">
            Enter your email and we'll send you a reset link.
          </p>
        </div>

        {sent ? (
          <Alert tone="success">
            If an account exists for <strong>{email}</strong>, a password reset link has been
            sent. Check your inbox (and spam). In local development the link is printed in the
            Django server console.
          </Alert>
        ) : (
          <>
            {error && <Alert tone="error" className="mb-4">{error}</Alert>}
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <Input
                label="Email"
                type="email"
                placeholder="you@college.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
              <Button type="submit" className="w-full" loading={submitting}>
                Send reset link
              </Button>
            </form>
          </>
        )}

        <p className="mt-6 text-center text-sm text-slate-500">
          Remembered it?{' '}
          <Link to="/auth/login" className="font-medium text-brand-700 hover:underline">
            Back to sign in
          </Link>
        </p>
      </Card>
    </div>
  )
}