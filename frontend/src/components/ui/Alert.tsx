import type { ReactNode } from 'react'
import { AlertCircle, CheckCircle2, Info } from 'lucide-react'
import { cn } from '../../utils/cn'

type AlertTone = 'error' | 'success' | 'info'

const styles: Record<AlertTone, string> = {
  error: 'border-red-100 bg-red-50/80 text-red-700',
  success: 'border-emerald-100 bg-emerald-50/80 text-emerald-700',
  info: 'border-brand-100 bg-brand-50/80 text-brand-800',
}

const iconColors: Record<AlertTone, string> = {
  error: 'text-red-500',
  success: 'text-emerald-500',
  info: 'text-brand-500',
}

export function Alert({
  tone = 'info',
  children,
  className,
}: {
  tone?: AlertTone
  children: ReactNode
  className?: string
}) {
  const Icon = tone === 'error' ? AlertCircle : tone === 'success' ? CheckCircle2 : Info
  return (
    <div
      role={tone === 'error' ? 'alert' : undefined}
      className={cn(
        'flex items-start gap-3 rounded-xl border px-4 py-3 text-sm',
        styles[tone],
        className,
      )}
    >
      <Icon className={cn('mt-0.5 h-4 w-4 shrink-0', iconColors[tone])} aria-hidden="true" />
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  )
}
