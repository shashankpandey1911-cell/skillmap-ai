import { useState, type FormEvent } from 'react'
import { Alert, Button, Input, Modal } from '../../../components/ui'
import {
  createCertification,
  updateCertification,
  type Certification,
  type CertificationPayload,
} from '../../../api/endpoints/students'
import { extractApiError, extractFieldErrors } from '../../../utils/errors'

interface Props {
  /** Pass a certification to edit; null means create. */
  certification: Certification | null
  onClose: () => void
  onSaved: () => void
}

type FormState = Omit<CertificationPayload, 'issued_date'> & { issued_date: string }

const EMPTY: FormState = {
  name: '',
  provider: '',
  issued_date: '',
  credential_url: '',
}

export function CertificationFormModal({ certification, onClose, onSaved }: Props) {
  const [form, setForm] = useState<FormState>(() =>
    certification
      ? {
          name: certification.name,
          provider: certification.provider,
          issued_date: certification.issued_date ?? '',
          credential_url: certification.credential_url,
        }
      : EMPTY,
  )
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const set = (key: keyof FormState, value: string) =>
    setForm((f) => ({ ...f, [key]: value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setFieldErrors({})
    setSubmitting(true)
    try {
      if (certification) {
        await updateCertification(certification.id, form)
      } else {
        await createCertification(form)
      }
      onSaved()
    } catch (err) {
      const fieldErrs = extractFieldErrors(err)
      if (Object.keys(fieldErrs).length > 0) {
        setFieldErrors(fieldErrs)
      } else {
        setFormError(extractApiError(err, 'Could not save the certification.'))
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal
      open
      title={certification ? 'Edit certification' : 'Add certification'}
      onClose={onClose}
    >
      {formError && <Alert tone="error" className="mb-4">{formError}</Alert>}
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <Input
          label="Certificate name"
          value={form.name}
          onChange={(e) => set('name', e.target.value)}
          error={fieldErrors.name}
          required
          autoFocus
        />
        <Input
          label="Provider"
          value={form.provider}
          onChange={(e) => set('provider', e.target.value)}
          error={fieldErrors.provider}
          placeholder="e.g. Coursera, AWS, NPTEL"
        />
        <Input
          label="Date issued"
          type="date"
          value={form.issued_date}
          onChange={(e) => set('issued_date', e.target.value)}
          error={fieldErrors.issued_date}
        />
        <Input
          label="Credential link"
          type="url"
          value={form.credential_url}
          onChange={(e) => set('credential_url', e.target.value)}
          error={fieldErrors.credential_url}
          placeholder="https://…"
        />
        <div className="flex justify-end gap-3 border-t border-slate-100 pt-4">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={submitting}>
            {certification ? 'Save changes' : 'Add certification'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}