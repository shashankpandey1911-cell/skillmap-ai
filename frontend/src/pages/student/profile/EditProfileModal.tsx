import { useState, type FormEvent } from 'react'
import { Alert, Button, Input, Modal, Select, Textarea } from '../../../components/ui'
import { updateMe, type StudentMe, type StudentProfileUpdate } from '../../../api/endpoints/students'
import { extractApiError, extractFieldErrors } from '../../../utils/errors'

const YEARS = [
  { value: '', label: 'Select year' },
  ...[1, 2, 3, 4, 5, 6].map((y) => ({ value: String(y), label: `Year ${y}` })),
]
const SEMESTERS = [
  { value: '', label: 'Select semester' },
  ...[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((s) => ({ value: String(s), label: `Semester ${s}` })),
]

interface Props {
  me: StudentMe
  onClose: () => void
  onSaved: () => void
}

/**
 * Rendered only while open (parent gates it), so state initializes fresh on
 * every open via the useState initializer — no effect needed.
 */
export function EditProfileModal({ me, onClose, onSaved }: Props) {
  const [form, setForm] = useState<StudentProfileUpdate>(() => ({
    first_name: me.user.first_name,
    last_name: me.user.last_name,
    phone: me.user.phone ?? '',
    ...me.profile,
  }))
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const set = (key: keyof StudentProfileUpdate, value: unknown) =>
    setForm((f) => ({ ...f, [key]: value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setFieldErrors({})
    setSubmitting(true)
    try {
      await updateMe(form)
      onSaved()
    } catch (err) {
      const fieldErrs = extractFieldErrors(err)
      if (Object.keys(fieldErrs).length > 0) {
        setFieldErrors(fieldErrs)
      } else {
        setFormError(extractApiError(err, 'Could not save the profile.'))
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open title="Edit profile" onClose={onClose} wide>
      {formError && <Alert tone="error" className="mb-4">{formError}</Alert>}
      <form onSubmit={handleSubmit} className="space-y-6" noValidate>
        <fieldset className="space-y-4">
          <legend className="text-sm font-semibold text-brand-700">Personal</legend>
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="First name" value={form.first_name ?? ''} onChange={(e) => set('first_name', e.target.value)} error={fieldErrors.first_name} />
            <Input label="Last name" value={form.last_name ?? ''} onChange={(e) => set('last_name', e.target.value)} error={fieldErrors.last_name} />
          </div>
          <Input label="Phone" type="tel" value={form.phone ?? ''} onChange={(e) => set('phone', e.target.value)} error={fieldErrors.phone} placeholder="+91 …" />
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="College" value={form.college ?? ''} onChange={(e) => set('college', e.target.value)} error={fieldErrors.college} />
            <Input label="Course" value={form.course ?? ''} onChange={(e) => set('course', e.target.value)} error={fieldErrors.course} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="Branch" value={form.branch ?? ''} onChange={(e) => set('branch', e.target.value)} error={fieldErrors.branch} />
            <Select label="Year" options={YEARS} value={String(form.year ?? '')} onChange={(e) => set('year', e.target.value ? Number(e.target.value) : null)} error={fieldErrors.year} />
          </div>
        </fieldset>

        <fieldset className="space-y-4">
          <legend className="text-sm font-semibold text-brand-700">Academic</legend>
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="CGPA" type="text" inputMode="decimal" value={form.cgpa ?? ''} onChange={(e) => set('cgpa', e.target.value === '' ? null : e.target.value)} error={fieldErrors.cgpa} placeholder="e.g. 8.5" hint="Between 0 and 10, e.g. 8.5" />
            <Select label="Semester" options={SEMESTERS} value={String(form.semester ?? '')} onChange={(e) => set('semester', e.target.value ? Number(e.target.value) : null)} error={fieldErrors.semester} />
          </div>
          <Textarea label="Academic achievements" rows={3} value={form.achievements ?? ''} onChange={(e) => set('achievements', e.target.value)} error={fieldErrors.achievements} placeholder="Awards, scholarships, hackathons, projects…" />
        </fieldset>

        <fieldset className="space-y-4">
          <legend className="text-sm font-semibold text-brand-700">Career</legend>
          <Input label="Career goal" value={form.career_goal ?? ''} onChange={(e) => set('career_goal', e.target.value)} error={fieldErrors.career_goal} placeholder="e.g. Software Engineer at a product company" />
          <Input label="Preferred domain" value={form.preferred_domain ?? ''} onChange={(e) => set('preferred_domain', e.target.value)} error={fieldErrors.preferred_domain} placeholder="e.g. AI/ML, Backend, Data" />
          <Textarea label="Interests" rows={3} value={form.interests ?? ''} onChange={(e) => set('interests', e.target.value)} error={fieldErrors.interests} />
        </fieldset>

        <fieldset className="space-y-4">
          <legend className="text-sm font-semibold text-brand-700">About & links</legend>
          <Textarea label="About me" rows={3} value={form.about ?? ''} onChange={(e) => set('about', e.target.value)} error={fieldErrors.about} />
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="LinkedIn URL" type="url" value={form.linkedin_url ?? ''} onChange={(e) => set('linkedin_url', e.target.value)} error={fieldErrors.linkedin_url} placeholder="https://linkedin.com/in/…" />
            <Input label="GitHub URL" type="url" value={form.github_url ?? ''} onChange={(e) => set('github_url', e.target.value)} error={fieldErrors.github_url} placeholder="https://github.com/…" />
          </div>
        </fieldset>

        <div className="flex justify-end gap-3 border-t border-slate-100 pt-4">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={submitting}>Save profile</Button>
        </div>
      </form>
    </Modal>
  )
}