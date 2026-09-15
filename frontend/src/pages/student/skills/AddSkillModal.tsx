import { useMemo, useState, type FormEvent } from 'react'
import { Search } from 'lucide-react'
import {
  Alert,
  Badge,
  Button,
  Input,
  Modal,
  Select,
} from '../../../components/ui'
import {
  addMySkill,
  EXPERIENCE_LEVELS,
  listCatalog,
  PROFICIENCY_LABELS,
  SKILL_CATEGORIES,
  type Skill,
  type UserSkill,
} from '../../../api/endpoints/skills'
import { useApi } from '../../../hooks/useApi'
import { extractApiError, extractFieldErrors } from '../../../utils/errors'
import { cn } from '../../../utils/cn'

interface Props {
  /** Skills the student already has — hidden from the picker. */
  existingSkills: UserSkill[]
  onClose: () => void
  onSaved: () => void
}

export function AddSkillModal({ existingSkills, onClose, onSaved }: Props) {
  const catalogQuery = useApi(() => listCatalog())
  const [category, setCategory] = useState<string>('')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Skill | null>(null)
  const [proficiency, setProficiency] = useState('3')
  const [experience, setExperience] = useState('INTERMEDIATE')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const existingIds = useMemo(() => new Set(existingSkills.map((s) => s.skill.id)), [existingSkills])

  const options = useMemo(() => {
    const catalog = catalogQuery.data ?? []
    return catalog.filter((skill) => {
      if (existingIds.has(skill.id)) return false
      if (category && skill.category !== category) return false
      if (search && !skill.name.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [catalogQuery.data, existingIds, category, search])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setFieldErrors({})
    if (!selected) {
      setFieldErrors({ skill: 'Choose a skill from the catalog first.' })
      return
    }
    setSubmitting(true)
    try {
      await addMySkill({
        skill: selected.id,
        proficiency_level: Number(proficiency),
        experience_level: experience as UserSkill['experience_level'],
      })
      onSaved()
    } catch (err) {
      const fieldErrs = extractFieldErrors(err)
      if (Object.keys(fieldErrs).length > 0) {
        setFieldErrors(fieldErrs)
      } else {
        setFormError(extractApiError(err, 'Could not add the skill.'))
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open title="Add skill" onClose={onClose} wide>
      {formError && <Alert tone="error" className="mb-4">{formError}</Alert>}
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        <div>
          <p className="mb-2 text-sm font-medium text-slate-700">Pick a skill</p>
          <div className="mb-3 flex flex-col gap-2 sm:flex-row">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <Input
                aria-label="Search skills"
                placeholder="Search the catalog…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select
              aria-label="Filter by category"
              options={[
                { value: '', label: 'All categories' },
                ...SKILL_CATEGORIES.map((c) => ({ value: c, label: c })),
              ]}
              value={category}
              onChange={(e) => {
                setCategory(e.target.value)
                setSelected(null)
              }}
              className="sm:w-56"
            />
          </div>

          {catalogQuery.loading ? (
            <p className="py-4 text-sm text-slate-400">Loading catalog…</p>
          ) : options.length === 0 ? (
            <p className="rounded-lg bg-slate-50 py-4 text-center text-sm text-slate-500">
              {search || category
                ? 'No matching skills in the catalog.'
                : 'You have added every skill in the catalog. 🎉'}
            </p>
          ) : (
            <ul className="max-h-56 divide-y divide-slate-100 overflow-y-auto rounded-lg border border-slate-200">
              {options.map((skill) => {
                const isSelected = selected?.id === skill.id
                return (
                  <li key={skill.id}>
                    <button
                      type="button"
                      onClick={() => setSelected(isSelected ? null : skill)}
                      className={cn(
                        'flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-sm transition-colors',
                        isSelected ? 'bg-brand-50' : 'hover:bg-slate-50',
                      )}
                    >
                      <span className="font-medium text-slate-800">{skill.name}</span>
                      <Badge tone={isSelected ? 'brand' : 'slate'}>{skill.category}</Badge>
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
          {fieldErrors.skill && <p className="mt-1 text-xs text-red-600">{fieldErrors.skill}</p>}
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label="Self-rated proficiency"
            options={[1, 2, 3, 4, 5].map((n) => ({ value: String(n), label: PROFICIENCY_LABELS[n] }))}
            value={proficiency}
            onChange={(e) => setProficiency(e.target.value)}
          />
          <Select
            label="Experience level"
            options={EXPERIENCE_LEVELS.map((l) => ({ value: l.value, label: l.label }))}
            value={experience}
            onChange={(e) => setExperience(e.target.value)}
          />
        </div>

        {selected && (
          <p className="text-sm text-slate-600">
            Adding <strong className="text-brand-700">{selected.name}</strong>{' '}
            ({selected.category})
            {selected.description && <span> — {selected.description}</span>}
          </p>
        )}

        <div className="flex justify-end gap-3 border-t border-slate-100 pt-4">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={submitting} disabled={!selected}>Add skill</Button>
        </div>
      </form>
    </Modal>
  )
}