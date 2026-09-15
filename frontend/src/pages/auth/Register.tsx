import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { roleHome } from '../../auth/guards'
import { Alert, Button, Card, Input, Select } from '../../components/ui'
import { extractApiError, extractFieldErrors } from '../../utils/errors'
import type { RegisterPayload } from '../../api/endpoints/auth'

const YEARS = [
  { value: '', label: 'Select year' },
  ...[1, 2, 3, 4, 5, 6].map((y) => ({ value: String(y), label: `Year ${y}` })),
]

export function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [role, setRole] = useState<'STUDENT' | 'PROFESSOR'>('STUDENT')
  const [college, setCollege] = useState('')
  const [course, setCourse] = useState('')
  const [year, setYear] = useState('')

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setFieldErrors({})

    if (password !== confirm) {
      setFieldErrors({ confirm: 'Passwords do not match.' })
      return
    }

    const payload: RegisterPayload = {
      full_name: fullName.trim(),
      email: email.trim(),
      password,
      role,
      ...(role === 'STUDENT'
        ? { college: college.trim(), course: course.trim(), year: year ? Number(year) : null }
        : {}),
    }

    setSubmitting(true)
    try {
      const user = await register(payload)
      navigate(roleHome[user.role], { replace: true })
    } catch (err) {
      const fieldErrs = extractFieldErrors(err)
      if (Object.keys(fieldErrs).length > 0) {
        setFieldErrors(fieldErrs)
      } else {
        setFormError(extractApiError(err, 'Registration failed. Please try again.'))
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <Card className="w-full max-w-lg">
        <div className="mb-6 text-center">
          <h1 className="text-xl font-semibold text-slate-900">Create your account</h1>
          <p className="mt-1 text-sm text-slate-500">
            Students build their career profile; professors guide them.
          </p>
        </div>

        {formError && <Alert tone="error" className="mb-4">{formError}</Alert>}

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          <Input
            label="Full name"
            placeholder="Riya Sharma"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            error={fieldErrors.full_name}
            required
            autoFocus
          />
          <Input
            label="Email"
            type="email"
            placeholder="riya@college.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            error={fieldErrors.email}
            required
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              label="Password"
              type="password"
              placeholder="8+ characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={fieldErrors.password}
              required
            />
            <Input
              label="Confirm password"
              type="password"
              placeholder="Repeat password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              error={fieldErrors.confirm}
              required
            />
          </div>

          <Select
            label="I am a"
            options={[
              { value: 'STUDENT', label: 'Student' },
              { value: 'PROFESSOR', label: 'Professor' },
            ]}
            value={role}
            onChange={(e) => setRole(e.target.value as 'STUDENT' | 'PROFESSOR')}
            error={fieldErrors.role}
          />

          {role === 'STUDENT' && (
            <div className="grid gap-4 rounded-lg border border-slate-200 bg-slate-50 p-4 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <Input
                  label="College"
                  placeholder="National Institute of Technology, Trichy"
                  value={college}
                  onChange={(e) => setCollege(e.target.value)}
                  error={fieldErrors.college}
                  required
                />
              </div>
              <Input
                label="Course"
                placeholder="B.Tech Computer Science"
                value={course}
                onChange={(e) => setCourse(e.target.value)}
                error={fieldErrors.course}
                required
              />
              <Select
                label="Year"
                options={YEARS}
                value={year}
                onChange={(e) => setYear(e.target.value)}
                error={fieldErrors.year}
              />
            </div>
          )}

          <Button type="submit" className="w-full" size="lg" loading={submitting}>
            Create account
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{' '}
          <Link to="/auth/login" className="font-medium text-brand-700 hover:underline">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  )
}