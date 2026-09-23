import { useState, type FormEvent } from 'react'
import { Alert, Button, Input, Modal, Textarea } from '../../../components/ui'
import {
  createProject,
  updateProject,
  type Project,
  type ProjectPayload,
} from '../../../api/endpoints/students'
import { extractApiError, extractFieldErrors } from '../../../utils/errors'

interface Props {
  /** Pass a project to edit; null means create. */
  project: Project | null
  onClose: () => void
  onSaved: () => void
}

const EMPTY: ProjectPayload = {
  name: '',
  description: '',
  technologies: '',
  github_url: '',
  demo_url: '',
}

export function ProjectFormModal({ project, onClose, onSaved }: Props) {
  const [form, setForm] = useState<ProjectPayload>(() =>
    project
      ? {
          name: project.name,
          description: project.description,
          technologies: project.technologies,
          github_url: project.github_url,
          demo_url: project.demo_url,
        }
      : EMPTY,
  )
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const set = (key: keyof ProjectPayload, value: string) =>
    setForm((f) => ({ ...f, [key]: value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setFieldErrors({})
    setSubmitting(true)
    try {
      if (project) {
        await updateProject(project.id, form)
      } else {
        await createProject(form)
      }
      onSaved()
    } catch (err) {
      const fieldErrs = extractFieldErrors(err)
      if (Object.keys(fieldErrs).length > 0) {
        setFieldErrors(fieldErrs)
      } else {
        setFormError(extractApiError(err, 'Could not save the project.'))
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open title={project ? 'Edit project' : 'Add project'} onClose={onClose}>
      {formError && <Alert tone="error" className="mb-4">{formError}</Alert>}
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <Input
          label="Project name"
          value={form.name}
          onChange={(e) => set('name', e.target.value)}
          error={fieldErrors.name}
          required
          autoFocus
        />
        <Textarea
          label="Description"
          rows={3}
          value={form.description}
          onChange={(e) => set('description', e.target.value)}
          error={fieldErrors.description}
          placeholder="What does it do? What problem does it solve?"
        />
        <Input
          label="Technologies"
          value={form.technologies}
          onChange={(e) => set('technologies', e.target.value)}
          error={fieldErrors.technologies}
          placeholder="React, Django, PostgreSQL"
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="GitHub link"
            type="url"
            value={form.github_url}
            onChange={(e) => set('github_url', e.target.value)}
            error={fieldErrors.github_url}
            placeholder="https://github.com/…"
          />
          <Input
            label="Demo link"
            type="url"
            value={form.demo_url}
            onChange={(e) => set('demo_url', e.target.value)}
            error={fieldErrors.demo_url}
            placeholder="https://…"
          />
        </div>
        <div className="flex justify-end gap-3 border-t border-slate-100 pt-4">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={submitting}>
            {project ? 'Save changes' : 'Add project'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
