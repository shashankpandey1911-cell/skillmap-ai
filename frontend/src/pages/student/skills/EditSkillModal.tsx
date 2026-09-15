import { useState, type FormEvent } from 'react'
import { Alert, Badge, Button, Modal, Select } from '../../../components/ui'
import {
  EXPERIENCE_LEVELS,
  PROFICIENCY_LABELS,
  updateMySkill,
  type UserSkill,
} from '../../../api/endpoints/skills'
import { extractApiError, extractFieldErrors } from '../../../utils/errors'

interface Props {
  skill: UserSkill
  onClose: () => void
  onSaved: () => void
}

export function EditSkillModal({ skill, onClose, onSaved }: Props) {
  const [proficiency, setProficiency] = useState(String(skill.proficiency_level))
  const [experience, setExperience] = useState<UserSkill['experience_level']>(skill.experience_level)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setFieldErrors({})
    setSubmitting(true)
    try {
      await updateMySkill(skill.id, {
        proficiency_level: Number(proficiency),
        experience_level: experience,
      })
      onSaved()
    } catch (err) {
      const fieldErrs = extractFieldErrors(err)
      if (Object.keys(fieldErrs).length > 0) {
        setFieldErrors(fieldErrs)
      } else {
        setFormError(extractApiError(err, 'Could not update the skill.'))
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open title="Edit skill" onClose={onClose}>
      {formError && <Alert tone="error" className="mb-4">{formError}</Alert>}
      <div className="mb-5 flex items-center gap-2">
        <span className="text-base font-semibold text-slate-900">{skill.skill.name}</span>
        <Badge tone="brand">{skill.skill.category}</Badge>
        {skill.assessment_score !== null && (
          <Badge tone="green">Assessed · {skill.assessment_score}/100</Badge>
        )}
      </div>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <Select
          label="Self-rated proficiency"
          options={[1, 2, 3, 4, 5].map((n) => ({ value: String(n), label: PROFICIENCY_LABELS[n] }))}
          value={proficiency}
          onChange={(e) => setProficiency(e.target.value)}
          error={fieldErrors.proficiency_level}
        />
        <Select
          label="Experience level"
          options={EXPERIENCE_LEVELS.map((l) => ({ value: l.value, label: l.label }))}
          value={experience}
          onChange={(e) => setExperience(e.target.value as UserSkill['experience_level'])}
          error={fieldErrors.experience_level}
        />
        {skill.assessment_score === null && (
          <p className="text-xs text-slate-500">
            Your displayed score is your proficiency scaled to a percentage. Once you complete a
            skill assessment, your score becomes the objective assessment result.
          </p>
        )}
        <div className="flex justify-end gap-3 border-t border-slate-100 pt-4">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={submitting}>Save changes</Button>
        </div>
      </form>
    </Modal>
  )
}