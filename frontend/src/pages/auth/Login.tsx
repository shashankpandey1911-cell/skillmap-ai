import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Compass, ArrowRight } from 'lucide-react'
import { useAuth } from '../../auth/AuthContext'
import { roleHome } from '../../auth/guards'
import { Alert, Button, Input } from '../../components/ui'
import { extractApiError } from '../../utils/errors'

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const from = (location.state as { from?: string } | null)?.from

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const user = await login(email.trim(), password)
      navigate(from ?? roleHome[user.role], { replace: true })
    } catch (err) {
      setError(extractApiError(err, 'Unable to log in. Check your email and password.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-1/2 gradient-navy relative overflow-hidden">
        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-16">
          <div className="flex items-center gap-3 mb-8">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm">
              <Compass className="h-7 w-7 text-brand-300" />
            </div>
            <span className="text-2xl font-bold text-white">
              SkillMap <span className="text-brand-300">AI</span>
            </span>
          </div>
          <h1 className="text-4xl font-bold text-white leading-tight mb-4">
            Your Career,<br />
            <span className="text-brand-300">Intelligently Mapped</span>
          </h1>
          <p className="text-lg text-white/70 max-w-md">
            Discover your strengths, close skill gaps, and find the perfect career path with AI-powered guidance.
          </p>
          <div className="mt-12 grid grid-cols-2 gap-4">
            {[
              { value: '50+', label: 'Skills Tracked' },
              { value: '10+', label: 'Career Paths' },
              { value: '100+', label: 'Learning Resources' },
              { value: 'AI', label: 'Powered Insights' },
            ].map((stat) => (
              <div key={stat.label} className="rounded-xl bg-white/5 backdrop-blur-sm p-4">
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-sm text-white/50">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
        {/* Decorative circles */}
        <div className="absolute top-20 right-20 h-64 w-64 rounded-full bg-brand-500/10 blur-3xl" />
        <div className="absolute bottom-20 left-20 h-48 w-48 rounded-full bg-brand-400/10 blur-3xl" />
      </div>

      {/* Right panel — form */}
      <div className="flex flex-1 items-center justify-center px-6 py-12 bg-white">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600">
              <Compass className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">
              SkillMap <span className="text-brand-600">AI</span>
            </span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900">Welcome back</h2>
            <p className="mt-2 text-sm text-gray-500">
              Sign in to your account to continue
            </p>
          </div>

          {error && <Alert tone="error" className="mb-6">{error}</Alert>}

          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            <Input
              label="Email address"
              type="email"
              autoComplete="email"
              placeholder="you@college.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
            <Input
              label="Password"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <div className="flex justify-end">
              <Link
                to="/auth/forgot-password"
                className="text-sm font-medium text-brand-600 hover:text-brand-700 transition-colors"
              >
                Forgot password?
              </Link>
            </div>
            <Button
              type="submit"
              className="w-full"
              loading={submitting}
              size="lg"
              icon={<ArrowRight className="h-4 w-4" />}
            >
              Sign in
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <Link
              to="/auth/register"
              className="font-semibold text-brand-600 hover:text-brand-700 transition-colors"
            >
              Create one now
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
