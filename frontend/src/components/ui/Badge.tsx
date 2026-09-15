import type { ReactNode } from 'react'
import { cn } from '../../utils/cn'

export type BadgeTone = 'brand' | 'green' | 'amber' | 'red' | 'slate' | 'purple'

const tones: Record<BadgeTone, string> = {
  brand: 'bg-brand-50 text-brand-700 ring-brand-200/50',
  green: 'bg-emerald-50 text-emerald-700 ring-emerald-200/50',
  amber: 'bg-amber-50 text-amber-700 ring-amber-200/50',
  red: 'bg-red-50 text-red-700 ring-red-200/50',
  slate: 'bg-gray-100 text-gray-600 ring-gray-200/50',
  purple: 'bg-purple-50 text-purple-700 ring-purple-200/50',
}

export function Badge({
  tone = 'slate',
  children,
  className,
}: {
  tone?: BadgeTone
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset',
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}
