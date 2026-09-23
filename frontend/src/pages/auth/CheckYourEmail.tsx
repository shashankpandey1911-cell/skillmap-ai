import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Alert, Button, Card } from '../../components/ui'
import { extractApiError } from '../../utils/errors'
import { resendVerification } from '../../api/endpoints/auth'

/** Shown right after sign-up: instructs the user to confirm their email. */
export function CheckYourEmail({ email }: { email: string }) {
  const [resent, setResent] = useState(false)
  const [resendError, setResendError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  const handleResend = async () => {
    setResendError(null)
    setResent(false)
    setSending(true)
    try {
      await resendVerification(email)
      setResent(true)
    } catch (err) {
      setResendError(extractApiError(err, 'Could not resend the email. Please try again.'))
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-2xl">
            ✉️
          </div>
          <h1 className="text-xl font-semibold text-slate-900">
            Check your email to verify your account.
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            We sent a verification link to <span className="font-medium text-slate-700">{email}</span>.
            Click it to activate your account. The link is valid for 24 hours.
          </p>
        </div>

        {resent && (
          <Alert tone="success" className="mb-4">
            A new verification link has been sent to {email}.
          </Alert>
        )}
        {resendError && <Alert tone="error" className="mb-4">{resendError}</Alert>}

        <Button className="w-full" variant="secondary" loading={sending} onClick={handleResend}>
          Resend verification email
        </Button>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already verified?{' '}
          <Link to="/auth/login" className="font-medium text-brand-700 hover:underline">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  )
}
