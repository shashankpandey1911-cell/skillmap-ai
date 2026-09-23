import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Alert, Button, Card, Input } from '../../components/ui'
import { extractApiError } from '../../utils/errors'
import { resendVerification, verifyEmail } from '../../api/endpoints/auth'

type VerifyState = 'verifying' | 'success' | 'already_verified' | 'expired' | 'invalid' | 'error'

type ApiVerifyStatus = 'verified' | 'already_verified' | 'expired' | 'invalid'

const STATE_CONFIG: Record<Exclude<VerifyState, 'verifying'>, { icon: string; title: string; tone: 'success' | 'warning' | 'error' }> = {
  success: { icon: '✅', title: 'Email verified!', tone: 'success' },
  already_verified: { icon: '✅', title: 'Already verified', tone: 'success' },
  expired: { icon: '⏰', title: 'Link expired', tone: 'warning' },
  invalid: { icon: '❌', title: 'Invalid link', tone: 'error' },
  error: { icon: '⚠️', title: 'Something went wrong', tone: 'error' },
}

/** Landing page for the verification link emailed at sign-up. */
export function VerifyEmail() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const uidb64 = params.get('uid') ?? ''
  const token = params.get('token') ?? ''

  const [state, setState] = useState<VerifyState>('verifying')
  const [message, setMessage] = useState('')
  const [resendEmail, setResendEmail] = useState('')
  const [showResend, setShowResend] = useState(false)
  const [resent, setResent] = useState(false)
  const [resendError, setResendError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const ranOnce = useRef(false)

  useEffect(() => {
    if (ranOnce.current) return
    ranOnce.current = true
    if (!uidb64 || !token) {
      setState('invalid')
      setMessage('This verification link is malformed.')
      return
    }
    verifyEmail(uidb64, token)
      .then((res) => {
        // Map the API outcome onto the local state machine.
        const status: VerifyState = res.status === 'verified' ? 'success' : res.status
        setState(status)
        setMessage(res.detail)
      })
      .catch((err) => {
        // 400 responses carry a status field; network errors land here too.
        const apiStatus = (err as { response?: { data?: { status?: ApiVerifyStatus } } })?.response?.data?.status
        const detail = extractApiError(err, 'Verification failed. Please try again.')
        const mapped: VerifyState | null =
          apiStatus === 'verified'
            ? 'success'
            : apiStatus === 'already_verified'
              ? 'already_verified'
              : apiStatus === 'expired'
                ? 'expired'
                : apiStatus === 'invalid'
                  ? 'invalid'
                  : null
        setState(mapped ?? 'error')
        setMessage(detail)
      })
  }, [uidb64, token])

  const handleResend = async () => {
    setResendError(null)
    setResent(false)
    setSending(true)
    try {
      await resendVerification(resendEmail)
      setResent(true)
    } catch (err) {
      setResendError(extractApiError(err, 'Could not resend the email. Please try again.'))
    } finally {
      setSending(false)
    }
  }

  const canResend = showResend || state === 'expired' || state === 'invalid'

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <Card className="w-full max-w-md">
        {state === 'verifying' ? (
          <div className="py-10 text-center">
            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600" />
            <p className="text-sm text-slate-500">Verifying your email…</p>
          </div>
        ) : (
          <>
            <div className="mb-6 text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-brand-50 text-2xl">
                {STATE_CONFIG[state].icon}
              </div>
              <h1 className="text-xl font-semibold text-slate-900">{STATE_CONFIG[state].title}</h1>
              {message && <p className="mt-2 text-sm text-slate-500">{message}</p>}
            </div>

            {(state === 'success' || state === 'already_verified') && (
              <Button
                className="w-full"
                size="lg"
                onClick={() => navigate('/auth/login')}
              >
                Sign in
              </Button>
            )}

            {canResend && (
              <div className="mt-2 space-y-3">
                {resent && <Alert tone="success">A new verification link has been sent.</Alert>}
                {resendError && <Alert tone="error">{resendError}</Alert>}
                {showResend ? (
                  <div className="flex gap-2">
                    <Input
                      type="email"
                      placeholder="you@college.edu"
                      value={resendEmail}
                      onChange={(e) => setResendEmail(e.target.value)}
                      className="flex-1"
                    />
                    <Button loading={sending} onClick={handleResend} disabled={!resendEmail.trim()}>
                      Send
                    </Button>
                  </div>
                ) : (
                  <Button variant="secondary" className="w-full" onClick={() => setShowResend(true)}>
                    Resend verification email
                  </Button>
                )}
              </div>
            )}

            <p className="mt-6 text-center text-sm text-slate-500">
              <Link to="/auth/login" className="font-medium text-brand-700 hover:underline">
                Back to sign in
              </Link>
            </p>
          </>
        )}
      </Card>
    </div>
  )
}
