import type { LucideIcon } from 'lucide-react'
import { cn } from '../../utils/cn'

interface StatCardProps {
  label: string
  value: string | number
  icon: LucideIcon
  sub?: string
  /** Optional gradient variant */
  gradient?: 'blue' | 'green' | 'purple' | 'amber'
}

const gradients = {
  blue: 'from-brand-500 to-brand-600',
  green: 'from-emerald-500 to-emerald-600',
  purple: 'from-purple-500 to-purple-600',
  amber: 'from-amber-500 to-amber-600',
}

const iconColors = {
  blue: 'text-white',
  green: 'text-white',
  purple: 'text-white',
  amber: 'text-white',
}

export function StatCard({ label, value, icon: Icon, sub, gradient = 'blue' }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-card transition-shadow duration-200 hover:shadow-card-hover">
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900 tracking-tight">{value}</p>
          {sub && <p className="mt-1 text-xs text-gray-400">{sub}</p>}
        </div>
        <div
          className={cn(
            'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br shadow-sm',
            gradients[gradient],
          )}
        >
          <Icon className={cn('h-6 w-6', iconColors[gradient])} aria-hidden="true" />
        </div>
      </div>
    </div>
  )
}
