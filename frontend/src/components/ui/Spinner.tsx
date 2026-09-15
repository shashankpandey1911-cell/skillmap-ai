import { Loader2 } from 'lucide-react'
import { cn } from '../../utils/cn'

export function Spinner({ label = 'Loading…', centered = false }: { label?: string; centered?: boolean }) {
  return (
    <div className={cn(
      'flex items-center gap-3 text-sm text-gray-500',
      centered && 'justify-center py-12',
    )}>
      <Loader2 className="h-5 w-5 animate-spin text-brand-500" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}
