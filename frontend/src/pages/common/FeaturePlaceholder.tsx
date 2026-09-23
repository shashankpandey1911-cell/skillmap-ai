import { Construction } from 'lucide-react'
import { Card, Badge } from '../../components/ui'
import type { RouteMeta } from '../../router/routes'

/**
 * Rendered for features that belong to a later build phase. Shows what the
 * feature will do and which phase delivers it — no fake buttons, no dead UI.
 */
export function FeaturePlaceholder({ meta }: { meta: RouteMeta }) {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <Badge tone="brand">{meta.phase}</Badge>
        <h2 className="text-xl font-semibold text-slate-900">{meta.title}</h2>
      </div>

      <Card>
        <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-700">
            <Construction className="h-6 w-6" aria-hidden="true" />
          </div>
          <div>
            <p className="font-medium text-slate-900">Under construction</p>
            <p className="mt-1 text-sm text-slate-600">{meta.description}</p>
          </div>
        </div>
      </Card>

      {meta.planned && meta.planned.length > 0 && (
        <Card title="Planned for this phase" subtitle="What this page will include">
          <ul className="grid gap-2 sm:grid-cols-2">
            {meta.planned.map((item) => (
              <li key={item} className="flex items-center gap-2 text-sm text-slate-600">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-400" aria-hidden="true" />
                {item}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  )
}
