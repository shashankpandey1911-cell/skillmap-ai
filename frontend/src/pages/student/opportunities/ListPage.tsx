import { useEffect, useMemo, useState } from 'react'
import { Briefcase, Search, X } from 'lucide-react'
import {
  listOpportunities,
  OPPORTUNITY_TYPES,
  type OpportunitySummary,
  type OpportunityType,
} from '../../../api/endpoints/opportunities'
import { useAuth } from '../../../auth/AuthContext'
import { Alert, Badge, Button, Card, Select, Spinner } from '../../../components/ui'
import { cn } from '../../../utils/cn'
import { OpportunityCard } from './OpportunityCard'

type SortOption = 'recent' | 'deadline' | 'match'

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'recent', label: 'Newest first' },
  { value: 'deadline', label: 'Closes soonest' },
  { value: 'match', label: 'Best match' },
]

export function OpportunitiesPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')
  const [type, setType] = useState<OpportunityType | ''>('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [sort, setSort] = useState<SortOption>('recent')
  const [debounced, setDebounced] = useState({ search: '', location: '' })

  // Debounce the free-text fields so typing doesn't fire a request per key.
  useEffect(() => {
    const timer = setTimeout(
      () => setDebounced({ search: search.trim(), location: location.trim() }),
      350,
    )
    return () => clearTimeout(timer)
  }, [search, location])

  const { data, loading, error } = useOpportunityList({
    search: debounced.search,
    location: debounced.location,
    type,
    remoteOnly,
    sort,
  })

  const hasFilters =
    Boolean(debounced.search) ||
    Boolean(debounced.location) ||
    type !== '' ||
    remoteOnly ||
    sort !== 'recent'

  const resetFilters = () => {
    setSearch('')
    setLocation('')
    setType('')
    setRemoteOnly(false)
    setSort('recent')
  }

  const internships = useMemo(
    () => (data ?? []).filter((o) => o.opportunity_type === 'INTERNSHIP').length,
    [data],
  )
  const jobs = useMemo(
    () => (data ?? []).filter((o) => o.opportunity_type === 'JOB').length,
    [data],
  )

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Opportunities</h2>
        <p className="mt-1 text-sm text-slate-500">
          {user?.full_name ?? user?.username}, browse open jobs, internships, hackathons
          and competitions — with a real skills match for each.
        </p>
      </div>

      <Card className="space-y-4">
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto_auto]">
          <label className="relative block">
            <span className="sr-only">Search opportunities</span>
            <Search
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
              aria-hidden="true"
            />
            <input
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search title, company, keywords…"
              className="h-10 w-full rounded-lg border border-slate-300 bg-white pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-2 focus:outline-brand-500/30"
            />
          </label>
          <label className="relative block">
            <span className="sr-only">Filter by location</span>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Location (e.g. Bengaluru, Remote)…"
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-2 focus:outline-brand-500/30"
            />
          </label>
          <Select
            aria-label="Sort opportunities"
            value={sort}
            onChange={(e) => setSort(e.target.value as SortOption)}
            options={SORT_OPTIONS.map((o) => ({ value: o.value, label: o.label }))}
            className="w-44"
          />
          <button
            type="button"
            onClick={() => setRemoteOnly((v) => !v)}
            aria-pressed={remoteOnly}
            className={cn(
              'h-10 self-end rounded-lg border px-3 text-sm font-medium transition-colors',
              remoteOnly
                ? 'border-brand-600 bg-brand-700 text-white'
                : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50',
            )}
          >
            Remote only
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Type
          </span>
          <div className="flex flex-wrap gap-1.5">
            <TypePill active={type === ''} onClick={() => setType('')} label="All" />
            {OPPORTUNITY_TYPES.map((t) => (
              <TypePill
                key={t}
                active={type === t}
                onClick={() => setType(type === t ? '' : t)}
                label={t.charAt(0) + t.slice(1).toLowerCase() + 's'}
              />
            ))}
          </div>
          <div className="ml-auto flex items-center gap-2 text-sm text-slate-500">
            {data && (
              <>
                <Badge tone="brand">{data.length} open</Badge>
                <Badge tone="green">{internships} internships</Badge>
                <Badge tone="slate">{jobs} jobs</Badge>
              </>
            )}
          </div>
        </div>
      </Card>

      {loading ? (
        <Spinner label="Loading opportunities…" />
      ) : error ? (
        <Alert tone="error">{error}</Alert>
      ) : data && data.length === 0 ? (
        <Card>
          <div className="flex flex-col items-center gap-3 py-10 text-center">
            <Briefcase className="h-10 w-10 text-slate-300" aria-hidden="true" />
            <div>
              <p className="font-medium text-slate-800">No opportunities found</p>
              <p className="mt-1 text-sm text-slate-500">
                {hasFilters
                  ? 'Try widening your search or clearing the filters.'
                  : 'The admin has not published any opportunities yet.'}
              </p>
            </div>
            {hasFilters && (
              <Button variant="outline" onClick={resetFilters} className="mt-1">
                <X className="h-4 w-4" aria-hidden="true" />
                Clear filters
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {(data ?? []).map((opportunity) => (
            <OpportunityCard key={opportunity.id} opportunity={opportunity} />
          ))}
        </div>
      )}
    </div>
  )
}

interface OpportunityQuery {
  search: string
  location: string
  type: OpportunityType | ''
  remoteOnly: boolean
  sort: SortOption
}

/** Fetch the listing; refetches whenever the committed filters change. */
function useOpportunityList(query: OpportunityQuery) {
  const [data, setData] = useState<OpportunitySummary[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    listOpportunities({
      search: query.search || undefined,
      location: query.location || undefined,
      type: query.type || undefined,
      remote: query.remoteOnly || undefined,
      sort: query.sort,
    })
      .then((rows) => {
        if (!cancelled) {
          setData(rows)
          setError(null)
        }
      })
      .catch(() => {
        if (!cancelled) setError('Could not load opportunities. Please try again.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query.search, query.location, query.type, query.remoteOnly, query.sort])

  return { data, loading, error }
}

function TypePill({
  active,
  onClick,
  label,
}: {
  active: boolean
  onClick: () => void
  label: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        'rounded-full px-3 py-1 text-xs font-medium transition-colors',
        active
          ? 'bg-brand-700 text-white'
          : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
      )}
    >
      {label}
    </button>
  )
}
