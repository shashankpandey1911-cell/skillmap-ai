import { useMemo, useState } from 'react'
import {
  BarChart3,
  Brain,
  Cloud,
  Code2,
  Database,
  Globe,
  Layers,
  MessageSquare,
  Pencil,
  Plus,
  Search,
  Wrench,
  type LucideIcon,
} from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import { useAuth } from '../../auth/AuthContext'
import {
  deleteMySkill,
  EXPERIENCE_LEVELS,
  listMySkills,
  SKILL_CATEGORIES,
  type UserSkill,
} from '../../api/endpoints/skills'
import {
  Alert,
  Badge,
  Button,
  Card,
  ConfirmDelete,
  Input,
  ProgressBar,
  Spinner,
} from '../../components/ui'
import { AddSkillModal } from './skills/AddSkillModal'
import { EditSkillModal } from './skills/EditSkillModal'
import { cn } from '../../utils/cn'

const CATEGORY_ICONS: Record<string, LucideIcon> = {
  Programming: Code2,
  'Web Development': Globe,
  Database: Database,
  Cloud: Cloud,
  'AI/ML': Brain,
  'Data Science': BarChart3,
  Tools: Wrench,
  'Soft Skills': MessageSquare,
  Other: Layers,
}

const EXPERIENCE_LABEL = Object.fromEntries(
  EXPERIENCE_LEVELS.map((l) => [l.value, l.label]),
) as Record<UserSkill['experience_level'], string>

// Stable empty-array reference so useMemo deps stay constant.
const EMPTY_SKILLS: UserSkill[] = []

const EXPERIENCE_TONE = {
  BEGINNER: 'slate',
  INTERMEDIATE: 'brand',
  ADVANCED: 'amber',
  EXPERT: 'green',
} as const

export function MySkillsPage() {
  const { user } = useAuth()
  const { data, loading, error, refresh } = useApi(listMySkills)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string>('')
  const [addOpen, setAddOpen] = useState(false)
  const [editing, setEditing] = useState<UserSkill | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const allSkills = data ?? EMPTY_SKILLS

  const skills = useMemo(() => {
    const q = search.trim().toLowerCase()
    return allSkills.filter((s) => {
      if (category && s.skill.category !== category) return false
      if (q && !s.skill.name.toLowerCase().includes(q)) return false
      return true
    })
  }, [allSkills, search, category])

  const grouped = useMemo(() => {
    const map = new Map<string, UserSkill[]>()
    for (const s of skills) {
      const list = map.get(s.skill.category) ?? []
      list.push(s)
      map.set(s.skill.category, list)
    }
    return map
  }, [skills])

  const runDelete = async (id: number) => {
    setActionError(null)
    try {
      await deleteMySkill(id)
      refresh()
    } catch {
      setActionError('Could not delete the skill. Please try again.')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">My Skills</h2>
          <p className="mt-1 text-sm text-slate-500">
            {user?.full_name ?? user?.username}, keep your skill set up to date — it drives
            your career matches.
          </p>
        </div>
        <Button onClick={() => setAddOpen(true)}>
          <Plus className="h-4 w-4" aria-hidden="true" />
          Add skill
        </Button>
      </div>

      {/* Search + category filter */}
      <div className="space-y-3">
        <div className="relative max-w-md">
          <Search
            className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
          <Input
            aria-label="Search my skills"
            placeholder="Search your skills…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <FilterChip active={category === ''} onClick={() => setCategory('')}>
            All
          </FilterChip>
          {SKILL_CATEGORIES.map((c) => (
            <FilterChip key={c} active={category === c} onClick={() => setCategory(c)}>
              {c}
            </FilterChip>
          ))}
        </div>
      </div>

      {actionError && <Alert tone="error">{actionError}</Alert>}

      {loading ? (
        <Spinner />
      ) : error ? (
        <Alert tone="error">{error}</Alert>
      ) : allSkills.length === 0 ? (
        <Card>
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <Code2 className="h-10 w-10 text-slate-300" aria-hidden="true" />
            <div>
              <p className="font-medium text-slate-800">No skills added yet</p>
              <p className="mt-1 text-sm text-slate-500">
                Add skills from the catalog to start measuring your readiness.
              </p>
            </div>
            <Button onClick={() => setAddOpen(true)}>
              <Plus className="h-4 w-4" aria-hidden="true" />
              Add your first skill
            </Button>
          </div>
        </Card>
      ) : grouped.size === 0 ? (
        <Card>
          <p className="py-6 text-center text-sm text-slate-500">
            No skills match “{search}”{category && ` in ${category}`}.
          </p>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {[...grouped.entries()].map(([catName, catSkills]) => {
            const Icon = CATEGORY_ICONS[catName] ?? Layers
            return (
              <Card
                key={catName}
                className="md:col-span-1"
                title={
                  <span className="flex items-center gap-2">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
                      <Icon className="h-4 w-4" aria-hidden="true" />
                    </span>
                    {catName}
                  </span>
                }
                subtitle={`${catSkills.length} skill${catSkills.length === 1 ? '' : 's'}`}
              >
                <ul className="space-y-4">
                  {catSkills.map((item) => (
                    <SkillRow
                      key={item.id}
                      item={item}
                      onEdit={() => setEditing(item)}
                      onDelete={() => runDelete(item.id)}
                    />
                  ))}
                </ul>
              </Card>
            )
          })}
        </div>
      )}

      {addOpen && (
        <AddSkillModal
          existingSkills={allSkills}
          onClose={() => setAddOpen(false)}
          onSaved={() => {
            setAddOpen(false)
            refresh()
          }}
        />
      )}
      {editing && (
        <EditSkillModal
          key={editing.id}
          skill={editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null)
            refresh()
          }}
        />
      )}
    </div>
  )
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded-full border px-3 py-1 text-xs font-medium transition-colors',
        active
          ? 'border-brand-700 bg-brand-700 text-white'
          : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50',
      )}
    >
      {children}
    </button>
  )
}

function SkillRow({
  item,
  onEdit,
  onDelete,
}: {
  item: UserSkill
  onEdit: () => void
  onDelete: () => void
}) {
  const tone = EXPERIENCE_TONE[item.experience_level]
  return (
    <li className="rounded-lg border border-slate-100 px-3 py-3">
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-900">{item.skill.name}</p>
          <div className="mt-1 flex flex-wrap items-center gap-1.5">
            <Badge tone={tone}>{EXPERIENCE_LABEL[item.experience_level]}</Badge>
            <span className="text-xs text-slate-400">
              Self-rated {item.proficiency_level}/5
            </span>
            {item.assessment_score !== null && (
              <Badge tone="green">Assessed {item.assessment_score}/100</Badge>
            )}
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          <button
            type="button"
            onClick={onEdit}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
            aria-label={`Edit ${item.skill.name}`}
          >
            <Pencil className="h-4 w-4" />
          </button>
          <ConfirmDelete onConfirm={onDelete} />
        </div>
      </div>
      <div className="mt-2 flex items-center gap-3">
        <ProgressBar
          value={item.score}
          tone={item.assessment_score !== null ? 'green' : 'brand'}
          className="flex-1"
        />
        <span className="w-10 text-right text-sm font-semibold text-slate-700">
          {Math.round(item.score)}%
        </span>
      </div>
    </li>
  )
}