import { Badge } from '../../../components/ui'
import type { OpportunityType } from '../../../api/endpoints/opportunities'
import { typeLabel, TYPE_META } from './helpers'

export function TypeBadge({ type }: { type: OpportunityType }) {
  const meta = TYPE_META[type]
  const Icon = meta.icon
  return (
    <Badge tone={meta.badgeTone} className="gap-1 uppercase tracking-wide">
      <Icon className="h-3 w-3" aria-hidden="true" />
      {typeLabel(type)}
    </Badge>
  )
}
