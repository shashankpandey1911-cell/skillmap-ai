import { cn } from '../../utils/cn'
import type { BadgeTone } from './Badge'

interface ProgressBarProps {
  /** 0-100 */
  value: number
  tone?: BadgeTone
  className?: string
  /** Show label */
  showLabel?: boolean
}

const gradients: Record<BadgeTone, string> = {
  brand: 'from-brand-400 to-brand-600',
  green: 'from-emerald-400 to-emerald-600',
  amber: 'from-amber-400 to-amber-600',
  red: 'from-red-400 to-red-600',
  slate: 'from-gray-300 to-gray-400',
  purple: 'from-purple-400 to-purple-600',
}

export function ProgressBar({ value, tone = 'brand', className, showLabel }: ProgressBarProps) {
  const clamped = Math.round(Math.max(0, Math.min(100, value)))
  return (
    <div className={cn('space-y-1', className)}>
      {showLabel && (
        <div className="flex justify-between text-xs">
          <span className="text-gray-500">Progress</span>
          <span className="font-medium text-gray-700">{clamped}%</span>
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        className="h-2 w-full overflow-hidden rounded-full bg-gray-100"
      >
        <div
          className={cn(
            'h-full rounded-full bg-gradient-to-r transition-all duration-500 ease-out',
            gradients[tone],
          )}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  )
}
